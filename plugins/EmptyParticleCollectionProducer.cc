#include "HLTrigger/DeepTauTraining/plugins/EmptyParticleCollectionProducer.h"

#include "DataFormats/PatCandidates/interface/Electron.h" // pat::Electron
#include "DataFormats/PatCandidates/interface/Muon.h"     // pat::Muon
#include "DataFormats/PatCandidates/interface/Tau.h"      // pat::Tau
#include "DataFormats/PatCandidates/interface/Jet.h"      // pat::Jet

typedef EmptyParticleCollectionProducer<pat::Electron> EmptyPATElectronCollectionProducer;
typedef EmptyParticleCollectionProducer<pat::Muon>     EmptyPATMuonCollectionProducer;
typedef EmptyParticleCollectionProducer<pat::Tau>      EmptyPATTauCollectionProducer;
typedef EmptyParticleCollectionProducer<pat::Jet>      EmptyPATJetCollectionProducer;

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(EmptyPATElectronCollectionProducer);
DEFINE_FWK_MODULE(EmptyPATMuonCollectionProducer);
DEFINE_FWK_MODULE(EmptyPATTauCollectionProducer);
DEFINE_FWK_MODULE(EmptyPATJetCollectionProducer);
