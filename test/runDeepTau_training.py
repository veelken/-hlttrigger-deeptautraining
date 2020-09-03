#!/usr/bin/env python

import getpass
import os
import subprocess
import time

from HLTrigger.DeepTauTraining.run_command import *

version_rawNtuples = "2020Sep01wHGCalFix"
version_training = "training_v1"

outputDir_scratch = os.path.join("/home", getpass.getuser(), "temp/Phase2HLT_DeepTauTraining", version_rawNtuples, version_training)
run_command('mkdir -p %s' % outputDir_scratch)

outputDir_root_to_hdf = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "training-hdf5")
run_command('mkdir -p %s' % outputDir_root_to_hdf)
run_command('mkdir -p %s/even-events-classified-by-DeepTau_even' % outputDir_root_to_hdf)
run_command('mkdir -p %s/even-events-classified-by-DeepTau_odd' % outputDir_root_to_hdf)
run_command('mkdir -p %s/even-events-classified-by-chargedIsoPtSum' % outputDir_root_to_hdf)
run_command('mkdir -p %s/odd-events-classified-by-DeepTau_even' % outputDir_root_to_hdf)
run_command('mkdir -p %s/odd-events-classified-by-DeepTau_odd' % outputDir_root_to_hdf)
run_command('mkdir -p %s/odd-events-classified-by-chargedIsoPtSum' % outputDir_root_to_hdf)

outputDir_models = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "models")
run_command('mkdir -p %s' % outputDir_models)

outputDir_plots = os.path.join("/home", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "plots")
run_command('mkdir -p %s' % outputDir_plots)

# CV: clean scratch directory
run_command('rm -rf %s/*' % outputDir_scratch)

#----------------------------------------------------------------------------------------------------
# CV: run actual DeepTau training
print("Compiling _fill_grid_setup.py script...")
run_command('source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/compile_fill_grid_setup.sh')
print(" Done.")

outputFiles_root_to_hdf = {}
models = {}
for part in [ "even", "odd" ]:
    print("Running DeepTau training for '%s' sample..." % part)
    outputFiles_root_to_hdf[part] = "%s_pt_20_eta_0.000.h5" % part
    models[part] = "DeepTauPhase2HLTv2%s" % part
    command = 'source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/Training_p6_Phase2HLT_wrapper.sh %s %s' % \
      (os.path.join(outputDir_root_to_hdf, "%s-events" % part, outputFiles_root_to_hdf[part]), models[part])
    run_command(command)
    run_command('cp $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2/%s_step1_final.h5 %s' % (models[part], outputDir_models))
    print(" Done.")
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: Convert DNN model to graph (.pb) format
for part in [ "even", "odd" ]:
    run_command('rm %s_step1_final.pb' % models[part])
    command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/deploy_model.py --input %s' % \
      (os.path.join(outputDir_models, "%s_step1_final.h5" % models[part]))
    run_command(command)
    run_command('mv %s_step1_final.pb $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2/' % models[part])
    run_command('cp $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2/%s_step1_final.pb %s' % (models[part], outputDir_models))
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: Split DeepTau model into three parts and convert DNN model to graph (.pb) format,
#     as needed by CMSSW implementation of DeepTau tau ID discriminator in RecoTauTag/RecoTau/plugins/DeepTauId.cc
for part in [ "even", "odd" ]:
    print("Splitting DeepTau model for '%s' sample into 'core', 'inner', and 'outer' graphs..." % part)
    command = 'source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/SplitNetwork_Phase2HLT_wrapper.sh %s %s' % \
      (os.path.join(outputDir_models, "%s_step1_final.h5" % models[part]), models[part])
    run_command(command)
    for graph in [ "inner", "outer", "core" ]: 
        run_command('cp $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2/%s_step1_final_%s.h5 %s' % (models[part], graph, outputDir_models))
        command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/deploy_model.py --input %s' % \
          (os.path.join(outputDir_models, "%s_step1_final_%s.h5" % (models[part], graph)))
        run_command(command)
        run_command('mv %s_step1_final_%s.pb $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2/' % (models[part], graph))
        run_command('cp $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2/%s_step1_final_%s.pb %s' % (models[part], graph, outputDir_models))
    print(" Done.")
#-------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: Classify tau candidates in events with even event numbers 
#     using DeepTau model trained on events with even event numbers and vice versa
outputDirs_root_to_hdf_classified = {}
for part_sample in [ "even", "odd" ]:
    for part_model in [ "even", "odd" ]:
        run_command('mkdir -p %s/testing-classified' % outputDir_scratch)
        command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/apply_training.py --input %s --output %s --model $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2/%s_step1_final.pb --chunk-size 1000 --batch-size 100 --max-queue-size 20' % \
          (os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample), os.path.join(outputDir_scratch, "testing-classified"), models[part_model])
        run_command(command)
        key = '%s-events-classified-by-DeepTau_%s' % (part_sample, part_model)
        outputDirs_root_to_hdf_classified[key] = os.path.join(outputDir_root_to_hdf, "%s-events-classified-by-DeepTau_%s" % (part_sample, part_model))
        move_all_files_to_hdfs(os.path.join(outputDir_scratch, "testing-classified"), outputDirs_root_to_hdf_classified[key])
        run_command('rm -rf %s/testing-classified' % outputDir_scratch)
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: Make plot of test vs train performance ROC curve
for part_sample in [ "even", "odd" ]:
    part_model_train = part_sample
    part_model_test = None
    if part_sample == "even":
        part_model_test = "odd"
    elif part_sample == "odd":
        part_model_test = "even"
    else:
        raise ValueError("Invalid parameter 'part_sample' = '%s' !!" % part_sample)
    key_train = '%s-events-classified-by-DeepTau_%s' % (part_sample, part_model_train)
    key_test = '%s-events-classified-by-DeepTau_%s' % (part_sample, part_model_test)
    command = 'python3 $CMSSW_BASE/src/TauMLTools/Training/python/evaluate_performance.py --input-taus %s --other-type jet --deep-results %s --deep-results-label "Train" --prev-deep-results %s --prev-deep-results-label "Test" --output %s/rocCurve_DeepTau_test_vs_train_%s.pdf --setup $CMSSW_BASE/src/TauMLTools/Training/python/plot_setups/overtraining.py' % \
      (os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample, outputFiles_root_to_hdf[part_sample]), 
       outputDirs_root_to_hdf_classified[key_train], 
       outputDirs_root_to_hdf_classified[key_test],
       outputDir_plots, part_sample)
    run_command(command)

# CV: Make plot of DeepTau vs chargedIsoPtSum performance ROC curve (for test sample)
for part_sample in [ "even", "odd" ]:
    part_model = None
    if part_sample == "even":
        part_model = "odd"
    elif part_sample == "odd":
        part_model = "even"
    else:
        raise ValueError("Invalid parameter 'part_sample' = '%s' !!" % part_sample)
    key_DeepTau = '%s-events-classified-by-DeepTau_%s' % (part_sample, part_model)
    command = 'python3 $CMSSW_BASE/src/TauMLTools/Training/python/evaluate_performance.py --input-taus %s --other-type jet --deep-results %s --output %s/rocCurve_DeepTau_vs_chargedIsoPtSum_%s.pdf --setup $CMSSW_BASE/src/TauMLTools/Training/python/plot_setups/phase2_hlt.py' % \
      (os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample, outputFiles_root_to_hdf[part_sample]), 
       outputDirs_root_to_hdf_classified[key_DeepTau], 
       outputDir_plots, part_sample)
    run_command(command)
#----------------------------------------------------------------------------------------------------
