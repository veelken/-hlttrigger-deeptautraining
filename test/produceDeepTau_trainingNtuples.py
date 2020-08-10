#!/usr/bin/env python

import getpass
import os
import subprocess
import time

from HLTrigger.DeepTauTraining.run_command import *

version_rawNtuples = "2020Aug05"
version_training = "training_v2"

inputDir = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version_rawNtuples, "raw-tuples")

inputDir_sample = {
  'qqH_htt' : os.path.join(inputDir, "qqH_htt"),
  'minbias' : os.path.join(inputDir, "minbias"),
}

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
