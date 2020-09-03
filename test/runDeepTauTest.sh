
rm $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/deepTauTest_qqH_htt.root
rm runDeepTauTest.log ; cmsRun runDeepTauTest_cfg.py >& runDeepTauTest.log

rm $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/produceDeepTau_rawNtuple_DEBUG_qqH_htt.root
rm produceDeepTau_rawNtuple_DEBUG.log ; cmsRun produceDeepTau_rawNtuple_DEBUG_cfg.py >& produceDeepTau_rawNtuple_DEBUG.log

rm $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/tuple_DEBUG_qqH_htt.root
rm TrainingTupleProducer.log ; TrainingTupleProducer --input $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/produceDeepTau_rawNtuple_DEBUG_qqH_htt.root --output $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/tuple_DEBUG_qqH_htt.root >& TrainingTupleProducer.log

rm $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5/tuple_DEBUG_qqH_htt.h5
rm root_to_hdf.log; python $CMSSW_BASE/src/TauMLTools/Analysis/python/root_to_hdf.py --input $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/tuple_DEBUG_qqH_htt.root --output $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5/tuple_DEBUG_qqH_htt.h5 --trees taus,inner_cells,outer_cells >& root_to_hdf.log

rm /home/veelken/Phase2HLT_DeepTau/CMSSW_11_1_0/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5-classified/tuple_DEBUG_qqH_htt_pred.h5
rm apply_training.log ; python $CMSSW_BASE/src/TauMLTools/Training/python/apply_training.py --input $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5/ --output $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5-classified --model /hdfs/local/veelken/Phase2HLT/DeepTauTraining/2020Sep01wHGCalFix/training_v1/models/DeepTauPhase2HLTv2even_step1_final.pb --chunk-size 1000 --batch-size 1000 --max-queue-size 20 --debug true >& apply_training.log

rm validateDeepTau_CMSSW.log ; python $CMSSW_BASE/src/HLTrigger/DeepTauTraining/scripts/validateDeepTau_CMSSW.py >& validateDeepTau_CMSSW.log

#rm compareInputVariables.log ; python $CMSSW_BASE/src/HLTrigger/DeepTauTraining/scripts/compareInputVariables.py >& compareInputVariables.log
