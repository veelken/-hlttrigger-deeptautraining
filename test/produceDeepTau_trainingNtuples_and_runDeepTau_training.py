#!/usr/bin/env python

import getpass
import os
import subprocess
import time

version_rawNtuples = "2020Aug05"
version_training = "training_v2"

inputDir = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, "raw-tuples")

inputDir_sample = {
  'qqH_htt' : os.path.join(inputDir, "qqH_htt"),
  'minbias' : os.path.join(inputDir, "minbias"),
}

def run_command(command):
    print("executing command = '%s'" % command)
    os.system(command)

def move_file_to_hdfs(outputFile, outputDir_scratch, outputDir_hdfs):
    run_command('cp %s %s' % (os.path.join(outputDir_scratch, outputFile), os.path.join(outputDir_hdfs, outputFile)))
    # CV: sleep for 20 seconds in order to wait for copy command to /hdfs to finish
    #     before deleting file from scratch directory
    delay = 20
    print("Sleeping for %i seconds." % delay)
    time.sleep(delay)
    print(" Done.")
    run_command('rm -f %s' % os.path.join(outputDir_scratch, outputFile))

def move_all_files_to_hdfs(outputDir_scratch, outputDir_hdfs):
    run_command('cp %s/* %s' % (outputDir_scratch, outputDir_hdfs))
    # CV: sleep for 20 seconds per file copied in order to wait for copy command to /hdfs to finish
    #     before deleting file from scratch directory
    num_files = len([ file for file in os.listdir(outputDir_scratch) if os.path.isfile(os.path.join(outputDir_scratch, file)) ])
    delay = min(300, 20*num_files)
    print("Sleeping for %i seconds." % delay)
    time.sleep(delay)
    print(" Done.")
    run_command('rm -f %s/*' % outputDir_scratch)

def run_command_and_copy_output_to_hdfs(command, outputFile, outputDir_scratch, outputDir_hdfs):
    run_command(command % os.path.join(outputDir_scratch, outputFile))
    move_file_to_hdfs(outputFile, outputDir_scratch, outputDir_hdfs)

##print("Checking if xxhash package is already installed...")
##packages = subprocess.check_output([ 'pip', 'list' ])
##has_xxhash = False
##for package in packages.splitlines():
##    if package.find("xxhash") != -1: 
##        has_xxhash = True
##if has_xxhash:
##    print(" xxhash package already installed.")
##else:
##    print(" xxhash package not yet installed.")
##    print("Installing xxhash package...")
##    run_command('pip install xxhash --user')
##    print(" Done.")

outputDir_scratch = os.path.join("/home", getpass.getuser(), "temp/Phase2HLT_DeepTauTraining", version_rawNtuples, version_training)
run_command('mkdir -p %s' % outputDir_scratch)

executable_CreateBinnedTuples = 'CreateBinnedTuples'
outputDir_CreateBinnedTuples = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "training-preparation/CreateBinnedTuples")
run_command('mkdir -p %s' % outputDir_CreateBinnedTuples)
for sample in [ "qqH_htt", "minbias" ]:
    run_command('mkdir -p %s' % os.path.join(outputDir_CreateBinnedTuples, sample))

outputFile_size_list = "size_list.txt"
outputDir_size_list = outputDir_CreateBinnedTuples

outputDir_ShuffleMerge = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "training-preparation/ShuffleMerge")
run_command('mkdir -p %s' % outputDir_ShuffleMerge)
run_command('mkdir -p %s/all' % outputDir_ShuffleMerge)

outputDir_TrainingTupleProducer = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "training-root")
run_command('mkdir -p %s' % outputDir_TrainingTupleProducer)
run_command('mkdir -p %s/even-events' % outputDir_TrainingTupleProducer)
run_command('mkdir -p %s/odd-events' % outputDir_TrainingTupleProducer)

outputDir_root_to_hdf = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "training-hdf5")
run_command('mkdir -p %s' % outputDir_root_to_hdf)
run_command('mkdir -p %s/even-events' % outputDir_root_to_hdf)
run_command('mkdir -p %s/odd-events' % outputDir_root_to_hdf)
run_command('mkdir -p %s/even-events-classified-by-DeepTau_even' % outputDir_root_to_hdf)
run_command('mkdir -p %s/even-events-classified-by-DeepTau_odd' % outputDir_root_to_hdf)
run_command('mkdir -p %s/even-events-classified-by-chargedIsoPtSum' % outputDir_root_to_hdf)
run_command('mkdir -p %s/odd-events-classified-by-DeepTau_even' % outputDir_root_to_hdf)
run_command('mkdir -p %s/odd-events-classified-by-DeepTau_odd' % outputDir_root_to_hdf)
run_command('mkdir -p %s/odd-events-classified-by-chargedIsoPtSum' % outputDir_root_to_hdf)

outputDir_plots = os.path.join("/home", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "plots")
run_command('mkdir -p %s' % outputDir_plots)

regexp_sample = {
  'qqH_htt' : "[a-zA-Z0-9_/:.-]*produceDeepTau_rawNtuple_[a-zA-Z0-9_/:.-]+.root",
  'minbias' : "[a-zA-Z0-9_/:.-]*produceDeepTau_rawNtuple_[a-zA-Z0-9_/:.-]+.root",
}

binning_pt  = "20, 25, 30, 35, 40, 50, 60, 80, 120, 1000"
binning_eta = "0., 0.575, 1.15, 1.725, 2.3"

# CV: clean scratch directory
run_command('rm -rf %s/*' % outputDir_scratch)

#----------------------------------------------------------------------------------------------------
# CV: produce ROOT files for each tau type (tau_h, e, mu, jet), pT, and eta bin
for sample in [ "qqH_htt", "minbias" ]:
    ##run_command('mkdir -p %s' % os.path.join(outputDir_scratch, sample))
    command = '%s --output %s --input-dir %s --n-threads 12 --pt-bins "%s" --eta-bins "%s" --file-name-pattern "%s"' % \
      (executable_CreateBinnedTuples, os.path.join(outputDir_scratch, sample), inputDir_sample[sample], binning_pt, binning_eta, regexp_sample[sample])
    ##run_command(command)
    ##run_command('mkdir -p %s' % os.path.join(outputDir_CreateBinnedTuples, sample))
    ##move_all_files_to_hdfs(os.path.join(outputDir_scratch, sample), os.path.join(outputDir_CreateBinnedTuples, sample))

# CV: count number of entries in each ROOT file
outputFile_size_list = "size_list.txt"
##run_command('rm -f %s' % os.path.join(outputDir_CreateBinnedTuples, outputFile_size_list))
command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/CreateTupleSizeList.py --input %s >& %s' % \
  (outputDir_CreateBinnedTuples, "%s")
##run_command_and_copy_output_to_hdfs(command, outputFile_size_list, outputDir_scratch, outputDir_CreateBinnedTuples)
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: randomly sample tau candidates of different type, pT, and eta to produce "big training tuple"
for type in [ "tau", "e", "mu", "jet" ]:
    outputFile_ShuffleMerge = "%s_pt_20_eta_0.000.root" % type
    command = 'ShuffleMerge --cfg $CMSSW_BASE/src/TauMLTools/Analysis/config/training_inputs_%s_Phase2HLT.cfg --input %s --output %s --pt-bins "%s" --eta-bins "%s" --mode MergeAll --calc-weights true --ensure-uniformity true --max-bin-occupancy 500000 --n-threads 12  --disabled-branches "trainingWeight"' % \
      (type, outputDir_CreateBinnedTuples, "%s", binning_pt, binning_eta)
    ##run_command_and_copy_output_to_hdfs(command, outputFile_ShuffleMerge, outputDir_scratch, os.path.join(outputDir_ShuffleMerge, "all"))

# CV: count number of entries in each ROOT file again
outputFile_size_list = "size_list.txt"
##run_command('rm -f %s' % os.path.join(outputDir_ShuffleMerge, outputFile_size_list))
command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/CreateTupleSizeList.py --input %s >& %s' % \
  (outputDir_ShuffleMerge, "%s")
##run_command_and_copy_output_to_hdfs(command, outputFile_size_list, outputDir_scratch, outputDir_ShuffleMerge)

outputFile_ShuffleMerge = "all_pt_20_eta_0.000.root"
command = 'ShuffleMerge --cfg $CMSSW_BASE/src/TauMLTools/Analysis/config/training_inputs_step2_Phase2HLT.cfg --input %s --output %s --pt-bins "20, 1000" --eta-bins "0., 2.3" --mode MergeAll --calc-weights false --ensure-uniformity true --max-bin-occupancy 500000 --n-threads 12' % \
  (outputDir_ShuffleMerge, "%s")
##run_command_and_copy_output_to_hdfs(command, outputFile_ShuffleMerge, outputDir_scratch, outputDir_ShuffleMerge)
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: produce flat "TrainingTuples", 
#     separately for events with even and those with odd event numbers
outputFiles_TrainingTupleProducer = {}
for part in [ "even", "odd" ]:
    parity = None
    if part == "even":
        parity = 0
    elif part == "odd":
        parity = 1
    else:
        raise ValueError("Invalid parameter 'part' = '%s' !!" % part)
    outputFiles_TrainingTupleProducer[part] = "%s_pt_20_eta_0.000.root" % part
    command = 'TrainingTupleProducer --input %s --parity %i --output %s' % \
      (os.path.join(outputDir_ShuffleMerge, outputFile_ShuffleMerge), parity, "%s")
    ##run_command_and_copy_output_to_hdfs(command, outputFiles_TrainingTupleProducer[part], outputDir_scratch, os.path.join(outputDir_TrainingTupleProducer, "%s-events" % part))
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: convert flat "TrainingTuples" to HDF5 format,
#     again separately for events with even and events with odd event numbers
outputFiles_root_to_hdf = {}
for part in [ "even", "odd" ]:
    outputFiles_root_to_hdf[part] = "%s_pt_20_eta_0.000.h5" % part
    command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/root_to_hdf.py --input %s --output %s --trees taus,inner_cells,outer_cells' % \
     (os.path.join(outputDir_TrainingTupleProducer, "%s-events" % part, outputFiles_TrainingTupleProducer[part]), "%s")  
    run_command_and_copy_output_to_hdfs(command, outputFiles_root_to_hdf[part], outputDir_scratch, os.path.join(outputDir_root_to_hdf, "%s-events" % part))
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: run actual DeepTau training
print("Compiling _fill_grid_setup.py script...")
run_command('source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/compile_fill_grid_setup.sh')
print(" Done.")

models = {}
for part in [ "even", "odd" ]:
    print("Running DeepTau training for '%s' sample..." % part)
    models[part] = "DeepTauPhase2HLTv2%s" % part
    command = 'source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/runDeepTau_training.sh %s %s' % \
      (os.path.join(outputDir_root_to_hdf, "%s-events" % part, outputFiles_root_to_hdf[part]), models[part])
    run_command(command)
    print(" Done.")
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: Convert DNN model to graph (.pb) format
for part in [ "even", "odd" ]:
    command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/deploy_model.py --input $CMSSW_BASE/src/TauMLTools/Training/python/2017v2/%s_step1_final.hdf5' % \
      (models[part])
    run_command(command)
    run_command('mv %s_step1_final.pb $CMSSW_BASE/src/TauMLTools/Training/python/2017v2/' % models[part])
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: Classify tau candidates in events with even event numbers 
#     using DeepTau model trained on events with even event numbers and vice versa
outputDirs_root_to_hdf_classified = {}
for part_sample in [ "even", "odd" ]:
    for part_model in [ "even", "odd" ]:
        run_command('mkdir -p %s/testing-classified' % outputDir_scratch)
        command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/apply_training.py --input %s --output %s --model $CMSSW_BASE/src/TauMLTools/Training/python/2017v2/%s_step1_final.pb --chunk-size 1000 --batch-size 100 --max-queue-size 20' % \
          (os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample), os.path.join(outputDir_scratch, "testing-classified"), models[part])
        run_command(command)
        key = '%s-events-classified-by-DeepTau_%s' % (part_sample, part_model)
        outputDirs_root_to_hdf_classified[key] = os.path.join(outputDir_root_to_hdf, "%s-events-classified-by-DeepTau_%s" % (part_sample, part_model))
        move_all_files_to_hdfs(os.path.join(outputDir_scratch, "testing-classified"), outputDirs_root_to_hdf_classified[key])
        run_command('rm -rf %s/testing-classified' % outputDir_scratch)

    # CV: Classify events by cutting on charged isolation pT-sum of the tau candidates for comparison
    run_command('mkdir -p %s/testing-classified' % outputDir_scratch)
    command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/apply_chargedIsoPtSum.py --input %s --output %s --chunk-size 1000 --batch-size 100 --max-queue-size 20' % \
      (os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample), os.path.join(outputDir_scratch, "testing-classified"))
    run_command(command)
    key = '%s-events-classified-by-chargedIsoPtSum' % part_sample
    outputDirs_root_to_hdf_classified[key] = os.path.join(outputDir_root_to_hdf, "%s-events-classified-by-chargedIsoPtSum" % part_sample)
    move_all_files_to_hdfs(os.path.join(outputDir_scratch, "testing-classified"), outputDirs_root_to_hdf_classified[key])
    run_command('rm -rf %s/testing-classified' % outputDir_scratch)
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: Make DeepTau performance plots
#
#    1) Overtraining
for part_model in [ "even", "odd" ]:
    part_sample_train = part_model
    part_sample_test = None
    if part_model == "even":
        part_sample_test = "odd"
    elif part_model == "odd":
        part_sample_test = "even"
    else:
        raise ValueError("Invalid parameter 'part_model' = '%s' !!" % part_model)
    key_train = '%s-events-classified-by-DeepTau_%s' % (part_sample_train, part_model)
    key_test = '%s-events-classified-by-DeepTau_%s' % (part_sample_test, part_model)
    command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/evaluate_performance.py --input-taus %s --input-other %s --other-type jet --deep-results %s --deep-results-label "Train" --prev-deep-results %s --prev-deep-results-label "Test" --output %s/rocCurve_DeepTau_%s_test_vs_train.pdf' % \
      (os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample, outputFiles_root_to_hdf[part_sample]), 
       os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample, outputFiles_root_to_hdf[part_sample]),
       os.path.join(outputDirs_root_to_hdf_classified[key_train], outputFiles_root_to_hdf[part_sample]),
       os.path.join(outputDirs_root_to_hdf_classified[key_test], outputFiles_root_to_hdf[part_sample]),
       outputDir_plots,
       part_model)
#
#    2) Performance of DeepTau compared to charged isolation pT-sum
    key_DeepTau = '%s-events-classified-by-DeepTau_%s' % (part_sample_test, part_model)
    key_chargedIsoPtSum = '%s-events-classified-by-chargedIsoPtSum' % part_sample_test
    command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/evaluate_performance.py --input-taus %s --input-other %s --other-type jet --deep-results %s --deep-results-label "DeepTau" --prev-deep-results %s --prev-deep-results-label "chargedIsoPtSum" --output %s/rocCurve_DeepTau_%s_vs_chargedIsoPtSum.pdf' % \
      (os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample, outputFiles_root_to_hdf[part_sample]), 
       os.path.join(outputDir_root_to_hdf, "%s-events" % part_sample, outputFiles_root_to_hdf[part_sample]),
       os.path.join(outputDirs_root_to_hdf_classified[key_DeepTau], outputFiles_root_to_hdf[part_sample]),
       os.path.join(outputDirs_root_to_hdf_classified[key_chargedIsoPtSum], outputFiles_root_to_hdf[part_sample]),
       outputDir_plots,
       part_model)
#----------------------------------------------------------------------------------------------------
