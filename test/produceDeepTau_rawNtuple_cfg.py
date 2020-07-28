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
    ##input = cms.untracked.int32(-1)
    input = cms.untracked.int32(1000)
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

srcPFTaus = 'hltSelected%ss%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)
##srcPFTaus = 'hlt%ss%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)
print("Reading PFTaus@HLT from the collection '%s'." % srcPFTaus)

#--------------------------------------------------------------------------------
# set input files
if inputFilePath:
    from HLTrigger.TallinnHLTPFTauAnalyzer.tools.jobTools import getInputFileNames
    print("Searching for input files in path = '%s'" % inputFilePath)
    inputFileNames = getInputFileNames(inputFilePath)
    print("Found %i input files." % len(inputFileNames))
    #process.source.fileNames = cms.untracked.vstring(inputFileNames)
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

process.dumpGenTaus = cms.EDAnalyzer("DumpGenTaus",
    src = cms.InputTag('tauGenJetsSelectorAllHadrons')
)
process.productionSequence += process.dumpGenTaus

moduleName_dumpSelectedHLTPFTaus = "dumpSelectedHLT%ss%s" % (hlt_pfTauLabel, hlt_pfTauSuffix)
module_dumpSelectedHLTPFTaus = cms.EDAnalyzer("DumpRecoPFTaus",
    src = cms.InputTag(srcPFTaus),
    ##src_sumChargedIso = cms.InputTag('hltSelected%sChargedIsoPtSum%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)),
    src_sumChargedIso = cms.InputTag('hlt%sChargedIsoPtSum%s' % (hlt_pfTauLabel, hlt_pfTauSuffix)),
    src_discriminators = cms.VInputTag()
)
setattr(process, moduleName_dumpSelectedHLTPFTaus, module_dumpSelectedHLTPFTaus)
process.productionSequence += module_dumpSelectedHLTPFTaus

# CV: produce pat::Jet collection
from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
process.hltAK4PFJets = ak4PFJets.clone(
    src = cms.InputTag('particleFlowTmp'),
    srcPVs = cms.InputTag('offlinePrimaryVertices')
)
process.productionSequence += process.hltAK4PFJets

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
    jets = cms.InputTag('hltAK4PFJets')
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

from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
addJetCollection(
    process,
    labelName = 'HLTAK4PF',
    jetSource = cms.InputTag('hltAK4PFJets'),
    btagDiscriminators = [ 'None' ],
    genJetCollection = cms.InputTag('ak4GenJets'), 
    jetCorrections = ( 'AK4PF', cms.vstring([ 'L2Relative', 'L3Absolute' ]), 'None' )
)
process.makePatJets = cms.Sequence(process.patAlgosToolsTask)
process.productionSequence += process.makePatJets

process.load("PhysicsTools.PatAlgos.slimming.slimmedJets_cfi")
process.slimmedJets.src = cms.InputTag('patJetsHLTAK4PF')
process.productionSequence += process.slimmedJets

# CV: produce additional tau ID discriminators
from RecoTauTag.RecoTau.PFRecoTauDiscriminationByHPSSelection_cfi import hpsSelectionDiscriminator, decayMode_1Prong0Pi0, decayMode_1Prong1Pi0, decayMode_1Prong2Pi0, decayMode_2Prong0Pi0, decayMode_2Prong1Pi0, decayMode_3Prong0Pi0, decayMode_3Prong1Pi0
process.hltPFTauDecayModeFinding = hpsSelectionDiscriminator.clone(
    PFTauProducer = cms.InputTag(srcPFTaus),
    decayModes = cms.VPSet(
        decayMode_1Prong0Pi0,
        decayMode_1Prong1Pi0,
        decayMode_1Prong2Pi0,
        decayMode_3Prong0Pi0
    ),
    requireTauChargedHadronsToBeChargedPFCands = cms.bool(True),
    minPixelHits = cms.int32(1),
    ##verbosity = cms.int32(1)
)
process.productionSequence += process.hltPFTauDecayModeFinding

process.hltPFTauDecayModeFindingNewDMs = hpsSelectionDiscriminator.clone(
    PFTauProducer = cms.InputTag(srcPFTaus),
    decayModes = cms.VPSet(
        decayMode_1Prong0Pi0,
        decayMode_1Prong1Pi0,
        decayMode_1Prong2Pi0,
        decayMode_2Prong0Pi0,
        decayMode_2Prong1Pi0,
        decayMode_3Prong0Pi0,
        decayMode_3Prong1Pi0
    ),
    requireTauChargedHadronsToBeChargedPFCands = cms.bool(True),
    minPixelHits = cms.int32(1),
    ##verbosity = cms.int32(1)
)
process.productionSequence += process.hltPFTauDecayModeFindingNewDMs

from RecoTauTag.RecoTau.PFRecoTauQualityCuts_cfi import PFTauQualityCuts
hltQualityCuts = PFTauQualityCuts.clone()
hltQualityCuts.signalQualityCuts.minTrackPt = cms.double(0.9)
hltQualityCuts.isolationQualityCuts.minTrackPt = cms.double(0.9)
hlt_isolation_maxDeltaZ            = None
hlt_isolation_maxDeltaZToLeadTrack = None
if hlt_isolation_maxDeltaZOption == "primaryVertex":
    hlt_isolation_maxDeltaZ            =  0.15 # value optimized for offline tau reconstruction at higher pileup expected during LHC Phase-2
    hlt_isolation_maxDeltaZToLeadTrack = -1.   # disabled
elif hlt_isolation_maxDeltaZOption == "leadTrack":
    hlt_isolation_maxDeltaZ            = -1.   # disabled
    hlt_isolation_maxDeltaZToLeadTrack =  0.15 # value optimized for offline tau reconstruction at higher pileup expected during LHC Phase-2
else:
    raise ValueError("Invalid parameter hlt_isolation_maxDeltaZOption = '%s' !!" % hlt_isolation_maxDeltaZOption)
hltQualityCuts.isolationQualityCuts.maxDeltaZ = cms.double(hlt_isolation_maxDeltaZ)
hltQualityCuts.isolationQualityCuts.maxDeltaZToLeadTrack = cms.double(hlt_isolation_maxDeltaZToLeadTrack)
hltQualityCuts.isolationQualityCuts.minTrackHits = cms.uint32(hlt_isolation_minTrackHits)
hltQualityCuts.primaryVertexSrc = cms.InputTag(hlt_srcVertices) 
#------------------------------------------------------------------------------------------------
# CV: fix for Phase-2 HLT tau trigger studies
#    (pT of PFCandidates within HGCal acceptance is significantly higher than track pT !!)
hltQualityCuts.leadingTrkOrPFCandOption = cms.string('minLeadTrackOrPFCand')
#------------------------------------------------------------------------------------------------

##requireDecayMode = cms.PSet(
##    BooleanOperator = cms.string("and"),
##    decayMode = cms.PSet(
##        Producer = cms.InputTag('hltPFTauDecayModeFindingNewDMs'),
##        cut = cms.double(0.5)
##    )
##)

from RecoTauTag.RecoTau.PFRecoTauDiscriminationByLeadingObjectPtCut_cfi import pfRecoTauDiscriminationByLeadingObjectPtCut
process.hltPFTauDiscriminationByTrackFinding = pfRecoTauDiscriminationByLeadingObjectPtCut.clone(
     PFTauProducer = cms.InputTag(srcPFTaus),
     UseOnlyChargedHadrons = cms.bool(True),
     MinPtLeadingObject = cms.double(0.0)
)
process.productionSequence += process.hltPFTauDiscriminationByTrackFinding

requireLeadTrack = cms.PSet(
    BooleanOperator = cms.string("and"),
    decayMode = cms.PSet(
        Producer = cms.InputTag('hltPFTauDiscriminationByTrackFinding'),
        cut = cms.double(0.5)
    )
)

from RecoTauTag.RecoTau.PFRecoTauDiscriminationByIsolation_cfi import pfRecoTauDiscriminationByIsolation
from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants
process.hltPFTauBasicDiscriminators = pfRecoTauDiscriminationByIsolation.clone(
    PFTauProducer = cms.InputTag(srcPFTaus),
    particleFlowSrc = cms.InputTag('particleFlowTmp'),
    vertexSrc = cms.InputTag(hlt_srcVertices),
    ##Prediscriminants = requireDecayMode,
    Prediscriminants = requireLeadTrack,
    deltaBetaPUTrackPtCutOverride     = True, # Set the boolean = True to override.
    deltaBetaPUTrackPtCutOverride_val = 0.5,  # Set the value for new value.
    customOuterCone = 0.5,
    isoConeSizeForDeltaBeta = 0.8,
    deltaBetaFactor = "0.20",
    qualityCuts = hltQualityCuts,
    IDdefinitions = cms.VPSet(
        cms.PSet(
            IDname = cms.string("ChargedIsoPtSum"),
            ApplyDiscriminationByTrackerIsolation = cms.bool(True),
            storeRawSumPt = cms.bool(True)
        ),
        cms.PSet(
            IDname = cms.string("NeutralIsoPtSum"),
            ApplyDiscriminationByECALIsolation = cms.bool(True),
            storeRawSumPt = cms.bool(True)
        ),
        cms.PSet(
            IDname = cms.string("NeutralIsoPtSumWeight"),
            ApplyDiscriminationByWeightedECALIsolation = cms.bool(True),
            storeRawSumPt = cms.bool(True),
            UseAllPFCandsForWeights = cms.bool(True)
        ),
        cms.PSet(
            IDname = cms.string("TauFootprintCorrection"),
            storeRawFootprintCorrection = cms.bool(True)
        ),
        cms.PSet(
            IDname = cms.string("PhotonPtSumOutsideSignalCone"),
            storeRawPhotonSumPt_outsideSignalCone = cms.bool(True)
        ),
        cms.PSet(
            IDname = cms.string("PUcorrPtSum"),
            applyDeltaBetaCorrection = cms.bool(True),
            storeRawPUsumPt = cms.bool(True)
        ),
        cms.PSet(
            IDname = cms.string("ByRawCombinedIsolationDBSumPtCorr3Hits"),
            ApplyDiscriminationByTrackerIsolation = cms.bool(True),
            ApplyDiscriminationByECALIsolation = cms.bool(True),
            applyDeltaBetaCorrection = cms.bool(True),
            storeRawSumPt = cms.bool(True)
        )
    )
)
process.productionSequence += process.hltPFTauBasicDiscriminators

# CV: reconstruct tau lifetime information
from RecoTauTag.RecoTau.PFTauPrimaryVertexProducer_cfi import PFTauPrimaryVertexProducer
process.hltPFTauPrimaryVertexProducer = PFTauPrimaryVertexProducer.clone(
    PFTauTag = cms.InputTag(srcPFTaus),
    ElectronTag = cms.InputTag(""),
    MuonTag = cms.InputTag(""),
    PVTag = cms.InputTag(hlt_srcVertices),
    beamSpot = cms.InputTag('offlineBeamSpot'),
    Algorithm = cms.int32(0),
    useBeamSpot = cms.bool(True),
    RemoveMuonTracks = cms.bool(False),
    RemoveElectronTracks = cms.bool(False),
    useSelectedTaus = cms.bool(False),
    discriminators = cms.VPSet(
        cms.PSet(
            discriminator = cms.InputTag('hltPFTauDecayModeFindingNewDMs'),
            selectionCut = cms.double(0.5)
        )
    ),
    cut = cms.string("pt > 18.0 & abs(eta) < 2.4")
)
process.productionSequence += process.hltPFTauPrimaryVertexProducer

from RecoTauTag.RecoTau.PFTauSecondaryVertexProducer_cfi import PFTauSecondaryVertexProducer
process.hltPFTauSecondaryVertexProducer = PFTauSecondaryVertexProducer.clone(
    PFTauTag = cms.InputTag(srcPFTaus)
)
process.productionSequence += process.hltPFTauSecondaryVertexProducer

from RecoTauTag.RecoTau.PFTauTransverseImpactParameters_cfi import PFTauTransverseImpactParameters
process.hltPFTauTransverseImpactParameters = PFTauTransverseImpactParameters.clone(
    PFTauTag = cms.InputTag(srcPFTaus),
    PFTauPVATag = cms.InputTag('hltPFTauPrimaryVertexProducer'),
    PFTauSVATag = cms.InputTag('hltPFTauSecondaryVertexProducer'),
    useFullCalculation = cms.bool(True)
)
process.productionSequence += process.hltPFTauTransverseImpactParameters

# CV: produce pat::Tau collection
process.load("PhysicsTools.PatAlgos.producersLayer1.tauProducer_cff")
process.tauMatch.src = cms.InputTag(srcPFTaus)
process.tauGenJetMatch.src = cms.InputTag(srcPFTaus)
process.patTaus.tauSource = cms.InputTag(srcPFTaus)
process.patTaus.tauTransverseImpactParameterSource = cms.InputTag('hltPFTauTransverseImpactParameters')
process.patTaus.tauIDSources = cms.PSet()
from PhysicsTools.PatAlgos.producersLayer1.tauProducer_cfi import singleID, containerID
singleID(process.patTaus.tauIDSources, "hltPFTauDecayModeFinding", "decayModeFinding")
singleID(process.patTaus.tauIDSources, "hltPFTauDecayModeFindingNewDMs", "decayModeFindingNewDMs")
containerID(process.patTaus.tauIDSources, "hltPFTauBasicDiscriminators", "IDdefinitions", [
    [ "chargedIsoPtSum", "ChargedIsoPtSum" ],
    [ "neutralIsoPtSum", "NeutralIsoPtSum" ],
    [ "puCorrPtSum", "PUcorrPtSum" ],
    [ "neutralIsoPtSumWeight", "NeutralIsoPtSumWeight" ],
    [ "footprintCorrection", "TauFootprintCorrection" ],
    [ "photonPtSumOutsideSignalCone", "PhotonPtSumOutsideSignalCone" ],
    [ "byCombinedIsolationDeltaBetaCorrRaw3Hits", "ByRawCombinedIsolationDBSumPtCorr3Hits" ]
])
process.productionSequence += process.makePatTaus

process.dumpPatTaus = cms.EDAnalyzer("DumpPATTaus",
    src = cms.InputTag('patTaus')
)
##process.productionSequence += process.dumpPatTaus

##process.load("PhysicsTools.PatAlgos.selectionLayer1.tauSelector_cfi")
##process.selectedPatTaus.cut = cms.string("pt > 20.0 & abs(eta) < 2.4 & tauID('decayModeFindingNewDMs') & leadChargedHadrCand.isNonnull() & leadChargedHadrCand.pt > 5.0")
##process.productionSequence += process.selectedPatTaus 

process.selectedPatTaus = cms.EDProducer("MyPATTauSelector",
    src                 = cms.InputTag('patTaus'),
    min_pt              = cms.double(20.0),
    max_pt              = cms.double(-1.),
    min_absEta          = cms.double(-1.),
    max_absEta          = cms.double(2.4),
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

process.dumpSelectedPatTaus = cms.EDAnalyzer("DumpPATTaus",
    src = cms.InputTag('selectedPatTaus')
)
process.productionSequence += process.dumpSelectedPatTaus

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
    requireGenMatch               = cms.bool(True),
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
    pfCandidates                  = cms.InputTag('packedPFCandidates')
)
process.productionSequence += process.tauTupleProducer

process.p = cms.Path(process.productionSequence)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

process.TFileService = cms.Service('TFileService', 
    fileName = cms.string(outputFileName) 
)

dump_file = open('dump.py','w')
dump_file.write(process.dumpPython())
