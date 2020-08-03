#include "HLTrigger/DeepTauTraining/plugins/EmptyCollectionProducer.h"

#include "DataFormats/PatCandidates/interface/Electron.h"             // pat::Electron
#include "DataFormats/PatCandidates/interface/Muon.h"                 // pat::Muon
#include "DataFormats/PatCandidates/interface/Tau.h"                  // pat::Tau
#include "DataFormats/PatCandidates/interface/Jet.h"                  // pat::Jet
#include "DataFormats/PatCandidates/interface/IsolatedTrack.h"        // pat::IsolatedTrack
//#include "DataFormats/Candidate/interface/VertexCompositeCandidate.h" // reco::VertexCompositeCandidate
//#include "DataFormats/VertexReco/interface/Vertex.h"                  // reco::Vertex
//#include "DataFormats/JetReco/interface/CaloJet.h"                    // reco::CaloJet

typedef EmptyCollectionProducer<pat::Electron>                  EmptyPATElectronCollectionProducer;
typedef EmptyCollectionProducer<pat::Muon>                      EmptyPATMuonCollectionProducer;
typedef EmptyCollectionProducer<pat::Tau>                       EmptyPATTauCollectionProducer;
typedef EmptyCollectionProducer<pat::Jet>                       EmptyPATJetCollectionProducer;
typedef EmptyCollectionProducer<pat::IsolatedTrack>             EmptyPATIsolatedTrackCollectionProducer;
//typedef EmptyCollectionProducer<reco::VertexCompositeCandidate> EmptyVertexCompositeCandidateCollectionProducer;
//typedef EmptyCollectionProducer<reco::Vertex>                   EmptyVertexCollectionProducer;
//typedef EmptyCollectionProducer<reco::CaloJet>                  EmptyCaloJetCollectionProducer;

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(EmptyPATElectronCollectionProducer);
DEFINE_FWK_MODULE(EmptyPATMuonCollectionProducer);
DEFINE_FWK_MODULE(EmptyPATTauCollectionProducer);
DEFINE_FWK_MODULE(EmptyPATJetCollectionProducer);
DEFINE_FWK_MODULE(EmptyPATIsolatedTrackCollectionProducer);
//DEFINE_FWK_MODULE(EmptyVertexCompositeCandidateCollectionProducer);
//DEFINE_FWK_MODULE(EmptyVertexCollectionProducer);
//DEFINE_FWK_MODULE(EmptyCaloJetCollectionProducer);
