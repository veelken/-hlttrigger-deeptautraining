import FWCore.ParameterSet.Config as cms

process = cms.Process("produceDeepTauRawNtupleDEBUG")

process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.Geometry.GeometryExtended2026D49Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:/home/veelken/Phase2HLT/CMSSW_11_1_0/src/HLTrigger/Phase2HLTPFTaus/test/step3_RAW2DIGI_RECO.root'
    ),
    ##eventsToProcess = cms.untracked.VEventRange(
    ##    '1:128:18039'
    ##) 
)

##inputFilePath = '/hdfs/cms/store/user/rdewanje/VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5/HLTConfig_VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5_wOfflineVtx_wDeepTau3/'
inputFilePath = None
inputFileNames = [ 'file:/hdfs/cms/store/user/rdewanje/VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5/HLTConfig_VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5_wOfflineVtx_wDeepTau4/200826_185528/0000/step3_RAW2DIGI_RECO_1.root' ]
processName = "qqH_htt"
hlt_srcVertices = 'offlinePrimaryVertices'
hlt_algorithm = "hps"
hlt_isolation_maxDeltaZOption = "primaryVertex"
hlt_isolation_minTrackHits = 8
outputFileName = "produceDeepTau_rawNtuple_DEBUG_%s.root" % processName

#--------------------------------------------------------------------------------
# set input files
if inputFilePath:
    from HLTrigger.TallinnHLTPFTauAnalyzer.tools.jobTools import getInputFileNames
    print("Searching for input files in path = '%s'" % inputFilePath)
    inputFileNames = getInputFileNames(inputFilePath)
    print("Found %i input files." % len(inputFileNames))
    process.source.fileNames = cms.untracked.vstring(inputFileNames)
else:
    print("Processing %i input files: %s" % (len(inputFileNames), inputFileNames))
    process.source.fileNames = cms.untracked.vstring(inputFileNames)
#--------------------------------------------------------------------------------

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic', '')

hlt_pfTauLabel = None
if hlt_algorithm == "shrinking-cone":
  hlt_pfTauLabel = "PFTau"
elif hlt_algorithm == "hps":
  hlt_pfTauLabel = "HpsPFTau"
else:
  raise ValueError("Invalid parameter hlt_algorithm = '%s' !!" % hlt_algorithm)

hlt_pfTauSuffix = "%iHits" % hlt_isolation_minTrackHits
if hlt_isolation_maxDeltaZOption == "primaryVertex":
  hlt_pfTauSuffix += "MaxDeltaZ"
elif hlt_isolation_maxDeltaZOption == "leadTrack":
  hlt_pfTauSuffix += "MaxDeltaZToLeadTrack"
else:
  raise ValueError("Invalid parameter hlt_isolation_maxDeltaZOption = '%s' !!" % hlt_isolation_maxDeltaZOption)
if hlt_srcVertices == "offlinePrimaryVertices":
  hlt_pfTauSuffix += "WithOfflineVertices"
elif hlt_srcVertices == "hltPhase2PixelVertices":
  hlt_pfTauSuffix += "WithOnlineVertices"
elif hlt_srcVertices == "hltPhase2TrimmedPixelVertices":
  hlt_pfTauSuffix += "WithOnlineVerticesTrimmed"
else:
  raise ValueError("Invalid parameter hlt_srcVertices = '%s' !!" % hlt_srcVertices)

hlt_srcPFTaus = 'hltSelected%ss%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)
print("Reading PFTaus@HLT from the collection '%s'." % hlt_srcPFTaus)

hlt_srcPFJets = 'hlt%sAK4PFJets%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)
print("Reading anti-kT (dR=0.4) PFJets@HLT from the collection '%s'." % hlt_srcPFJets)

##tauTupleProducer_requireGenMatch = True
tauTupleProducer_requireGenMatch = False

process.productionSequence = cms.Sequence()

# CV: produce genParticle collection
process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")
process.productionSequence += process.genParticles

process.load("PhysicsTools.JetMCAlgos.TauGenJets_cfi")
process.tauGenJets.GenParticles = cms.InputTag('genParticles')
process.productionSequence += process.tauGenJets

process.load("PhysicsTools.JetMCAlgos.TauGenJetsDecayModeSelectorAllHadrons_cfi")
process.productionSequence += process.tauGenJetsSelectorAllHadrons

process.selectedGenHadTaus = cms.EDFilter("GenJetSelector",
  src = cms.InputTag('tauGenJetsSelectorAllHadrons'),
  cut = cms.string('pt > 20. & abs(eta) < 2.4'),
  filter = cms.bool(False)
)
process.productionSequence += process.selectedGenHadTaus

# CV: produce pat::Jet collection
process.load("RecoJets.Configuration.GenJetParticles_cff")
process.productionSequence += process.genParticlesForJets

process.load("RecoJets.JetProducers.ak4GenJets_cfi")
process.productionSequence += process.ak4GenJets

process.load("RecoJets.JetProducers.fixedGridRhoProducer_cfi")
process.fixedGridRhoAll.pfCandidatesTag = cms.InputTag('particleFlowTmp')
process.productionSequence += process.fixedGridRhoAll

from PhysicsTools.PatAlgos.slimming.primaryVertexAssociation_cfi import primaryVertexAssociation
process.primaryVertexAssociation = primaryVertexAssociation.clone(
    particles = cms.InputTag('particleFlowTmp'),
    vertices = cms.InputTag(hlt_srcVertices),
    jets = cms.InputTag(hlt_srcPFJets)
)
process.productionSequence += process.primaryVertexAssociation

from PhysicsTools.PatAlgos.slimming.packedPFCandidates_cfi import packedPFCandidates
process.packedPFCandidates = packedPFCandidates.clone(
    inputCollection = cms.InputTag('particleFlowTmp'),
    inputVertices = cms.InputTag(hlt_srcVertices),
    originalVertices = cms.InputTag(hlt_srcVertices),
    originalTracks = cms.InputTag('generalTracks'),
    vertexAssociator = cms.InputTag('primaryVertexAssociation:original'),
    PuppiSrc = cms.InputTag(''),
    PuppiNoLepSrc = cms.InputTag(''),    
    chargedHadronIsolation = cms.InputTag(''),
    minPtForChargedHadronProperties = cms.double(0.9),
    secondaryVerticesForWhiteList = cms.VInputTag(),
    minPtForTrackProperties = cms.double(0.9)
)
process.productionSequence += process.packedPFCandidates

process.dummyIsolatedTracks = cms.EDProducer("EmptyPATIsolatedTrackCollectionProducer")
process.productionSequence += process.dummyIsolatedTracks

from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
addJetCollection(
    process,
    labelName = 'HLTAK4PF',
    jetSource = cms.InputTag(hlt_srcPFJets),
    btagDiscriminators = [ 'None' ],
    genJetCollection = cms.InputTag('ak4GenJets'), 
    jetCorrections = ( 'AK4PF', cms.vstring([ 'L2Relative', 'L3Absolute' ]), 'None' )
)
process.makePatJets = cms.Sequence(process.patAlgosToolsTask)
process.productionSequence += process.makePatJets

process.load("PhysicsTools.PatAlgos.slimming.slimmedJets_cfi")
process.slimmedJets.src = cms.InputTag('patJetsHLTAK4PF')
process.productionSequence += process.slimmedJets

# CV: produce pat::Tau collection
process.load("PhysicsTools.PatAlgos.producersLayer1.tauProducer_cff")
process.tauMatch.src = cms.InputTag(hlt_srcPFTaus)
process.tauGenJetMatch.src = cms.InputTag(hlt_srcPFTaus)
process.patTaus.tauSource = cms.InputTag(hlt_srcPFTaus)
process.patTaus.tauTransverseImpactParameterSource = cms.InputTag('hlt%sTransverseImpactParameters%s' % (hlt_pfTauLabel, hlt_pfTauSuffix))
process.patTaus.tauIDSources = cms.PSet()
from PhysicsTools.PatAlgos.producersLayer1.tauProducer_cfi import singleID, containerID
singleID(process.patTaus.tauIDSources, 'hlt%sDiscriminationByDecayModeFinding%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "decayModeFinding")
singleID(process.patTaus.tauIDSources, 'hlt%sDiscriminationByDecayModeFindingNewDMs%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "decayModeFindingNewDMs")
singleID(process.patTaus.tauIDSources, 'hltSelected%sChargedIsoPtSumHGCalFix%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "chargedIsoPtSumHGCalFix")
singleID(process.patTaus.tauIDSources, 'hltSelected%sNeutralIsoPtSumHGCalFix%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "neutralIsoPtSumHGCalFix")
singleID(process.patTaus.tauIDSources, 'hltSelected%sChargedIsoPtSumdR03HGCalFix%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "chargedIsoPtSumdR03HGCalFix")
singleID(process.patTaus.tauIDSources, 'hltSelected%sNeutralIsoPtSumdR03HGCalFix%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "neutralIsoPtSumdR03HGCalFix")
containerID(process.patTaus.tauIDSources, 'hlt%sBasicDiscriminators%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "IDdefinitions", [
    [ "chargedIsoPtSum", "ChargedIsoPtSum" ],
    [ "neutralIsoPtSum", "NeutralIsoPtSum" ],
    [ "puCorrPtSum", "PUcorrPtSum" ],
    [ "neutralIsoPtSumWeight", "NeutralIsoPtSumWeight" ],
    [ "footprintCorrection", "TauFootprintCorrection" ],
    [ "photonPtSumOutsideSignalCone", "PhotonPtSumOutsideSignalCone" ],
    [ "byCombinedIsolationDeltaBetaCorrRaw3Hits", "ByRawCombinedIsolationDBSumPtCorr3Hits" ]
])
containerID(process.patTaus.tauIDSources, 'hlt%sBasicDiscriminatorsdR03%s' % (hlt_pfTauLabel, hlt_pfTauSuffix), "IDdefinitions", [
    [ "chargedIsoPtSumdR03", "ChargedIsoPtSum" ],
    [ "neutralIsoPtSumdR03", "NeutralIsoPtSum" ],
    [ "puCorrPtSumdR03", "PUcorrPtSum" ],
    [ "neutralIsoPtSumWeightdR03", "NeutralIsoPtSumWeight" ],
    [ "footprintCorrectiondR03", "TauFootprintCorrection" ],
    [ "photonPtSumOutsideSignalConedR03", "PhotonPtSumOutsideSignalCone" ],
    [ "byCombinedIsolationDeltaBetaCorrRaw3HitsdR03", "ByRawCombinedIsolationDBSumPtCorr3Hits" ]
])
process.productionSequence += process.makePatTaus

process.selectedPatTaus = cms.EDProducer("MyPATTauSelector",
  src                 = cms.InputTag('patTaus'),
  min_pt              = cms.double(20.0),
  max_pt              = cms.double(-1.),
  min_absEta          = cms.double(-1.),
  max_absEta          = cms.double(2.4),
  decayModes          = cms.vint32(0, 1, 2, 10, 11),
  min_leadTrackPt     = cms.double(1.0),
  max_leadTrackPt     = cms.double(-1.),
  tauID_relChargedIso = cms.string("chargedIsoPtSum"),
  min_relChargedIso   = cms.double(-1.),
  max_relChargedIso   = cms.double(-1.),
  min_absChargedIso   = cms.double(-1.),
  max_absChargedIso   = cms.double(-1.),
  invert              = cms.bool(False)
)
process.productionSequence += process.selectedPatTaus

process.genMatchedPatTaus = cms.EDFilter("PATTauAntiOverlapSelector",
  src = cms.InputTag('selectedPatTaus'),
  srcNotToBeFiltered = cms.VInputTag('selectedGenHadTaus'),
  dRmin = cms.double(0.3),
  invert = cms.bool(True),
  filter = cms.bool(False)                                                          
)
process.productionSequence += process.genMatchedPatTaus

process.load("PhysicsTools.PatAlgos.slimming.slimmedTaus_cfi")
##process.slimmedTaus.src = cms.InputTag('patTaus')
process.slimmedTaus.src = cms.InputTag('genMatchedPatTaus')
process.productionSequence += process.slimmedTaus

##process.dumpPFTaus = cms.EDAnalyzer("DumpRecoPFTaus",
##  src = cms.InputTag(hlt_srcPFTaus),
##  src_sumChargedIso = cms.InputTag('hltSelected%sChargedIsoPtSum%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)),
##  src_discriminators = cms.VInputTag()
##)
##process.productionSequence += process.dumpPFTaus
##
##process.dumpPatTaus = cms.EDAnalyzer("DumpPATTaus",
##  src = cms.InputTag('slimmedTaus')
##)
##process.productionSequence += process.dumpPatTaus

##process.dumpPFCandidates = cms.EDAnalyzer("DumpRecoPFCandidates",
##  src = cms.InputTag('particleFlowTmp'),
##)
##process.productionSequence += process.dumpPFCandidates
##
##process.dumpPackedPFCandidates = cms.EDAnalyzer("DumpPackedCandidates",
##  src = cms.InputTag('packedPFCandidates'),
##)
##process.productionSequence += process.dumpPackedPFCandidates

# CV: fill DeepTau training Ntuple
process.dummyElectrons = cms.EDProducer("EmptyPATElectronCollectionProducer")
process.productionSequence += process.dummyElectrons 

process.dummyMuons = cms.EDProducer("EmptyPATMuonCollectionProducer")
process.productionSequence += process.dummyMuons

tauJetdR = 0.2
objectdR = 0.5

process.tauTupleProducer = cms.EDAnalyzer("TauTupleProducer",
    isMC                          = cms.bool(True),
    minJetPt                      = cms.double(10.0),
    maxJetEta                     = cms.double(3.0),
    forceTauJetMatch              = cms.bool(False),
    storeJetsWithoutTau           = cms.bool(False),
    tauJetMatchDeltaRThreshold    = cms.double(tauJetdR),
    objectMatchDeltaRThresholdTau = cms.double(objectdR),
    objectMatchDeltaRThresholdJet = cms.double(tauJetdR + objectdR),
    requireGenMatch               = cms.bool(tauTupleProducer_requireGenMatch),
    lheEventProduct               = cms.InputTag('externalLHEProducer'),
    genEvent                      = cms.InputTag('generator'),
    genParticles                  = cms.InputTag('genParticles'),
    puInfo                        = cms.InputTag('addPileupInfo'),
    vertices                      = cms.InputTag('offlinePrimaryVertices'),
    rho                           = cms.InputTag('fixedGridRhoAll'),
    electrons                     = cms.InputTag('dummyElectrons'),
    muons                         = cms.InputTag('dummyMuons'),
    taus                          = cms.InputTag('slimmedTaus'),
    jets                          = cms.InputTag('slimmedJets'),
    pfCandidates                  = cms.InputTag('packedPFCandidates'),
    tracks                        = cms.InputTag('dummyIsolatedTracks'),
)
process.productionSequence += process.tauTupleProducer

process.p = cms.Path(process.productionSequence)

process.TFileService = cms.Service('TFileService', 
    fileName = cms.string(outputFileName) 
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)
