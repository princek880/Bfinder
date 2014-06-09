import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing
ivars = VarParsing.VarParsing('analysis')
#ivars.inputFiles='root://eoscms//eos/cms/store/user/twang/HIBmeson_20131220/test_20140106/JpsiKp/PyquenMix_embedHIJING_Bp2JpsiKp_5TeV_102_2_VpA.root'
#ivars.inputFiles='file:/afs/cern.ch/work/t/twang/MITHIG/GenHIBmeson_20131220/BoostGen5GeVB_20140214/subGENSIM_20140219/subBdKs/step4/HIJINGemb_BdJpsiKs_TuneZ2star_5TeV_cff_step4_RAW2DIGI_L1Reco_RECO_Bd_JpsiKs_mumu.root'
#ivars.inputFiles='file:/afs/cern.ch/work/t/twang/MITHIG/GenHIBmeson_20131220/BoostGen5GeVB_20140214/localRun/RunMore/PyquenMix_embedHIJING_Bp2JpsiKp_Bpt5_5TeV_boostedMC.root'
ivars.inputFiles='file:/net/hisrv0001/home/tawei/twang/Hijing_PPb502_MinimumBias/PyquenMix_STARTHI53_V27_HIJINGembed_pPb_step4_RAW2DIGI_L1Reco_RECO_Bpt5_BuJpsiK_20140225/5dc89fb1319c58a400229c5d020a3799/HIJINGemb_BuJpsiK_TuneZ2star_5TeV_cff_step4_RAW2DIGI_L1Reco_RECO_92_1_Yd0.root'
ivars.outputFile='Bfinder_all.root'
ivars.parseArguments()

### Run on MC?
runOnMC = True

### HI label?
HIFormat = True
#HIFormat = False

### Include SIM tracks for matching?
UseGenPlusSim = False

### Using pat muon with trigger or not
UsepatMuonsWithTrigger = True

process = cms.Process("demo")
process.load("FWCore.MessageService.MessageLogger_cfi")
### Set TransientTrackBuilder 
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
### Set Geometry/GlobalTag/BField
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
#process.load("Configuration.Geometry.GeometryIdeal_cff")
#process.load("Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff")

### keep only Pat:: part 
from PhysicsTools.PatAlgos.patEventContent_cff import *
### output module
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('test.root'),
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    outputCommands = cms.untracked.vstring('drop *',
    )
)

### Set maxEvents
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

### Set global tag
if runOnMC:
    #process.GlobalTag.globaltag = cms.string( 'START53_V7F::All' )  #Summer12_DR53X
    #process.GlobalTag.globaltag = cms.string( 'STARTHI53_V26::All' ) 
    #process.GlobalTag.globaltag = cms.string( 'START52_V5::All' ) 
    #process.GlobalTag.globaltag = cms.string( 'START52_V7::All' )
    #process.GlobalTag.globaltag = cms.string( 'START53_V17::All' )
    process.GlobalTag.globaltag = cms.string( 'START53_V27::All' )
else:
    #process.GlobalTag.globaltag = cms.string( 'FT_53_V6_AN2::All' ) #for 2012AB
    #process.GlobalTag.globaltag = cms.string( 'FT_53_V10_AN2::All' )#for 2012C
    #process.GlobalTag.globaltag = cms.string( 'FT_P_V42_AN2::All' ) #for 2012D
    process.GlobalTag.globaltag = cms.string( 'GR_P_V43F::All' ) ##/PAMuon/HIRun2013-28Sep2013-v1/RECO                                                                                                      
    #process.GlobalTag.globaltag = cms.string( 'GR_P_V43D::All' ) ##/PAMuon/HIRun2013-PromptReco-v1/RECO

### PoolSource will be ignored when running crab
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring(ivars.inputFiles)
)
#process.load("_eos_cms_store_user_twang_HIBmeson_20131220_test_20140106_JpsiKp_cff")

### Set basic filter
process.primaryVertexFilter = cms.EDFilter("GoodVertexFilter",
	#vertexCollection = cms.InputTag('offlinePrimaryVertices'),
	vertexCollection = cms.InputTag('offlinePrimaryVerticesWithBS'),
	minimumNDOF = cms.uint32(4) ,
	maxAbsZ = cms.double(24),	
	maxd0 = cms.double(2)	
)

process.noscraping = cms.EDFilter("FilterOutScraping",
    applyfilter = cms.untracked.bool(True),
	debugOn = cms.untracked.bool(False),
	numtrack = cms.untracked.uint32(10),
	thresh = cms.untracked.double(0.25)
)

#process.filter = cms.Sequence(process.primaryVertexFilter+process.noscraping)
process.filter = cms.Sequence(process.noscraping)

##Producing Gen list with SIM particles
process.genParticlePlusGEANT = cms.EDProducer("GenPlusSimParticleProducer",
        src           = cms.InputTag("g4SimHits"), # use "famosSimHits" for FAMOS
        setStatus     = cms.int32(8),             # set status = 8 for GEANT GPs
        filter        = cms.vstring("pt > 0.0"),  # just for testing (optional)
	    genParticles   = cms.InputTag("genParticles") # original genParticle list
)

### Setup Pat
### Ref: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATMCMatching
process.load("PhysicsTools.PatAlgos.patSequences_cff")
if HIFormat:
	process.muonMatch.matched = cms.InputTag("hiGenParticles")
	process.genParticlePlusGEANT.genParticles = cms.InputTag("hiGenParticles")

##Using GEN plus SIM list for matching
if UseGenPlusSim:
	process.muonMatch.matched = cms.InputTag("genParticlePlusGEANT")

#process.allLayer1Jets.addJetCorrFactors = False
from PhysicsTools.PatAlgos.tools.trackTools import *
#process.load( 'PhysicsTools.PatAlgos.mcMatchLayer0.muonMatch_cff' )
if runOnMC:
    makeTrackCandidates(process,              # patAODTrackCands
        label='TrackCands',                   # output collection will be 'allLayer0TrackCands', 'allLayer1TrackCands', 'selectedLayer1TrackCands'
        tracks=cms.InputTag('generalTracks'), # input track collection
    	particleType='pi+',                   # particle type (for assigning a mass)
        preselection='pt > 0.3',              # preselection cut on candidates. Only methods of 'reco::Candidate' are available
        selection='pt > 0.3',                 # Selection on PAT Layer 1 objects ('selectedLayer1TrackCands')
    	isolation={},                         # Isolations to use ('source':deltaR; set to {} for None)
       	isoDeposits=[],
        mcAs='muon'                           # Replicate MC match as the one used for Muons
    );                                        # you can specify more than one collection for this
    ### MC+mcAs+Match/pat_label options
    #process.patTrackCandsMCMatch.matched = cms.InputTag("hiGenParticles")
    process.patTrackCandsMCMatch.resolveByMatchQuality = cms.bool(True)
    process.patTrackCandsMCMatch.resolveAmbiguities = cms.bool(True)
    process.patTrackCandsMCMatch.checkCharge = cms.bool(True)
    process.patTrackCandsMCMatch.maxDPtRel = cms.double(0.5)
    process.patTrackCandsMCMatch.maxDeltaR = cms.double(0.7)
    process.patTrackCandsMCMatch.mcPdgId = cms.vint32(111, 211, 311, 321)
    process.patTrackCandsMCMatch.mcStatus = cms.vint32(1)
    l1cands = getattr(process, 'patTrackCands')
    l1cands.addGenMatch = True

else :
    makeTrackCandidates(process,              # patAODTrackCands
        label='TrackCands',                   # output collection will be 'allLayer0TrackCands', 'allLayer1TrackCands', 'selectedLayer1TrackCands'
        tracks=cms.InputTag('generalTracks'), # input track collection
        particleType='pi+',                   # particle type (for assigning a mass)
        preselection='pt > 0.3',              # preselection cut on candidates. Only methods of 'reco::Candidate' are available
        selection='pt > 0.3',                 # Selection on PAT Layer 1 objects ('selectedLayer1TrackCands')
        isolation={},                         # Isolations to use ('source':deltaR; set to {} for None)
        isoDeposits=[],
        mcAs=None                             # Replicate MC match as the one used for Muons
    );                                        # you can specify more than one collection for this
    l1cands = getattr(process, 'patTrackCands')
    l1cands.addGenMatch = False
from PhysicsTools.PatAlgos.tools.coreTools import *
removeAllPATObjectsBut(process, ['Muons'])
#removeSpecificPATObjects(process, ['Jets'])

if not runOnMC :
	removeMCMatching(process, ['All'] )

process.load("MuonAnalysis.MuonAssociators.patMuonsWithTrigger_cff")
from MuonAnalysis.MuonAssociators.patMuonsWithTrigger_cff import *
###Criterias from Hyunchul's 
process.muonL1Info.maxDeltaR = 0.3
process.muonL1Info.fallbackToME1 = True
process.muonMatchHLTL1.maxDeltaR = 0.3
process.muonMatchHLTL1.fallbackToME1 = True
process.muonMatchHLTL2.maxDeltaR = 0.3
process.muonMatchHLTL2.maxDPtRel = 10.0
process.muonMatchHLTL3.maxDeltaR = 0.1
process.muonMatchHLTL3.maxDPtRel = 10.0
process.muonMatchHLTCtfTrack.maxDeltaR = 0.1
process.muonMatchHLTCtfTrack.maxDPtRel = 10.0
process.muonMatchHLTTrackMu.maxDeltaR = 0.1
process.muonMatchHLTTrackMu.maxDPtRel = 10.0

### Set Bfinder option
process.demo = cms.EDAnalyzer('Bfinder',
	Bchannel 		= cms.vint32(
		1,#RECONSTRUCTION: J/psi + K
		1,#RECONSTRUCTION: J/psi + Pi
		1,#RECONSTRUCTION: J/psi + Ks 
		1,#RECONSTRUCTION: J/psi + K* (K+, Pi-)
		1,#RECONSTRUCTION: J/psi + K* (K-, Pi+)
		1,#RECONSTRUCTION: J/psi + phi
		1,),#RECONSTRUCTION: J/psi + pi pi <= psi', X(3872), Bs->J/psi f0
    MuonTriggerMatchingPath = cms.vstring("HLT_PAMu3_v1"),
    AppliedMuID     = cms.bool(False),
	HLTLabel        = cms.InputTag('TriggerResults::HLT'),
    GenLabel        = cms.InputTag('genParticles'),
	MuonLabel       = cms.InputTag('selectedPatMuons'),         #selectedPatMuons
	TrackLabel      = cms.InputTag('selectedPatTrackCands'),    #selectedPat
    PUInfoLabel     = cms.InputTag("addPileupInfo"),
    BSLabel     = cms.InputTag("offlineBeamSpot"),
    PVLabel     = cms.InputTag("offlinePrimaryVerticesWithBS")
)
if HIFormat:
	process.demo.GenLabel = cms.InputTag('hiGenParticles')

if UseGenPlusSim:
	process.demo.GenLabel = cms.InputTag('genParticlePlusGEANT')

if UsepatMuonsWithTrigger:
	process.demo.MuonLabel = cms.InputTag('patMuonsWithTrigger')	
	if runOnMC:
		addMCinfo(process)

### SetUp HLT info
process.load('Bfinder.HiHLTAlgos.hltanalysis_cff')
process.hltanalysis.dummyBranches = cms.untracked.vstring()
#if HIFormat:
	#process.hltanalysis.HLTProcessName = cms.string("HISIGNAL")
	#process.hltanalysis.hltresults = cms.InputTag("TriggerResults","","HISIGNAL")
	#process.hltanalysis.l1GtObjectMapRecord = cms.InputTag("hltL1GtObjectMap::HISIGNAL")
process.hltAna = cms.Path(process.filter*process.hltanalysis)

### Set output
process.TFileService = cms.Service("TFileService",
	fileName = cms.string(ivars.outputFile)
)

if runOnMC:
	process.patDefaultSequence *= process.genParticlePlusGEANT

if UsepatMuonsWithTrigger:
	process.patDefaultSequence *= process.patMuonsWithTriggerSequence

process.p = cms.Path(	
	process.filter*process.patDefaultSequence*process.demo
)

process.schedule = cms.Schedule(
	process.p
	,process.hltAna
)
