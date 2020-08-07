#!/usr/bin/env python

import getpass
import os
import subprocess
import time

version_rawNtuples = "2020Aug05"
version_training = "training_v1"

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
    delay = 20*num_files
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
outputDir_CreateBinnedTuples = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "tuples")
run_command('mkdir -p %s' % outputDir_CreateBinnedTuples)
for sample in [ "qqH_htt", "minbias" ]:
    run_command('mkdir -p %s' % os.path.join(outputDir_CreateBinnedTuples, sample))

outputFile_size_list = "size_list.txt"
outputDir_size_list = outputDir_CreateBinnedTuples

outputDir_ShuffleMerge = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "training-preparation")
run_command('mkdir -p %s' % outputDir_ShuffleMerge)
run_command('mkdir -p %s/all' % outputDir_ShuffleMerge)
run_command('mkdir -p %s/testing' % outputDir_ShuffleMerge)

outputDir_TrainingTupleProducer = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "tuples-training-root")
run_command('mkdir -p %s' % outputDir_TrainingTupleProducer)
run_command('mkdir -p %s/testing' % outputDir_TrainingTupleProducer)

outputDir_root_to_hdf = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "tuples-training-hdf5")
run_command('mkdir -p %s' % outputDir_root_to_hdf)
run_command('mkdir -p %s/testing' % outputDir_root_to_hdf)
run_command('mkdir -p %s/testing-classified-DeepTau' % outputDir_ShuffleMerge)
run_command('mkdir -p %s/testing-classified-chargedIsoPtSum' % outputDir_ShuffleMerge)

outputDir_performance_plots = os.path.join("/home", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, version_training, "plots")
run_command('mkdir -p %s' % outputDir_performance_plots)

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
    run_command_and_copy_output_to_hdfs(command, outputFile_ShuffleMerge, outputDir_scratch, os.path.join(outputDir_ShuffleMerge, "all"))

# CV: count number of entries in each ROOT file again
outputFile_ShuffleMerge = "training_tauTuple.root"
##run_command('rm -f %s' % os.path.join(outputDir_ShuffleMerge, outputFile_ShuffleMerge))
outputFile_size_list = "size_list.txt"
##run_command('rm -f %s' % os.path.join(outputDir_ShuffleMerge, outputFile_size_list))
command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/CreateTupleSizeList.py --input %s >& %s' % \
  (outputDir_ShuffleMerge, "%s")
##run_command_and_copy_output_to_hdfs(command, outputFile_size_list, outputDir_scratch, outputDir_ShuffleMerge)
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# CV: 
outputFile_ShuffleMerge = "training_tauTuple.root"
command = 'ShuffleMerge --cfg $CMSSW_BASE/src/TauMLTools/Analysis/config/training_inputs_step2_Phase2HLT.cfg --input %s --output %s --pt-bins "20, 1000" --eta-bins "0., 2.3" --mode MergeAll --calc-weights false --ensure-uniformity true --max-bin-occupancy 500000 --n-threads 12' % \
  (outputDir_ShuffleMerge, "%s")
##run_command_and_copy_output_to_hdfs(command, outputFile_ShuffleMerge, outputDir_scratch, outputDir_ShuffleMerge)
#----------------------------------------------------------------------------------------------------

run_command('mkdir -p %s/testing' % outputDir_scratch)
command = 'ShuffleMerge --cfg $CMSSW_BASE/src/TauMLTools/Analysis/config/testing_inputs_Phase2HLT.cfg --input %s --output %s/testing --pt-bins "%s" --eta-bins "%s" --mode MergePerEntry --calc-weights false --ensure-uniformity false --max-bin-occupancy 20000 --n-threads 12 --disabled-branches "trainingWeight"' % \
  (outputDir_CreateBinnedTuples, outputDir_scratch, binning_pt, binning_eta)
run_command(command)
move_all_files_to_hdfs(os.path.join(outputDir_scratch, "testing"), os.path.join(outputDir_ShuffleMerge, "testing"))
run_command('rm -rf %s/testing' % outputDir_scratch)

# CV: produce flat "TrainingTuples" 
outputFile_TrainingTupleProducer = "part_0.root"
command = 'TrainingTupleProducer --input %s --output %s' % \
  (os.path.join(outputDir_ShuffleMerge, outputFile_ShuffleMerge), "%s")
##run_command_and_copy_output_to_hdfs(command, outputFile_TrainingTupleProducer, outputDir_scratch, outputDir_TrainingTupleProducer)

run_command('mkdir -p %s/testing' % outputDir_scratch)
idx_part = 0
for sample in [ "qqH_htt", "minbias" ]:
    for type in [ "tau", "e", "mu", "jet" ]:
        outputFile_ShuffleMerge = "%s_%s.root" % (type, sample)
        if os.path.isfile(os.path.join(outputDir_ShuffleMerge, inputFile_TrainingTupleProducer)):
            outputFile_TrainingTupleProducer = "part_%i.root" % idx_part
            idx_part += 1
            command = 'TrainingTupleProducer --input %s/testing --output/testing %s' % \
              (os.path.join(outputDir_ShuffleMerge, outputFile_ShuffleMerge), "%s")
            run_command_and_copy_output_to_hdfs(command, outputFile_TrainingTupleProducer, os.path.join(outputDir_scratch, "testing"), os.path.join(outputDir_TrainingTupleProducer, "testing"))
num_parts = idx_part + 1
run_command('rm -rf %s/testing' % outputDir_scratch)

# CV: convert flat "TrainingTuples" to HDF5 format
outputFile_root_to_hdf = "part_0.h5"
command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/root_to_hdf.py --input %s --output %s --trees taus,inner_cells,outer_cells' % \
  (os.path.join(outputDir_TrainingTupleProducer, outputFile_TrainingTupleProducer), "%s")
##run_command_and_copy_output_to_hdfs(command, outputFile_root_to_hdf, outputDir_scratch, outputDir_root_to_hdf)

run_command('mkdir -p %s/testing' % outputDir_scratch)
for idx_part in range(num_parts):
    outputFile_TrainingTupleProducer = "part_%i.root" % idx_part
    outputFile_root_to_hdf = "part_%i.h5" % idx_part
    command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/root_to_hdf.py --input %s --output %s --trees taus,inner_cells,outer_cells' % \
      (os.path.join(outputDir_TrainingTupleProducer, "testing", outputFile_TrainingTupleProducer), "%s")
    run_command_and_copy_output_to_hdfs(command, outputFile_root_to_hdf, os.path.join(outputDir_scratch, "testing"), os.path.join(outputDir_root_to_hdf, "testing"))
run_command('rm -rf %s/testing' % outputDir_scratch)

# CV: run actual DeepTau training
print("Compiling _fill_grid_setup.py script...")
##run_command('source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/compile_fill_grid_setup.sh')
print(" Done.")

print("Running DeepTau training...")
##run_command('source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/runDeepTau_training.sh')
print(" Done.")

command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/deploy_model.py --input $CMSSW_BASE/src/TauMLTools/Training/python/2017v2/DeepTauPhase2HLTv1_step1_final.hdf5'
##run_command(command)
##run_command('mv DeepTauPhase2HLTv1_step1_final.pb $CMSSW_BASE/src/TauMLTools/Training/python/2017v2/DeepTauPhase2HLTv1_step1_final.pb')

# CV: test DeepTau performance
run_command('mkdir -p %s/testing-classified' % outputDir_scratch)
command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/apply_training.py --input %s --output %s --model $CMSSW_BASE/src/TauMLTools/Training/python/2017v2/DeepTauPhase2HLTv1_step1_final.pb --chunk-size 1000 --batch-size 100 --max-queue-size 20' % \
  (os.path.join(outputDir_ShuffleMerge, "testing"), os.path.join(outputDir_scratch, "testing-classified"))
run_command(command)
move_all_files_to_hdfs(os.path.join(outputDir_scratch, "testing-classified"), os.path.join(outputDir_ShuffleMerge, "testing-classified-DeepTau"))
run_command('rm -rf %s/testing-classified' % outputDir_scratch)

run_command('mkdir -p %s/testing-classified' % outputDir_scratch)
command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/apply_chargedIsoPtSum.py --input %s --output %s --chunk-size 1000 --batch-size 100 --max-queue-size 20' % \
  (os.path.join(outputDir_ShuffleMerge, "testing"), os.path.join(outputDir_scratch, "testing-classified"))
run_command(command)
move_all_files_to_hdfs(os.path.join(outputDir_scratch, "testing-classified"), os.path.join(outputDir_ShuffleMerge, "testing-classified-chargedIsoPtSum"))
run_command('rm -rf %s/testing-classified' % outputDir_scratch)

command = 'python $CMSSW_BASE/src/TauMLTools/Training/python/evaluate_performance.py --input-taus %s --input-other %s --other-type jet --deep-results %s --deep-results-label "DeepTau" --prev-deep-results %s --prev-deep-results-label "chargedIsoPtSum" --output %s/rocCurve_DeepTau_vs_chargedIsoPtSum.pdf' % \
  (os.path.join(outputDir_ShuffleMerge, "testing/tau_qqH_htt.root"), os.path.join(outputDir_ShuffleMerge, "testing/jet_minbias.root"), 
   os.path.join(outputDir_ShuffleMerge, "testing-classified-DeepTau/tau_qqH_htt.hd5"), os.path.join(outputDir_ShuffleMerge, "testing-classified-DeepTau/jet_minbias.hd5"), 
   os.path.join(outputDir_ShuffleMerge, "testing-classified-chargedIsoPtSum/tau_qqH_htt.hd5"), os.path.join(outputDir_ShuffleMerge, "testing-classified-chargedIsoPtSum/jet_minbias.hd5"), 
   outputDir_performance_plots)
run_command(command)
