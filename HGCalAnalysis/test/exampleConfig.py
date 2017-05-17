import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

process = cms.Process("Demo")
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.Geometry.GeometryExtended2023D4Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_PostLS1_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('RecoLocalCalo.HGCalRecProducers.HGCalLocalRecoSequence_cff')

from FastSimulation.Event.ParticleFilter_cfi import *

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
   fileNames = cms.untracked.vstring(
#/RelValDoubleElectronPt15Eta17_27/CMSSW_9_1_0_pre3-91X_upgrade2023_realistic_v1_D13noSmear-v1/GEN-SIM-RECO
'root://xrootd-cms.infn.it//store/relval/CMSSW_9_1_0_pre3/RelValDoubleElectronPt15Eta17_27/GEN-SIM-RECO/91X_upgrade2023_realistic_v1_D13noSmear-v1/10000/0EDF6499-AF35-E711-8039-0CC47A7C3428.root',
'root://xrootd-cms.infn.it//store/relval/CMSSW_9_1_0_pre3/RelValDoubleElectronPt15Eta17_27/GEN-SIM-RECO/91X_upgrade2023_realistic_v1_D13noSmear-v1/10000/36ED744B-B235-E711-ADE1-0025905A6084.root',
'root://xrootd-cms.infn.it//store/relval/CMSSW_9_1_0_pre3/RelValDoubleElectronPt15Eta17_27/GEN-SIM-RECO/91X_upgrade2023_realistic_v1_D13noSmear-v1/10000/4436C35F-B235-E711-8F37-0025905A6090.root',
'root://xrootd-cms.infn.it//store/relval/CMSSW_9_1_0_pre3/RelValDoubleElectronPt15Eta17_27/GEN-SIM-RECO/91X_upgrade2023_realistic_v1_D13noSmear-v1/10000/5A6B4153-AF35-E711-A958-0CC47A745298.root',
'root://xrootd-cms.infn.it//store/relval/CMSSW_9_1_0_pre3/RelValDoubleElectronPt15Eta17_27/GEN-SIM-RECO/91X_upgrade2023_realistic_v1_D13noSmear-v1/10000/5CF20899-AF35-E711-A952-0025905A60BE.root',
'root://xrootd-cms.infn.it//store/relval/CMSSW_9_1_0_pre3/RelValDoubleElectronPt15Eta17_27/GEN-SIM-RECO/91X_upgrade2023_realistic_v1_D13noSmear-v1/10000/88C22846-AF35-E711-BC3D-0CC47A7C346E.root' 

    ),
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck")
)

process.ana = cms.EDAnalyzer('HGCalAnalysis',
                             detector = cms.string("all"),
                             rawRecHits = cms.bool(True),
                             readOfficialReco = cms.bool(True),
                             readCaloParticles = cms.bool(False),
                             layerClusterPtThreshold = cms.double(-1),  # All LayerCluster belonging to a multicluster are saved; this Pt threshold applied to the others
                             TestParticleFilter = ParticleFilterBlock.ParticleFilter
)

process.ana.TestParticleFilter.protonEMin = cms.double(100000)
process.ana.TestParticleFilter.etaMax = cms.double(3.1)

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("hgcalNtuple-pca-100.root")

                                   )

reRunClustering = True

if reRunClustering:
    process.hgcalLayerClusters.minClusters = cms.uint32(0)
    process.hgcalLayerClusters.realSpaceCone = cms.bool(True)
    process.hgcalLayerClusters.multiclusterRadius = cms.double(2.)  # in cm if realSpaceCone is true
    process.hgcalLayerClusters.dependSensor = cms.bool(True)
    process.hgcalLayerClusters.ecut = cms.double(3.)  # multiple of sigma noise if dependSensor is true
    process.hgcalLayerClusters.kappa = cms.double(9.)  # multiple of sigma noise if dependSensor is true
    #process.hgcalLayerClusters.deltac = cms.vdouble(2.,3.,5.) #specify delta c for each subdetector separately
    process.p = cms.Path(process.hgcalLayerClusters+process.ana)
else:
    process.p = cms.Path(process.ana)
