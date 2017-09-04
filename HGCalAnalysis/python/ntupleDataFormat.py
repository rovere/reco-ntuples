import math
import collections

import ROOT

class _Collection(object):
    """Adaptor class representing a collection of objects.
    Concrete collection classes should inherit from this class.
    """
    def __init__(self, tree, sizeBranch, objclass):
        """Constructor.
        Arguments:
        tree        -- TTree object
        sizeBranch  -- Name of the branch to be used in size()
        objclass    -- Class to be used for the objects in __getitem__()
        """
        super(_Collection, self).__init__()
        self._tree = tree
        self._sizeBranch = sizeBranch
        self._objclass = objclass

    def size(self):
        """Number of objects in the collection."""
        return int(getattr(self._tree, self._sizeBranch).size())

    def __len__(self):
        """Number of objects in the collection."""
        return self.size()

    def __getitem__(self, index):
        """Get object 'index' in the collection."""
        return self._objclass(self._tree, index)

    def __iter__(self):
        """Returns generator for the objects."""
        for index in xrange(self.size()):
            yield self._objclass(self._tree, index)


class _Object(object):
    """Adaptor class representing a single object in a collection.
    The member variables of the object are obtained from the branches
    with common prefix and a given index.
    Concrete object classes should inherit from this class.
    """
    def __init__(self, tree, index, prefix):
        """Constructor.
        Arguments:
        tree   -- TTree object
        index  -- Index for this object
        prefix -- Prefix of the branchs
        """
        super(_Object, self).__init__()
        self._tree = tree
        self._index = index
        self._prefix = prefix

    def __getattr__(self, attr):
        """Return object member variable.
        'attr' is translated as a branch in the TTree (<prefix>_<attr>).
        """
        self._checkIsValid()
        val = getattr(self._tree, self._prefix+"_"+attr)[self._index]
        return lambda: val

    def _checkIsValid(self):
        """Raise an exception if the object index is not valid."""
        if not self.isValid():
            raise Exception("%s is not valid" % self.__class__.__name__)

    def isValid(self):
        """Check if object index is valid."""
        return self._index != -1

    def index(self):
        """Return object index."""
        return self._index

##########
class HGCALNtuple(object):
    """Class abstracting the whole ntuple/TTree.
    Main benefit is to provide nice interface for
    - iterating over events
    - querying whether hit/seed information exists
    Note that to iteratate over the evets with zip(), you should use
    itertools.izip() instead.
    """
    def __init__(self, fileName, tree="ana/hgc"):
        """Constructor.
        Arguments:
        fileName -- String for path to the ROOT file
        tree     -- Name of the TTree object inside the ROOT file (default: 'trackingNtuple/tree')
        """
        super(HGCALNtuple, self).__init__()
        self._file = ROOT.TFile.Open(fileName)
        self._tree = self._file.Get(tree)
        self._entries = self._tree.GetEntriesFast()

    def file(self):
        return self._file

    def tree(self):
        return self._tree

    def nevents(self):
        return self._entries

    def hasHits(self):
        """Returns true if the ntuple has hit information."""
        return hasattr(self._tree, "rechit_x")

    def __iter__(self):
        """Returns generator for iterating over TTree entries (events)

        Generator returns Event objects.
        """
        for jentry in xrange(self._entries):
            # get the next tree in the chain and verify
            ientry = self._tree.LoadTree( jentry )
            if ientry < 0: break
            # copy next entry into memory and verify
            nb = self._tree.GetEntry( jentry )
            if nb <= 0: continue

            yield Event(self._tree, jentry)

    def getEvent(self, index):
        """Returns Event for a given index"""
        ientry = self._tree.LoadTree(index)
        if ientry < 0: return None
        nb = self._tree.GetEntry(ientry) # ientry or jentry?
        if nb <= 0: None

        return Event(self._tree, ientry) # ientry of jentry?


##########
class Event(object):
    """Class abstracting a single event.
    Main benefit is to provide nice interface to get various objects
    or collections of objects.
    """
    def __init__(self, tree, entry):
        """Constructor.
        Arguments:
        tree  -- TTree object
        entry -- Entry number in the tree
        """
        super(Event, self).__init__()
        self._tree = tree
        self._entry = entry

    def entry(self):
        return self._entry

    def event(self):
        """Returns event number."""
        return self._tree.event

    def lumi(self):
        """Returns lumisection number."""
        return self._tree.lumi

    def run(self):
        """Returns run number."""
        return self._tree.run

    def eventId(self):
        """Returns (run, lumi, event) tuple."""
        return (self._tree.run, self._tree.lumi, self._tree.event)

    def eventIdStr(self):
        """Returns 'run:lumi:event' string."""
        return "%d:%d:%d" % self.eventId()

    def tracks(self):
        """Returns Tracks object."""
        return Tracks(self._tree)

    def trackingParticles(self):
        """Returns TrackingParticles object."""
        return TrackingParticles(self._tree)

    def vertices(self):
        """Returns Vertices object."""
        return Vertices(self._tree)

    def trackingVertices(self):
        """Returns TrackingVertices object."""
        return TrackingVertices(self._tree)

    def genParticles(self):
        """Returns GenParticles object."""
        return GenParticles(self._tree)

    def caloParticles(self):
        """Returns a CaloParticle object."""
        return CaloParticle(self._tree)

    def multiClusters(self):
        """Returns a MultiCluster object."""
        return MultiClusters(self._tree)

    def layerClusters(self):
        """Returns a LayerCluster object."""
        return LayerClusters(self._tree)

    def pfclustersFromMultiCl(self):
        """Returns the collection of PFClusters
           created from the HGCAL MultiClusters"""
        return PFClustersFromMultiCl(self._tree)

    def recHits(self):
        """Returns a RecHit object."""
        return RecHits(self._tree)

    def electrons(self):
        """Returns an Electron object."""
        return Electrons(self._tree)

##########
class Track(_Object):
    """Class presenting a track."""
    def __init__(self, tree, index):
        """Constructor.
        Arguments:
        tree  -- TTree object
        index -- Index of the track
        """
        super(Track, self).__init__(tree, index, "track")

class Tracks(_Collection):
    """Class presenting a collection of tracks."""
    def __init__(self, tree):
        """Constructor.
        Arguments:
        tree -- TTree object
        """
        super(Tracks, self).__init__(tree, "track_pt", Track)

##########
class GenParticle(_Object):
    """Class representing a GenParticle"""
    def __init__(self, tree, index):
        super(GenParticle, self).__init__(tree, index, "genpart")

class GenParticles(_Collection):
    """Class presenting a collection of genparticles."""
    def __init__(self, tree):
        super(GenParticles, self).__init__(tree, "genpart_pt", GenParticle)

##########
class CaloParticle(_Object):
    """Class representing a caloParticle"""
    def __init__(self, tree):
        super(CaloParticle, self).__init__(tree, index, "calopart")

class CaloParticles(_Collection):
    """Class representing a collection of caloParticle."""
    def __init__(self, tree):
        super(CaloParticles, self).__init__(tree, "calopart_pt", CaloParticle)

##########
class MultiCluster(_Object):
    """Class representing an HGCAL MultiCluster."""
    def __init__(self, tree, index):
        super(MultiCluster, self).__init__(tree, index, "multiclus")

    def layerClusters(self):
        """Yields each LayerCluster within the current MultiCluster."""
        for layer_cluster_index in self.cluster2d():
            yield LayerCluster(self._tree, layer_cluster_index)

class MultiClusters(_Collection):
    """Class representing a collection of HGCAL MultiCluster."""
    def __init__(self, tree):
        super(MultiClusters, self).__init__(tree, "multiclus_pt", MultiCluster)

##########
class LayerCluster(_Object):
    """Class representing an HGCAL Layer Cluster."""
    def __init__(self, tree, index):
        super(LayerCluster, self).__init__(tree, index, "cluster2d")

    def rechits(self):
        """Yields each RecHit within the current LayerCluster."""
        for rechit_index in self.rechits():
            yield RecHit(self._tree, rechit_index)

class LayerClusters(_Collection):
    """Class representing a collection of HGCAL Layer Cluster."""
    def __init__(self, tree):
        super(LayerClusters, self).__init__(tree, "cluster2d_pt", LayerCluster)

##########
class RecHit(_Object):
    """Class representing an HGCAL RecHit."""
    def __init__(self, tree, index):
        super(RecHit, self).__init__(tree, index, "rechit")

class RecHits(_Collection):
    """Class representing a collection of HGCAL RecHit."""
    def __init__(self, tree):
        super(RecHits, self).__init__(tree, "rechit_pt", RecHit)

##########
class Electron(_Object):
    """Class representing an Ecal Driven Gsf Electron."""
    def __init__(self, tree, index):
        super(Electron, self).__init__(tree, index, "ecalDrivenGsfele")

    def clustersFromMultiCl(self):
        """Loop over all PFClusters associated to the SC and yield them"""
        for pfclusterIdx in self.pfClusterIndex():
            yield PFClusterFromMultiCl(self._tree, pfclusterIdx)

class Electrons(_Collection):
    """Class representing a collection of Ecal Driven Gsf Electrons."""
    def __init__(self, tree):
        super(Electrons, self).__init__(tree, "ecalDrivenGsfele_pt", Electron)

##########
class PFCluster(_Object):
    """Class representing a PFCluster."""

    def __init__(self, tree, index, prefix):
        """Constructor.
        Arguments:
        tree    -- TTree object
        index   -- Index of the PFCluster
        prefix -- TBranch prefix
        """
        super(PFCluster, self).__init__(tree, index, prefix)

class PFClusterFromMultiCl(PFCluster):
    """Class representing a PFClusterFromMultiCl"""
    def __init__(self, tree, index):
        super(PFClusterFromMultiCl, self).__init__(tree, index, "pfclusterFromMultiCl")

    def hits(self):
        """Loop over all RecHits associated to the PFCluster and yield them"""
        for rechitIdx in self.rechits():
            yield RecHit(self._tree, rechitIdx)
    def __repr__(self):
        return "PFClusterFromMultiCl position: ({x}, {y}, {z}) eta: {eta}, phi: {phi}, energy: {energy}".format(
                x=self.pos().x(), y=self.pos().y(), z=self.pos().z(),
                eta=self.eta(), phi=self.phi(),
                energy=self.energy())

class PFClusters(_Collection):
    """Class presenting a collection of PFClusters."""

    def __init__(self, tree, prefix):
        """Constructor.
        Arguments:
        tree -- TTree object
        prefix -- TBranch prefix
        """
        super(PFClusters, self).__init__(tree, prefix + "_pt", PFCluster, prefix)

class PFClustersFromMultiCl(_Collection):
    """Class presenting a collection of PFClustersFromMiltiCl."""

    def __init__(self, tree):
        super(PFClustersFromMultiCl, self).__init__(tree, "pfclusterFromMultiCl_pt", PFClusterFromMultiCl)

