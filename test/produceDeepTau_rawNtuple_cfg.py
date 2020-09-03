import FWCore.ParameterSet.Config as cms

process = cms.Process("produceDeepTauRawNtuple")

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
    )
)

inputFilePath = '/hdfs/cms/store/user/rdewanje/VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5/HLTConfig_VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5_wOfflineVtx_wL1_2FM/'
processName = "qqH_htt"
hlt_srcVertices = 'offlinePrimaryVertices'
hlt_algorithm = "hps" 
hlt_isolation_maxDeltaZOption = "primaryVertex"
hlt_isolation_minTrackHits = 8
outputFileName = "produceDeepTau_rawNtuple_%s_DEBUG.root" % processName

##inputFilePath = None
##inputFileNames = $inputFileNames
##processName = "$processName"
##hlt_srcVertices = '$hlt_srcVertices'
##hlt_algorithm = "$hlt_algorithm" 
##hlt_isolation_maxDeltaZOption = "$hlt_isolation_maxDeltaZOption"
##hlt_isolation_minTrackHits = $hlt_isolation_minTrackHits
##outputFileName = "$outputFileName"

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

tauTupleProducer_requireGenMatch = None
if processName == "qqH_htt":
    tauTupleProducer_requireGenMatch = True
    print("Running 'TauTupleProducer' module with gen-matching enabled.")
elif processName in [ "minbias", "qcd_pt30to50", "qcd_pt50to80", "qcd_pt80to120", "qcd_pt120to170", "qcd_pt170to300", "qcd_ptGt300", "dy_mass10to50", "dy_massGt50", "w" ]:
    tauTupleProducer_requireGenMatch = False
    print("Running 'TauTupleProducer' module with gen-matching disabled.")
else:
    raise ValueError("Invalid parameter processName = '%s' !!" % processName)

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

process.productionSequence = cms.Sequence()

# CV: produce genParticle collection
process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")
process.productionSequence += process.genParticles

process.load("PhysicsTools.JetMCAlgos.TauGenJets_cfi")
process.tauGenJets.GenParticles = cms.InputTag('genParticles')
process.productionSequence += process.tauGenJets

process.load("PhysicsTools.JetMCAlgos.TauGenJetsDecayModeSelectorAllHadrons_cfi")
process.productionSequence += process.tauGenJetsSelectorAllHadrons

##process.dumpGenTaus = cms.EDAnalyzer("DumpGenTaus",
##    src = cms.InputTag('tauGenJetsSelectorAllHadrons')
##)
##process.productionSequence += process.dumpGenTaus

##moduleName_dumpSelectedHLTPFTaus = "dumpSelectedHLT%ss%s" % (hlt_pfTauLabel, hlt_pfTauSuffix)
##module_dumpSelectedHLTPFTaus = cms.EDAnalyzer("DumpRecoPFTaus",
##    src = cms.InputTag(hlt_srcPFTaus),
##    src_sumChargedIso = cms.InputTag('hltSelected%sChargedIsoPtSum%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)),
##    src_discriminators = cms.VInputTag()
##)
##setattr(process, moduleName_dumpSelectedHLTPFTaus, module_dumpSelectedHLTPFTaus)
##process.productionSequence += module_dumpSelectedHLTPFTaus

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

##process.dumpPatTaus = cms.EDAnalyzer("DumpPATTaus",
##    src = cms.InputTag('patTaus')
##)
##process.productionSequence += process.dumpPatTaus

process.selectedPatTaus = cms.EDProducer("MyPATTauSelector",
    src                 = cms.InputTag('patTaus'),
    min_pt              = cms.double(20.0),
    max_pt              = cms.double(-1.),
    min_absEta          = cms.double(-1.),
    max_absEta          = cms.double(2.4),
    decayModes          = cms.vint32(0, 1, 2, 10, 11),
    min_leadTrackPt     = cms.double(5.0),
    max_leadTrackPt     = cms.double(-1.),
    tauID_relChargedIso = cms.string("chargedIsoPtSum"),
    min_relChargedIso   = cms.double(-1.),
    max_relChargedIso   = cms.double(-1.),
    min_absChargedIso   = cms.double(-1.),
    max_absChargedIso   = cms.double(-1.),
    invert              = cms.bool(False)
)
process.productionSequence += process.selectedPatTaus

process.load("PhysicsTools.PatAlgos.slimming.slimmedTaus_cfi")
process.productionSequence += process.slimmedTaus

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

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

process.TFileService = cms.Service('TFileService', 
    fileName = cms.string(outputFileName) 
)

##dump_file = open('dump.py','w')
##dump_file.write(process.dumpPython())
