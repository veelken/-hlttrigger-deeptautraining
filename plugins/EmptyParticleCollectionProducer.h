#ifndef HLTrigger_DeepTauTraining_EmptyParticleCollectionProducer_h
#define HLTrigger_DeepTauTraining_EmptyParticleCollectionProducer_h

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/Common/interface/Handle.h"

template <class T, class TCollection = std::vector<T>>
class EmptyParticleCollectionProducer : public edm::global::EDProducer<>
{
 public:
  explicit EmptyParticleCollectionProducer(const edm::ParameterSet& cfg)
  {
    produces<TCollection>();
  }
  ~EmptyParticleCollectionProducer() override
  {}

  void produce(edm::StreamID, edm::Event& evt, const edm::EventSetup& es) const 
  {
    std::unique_ptr<TCollection> particles(new TCollection());
    evt.put(std::move(particles));
  }
};

#endif
