#!/usr/bin/env python

import getpass
import os
import subprocess

version = "2020Aug03v3"

inputDir = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "raw-tuples")

inputDir_sample = {
  'qqH_htt' : os.path.join(inputDir, "qqH_htt"),
  'minbias' : os.path.join(inputDir, "minbias"),
}

def run_command(command):
    print("executing command = '%s'" % command)
    os.system(command)

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

executable_CreateBinnedTuples = 'CreateBinnedTuples'
outputDir_CreateBinnedTuples = os.path.join("/home", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "tuples")
run_command('mkdir -p %s' % outputDir_CreateBinnedTuples)
for sample in [ "qqH_htt", "minbias" ]:
    run_command('mkdir -p %s' % os.path.join(outputDir_CreateBinnedTuples, sample))

outputFile_size_list = "size_list.txt"
outputDir_size_list = outputDir_CreateBinnedTuples

outputDir_ShuffleMerge = os.path.join("/home", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "training_preparation")
run_command('mkdir -p %s' % outputDir_ShuffleMerge)
run_command('mkdir -p %s/all' % outputDir_ShuffleMerge)
run_command('mkdir -p %s/testing' % outputDir_ShuffleMerge)

outputDir_TrainingTupleProducer = os.path.join("/home", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "tuples-training-root")
run_command('mkdir -p %s' % outputDir_TrainingTupleProducer)

outputDir_root_to_hdf = os.path.join("/home", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "training")
run_command('mkdir -p %s' % outputDir_root_to_hdf)

regexp_sample = {
  'qqH_htt' : "[a-zA-Z0-9_/:.-]*produceDeepTau_rawNtuple_[a-zA-Z0-9_/:.-]+.root",
  'minbias' : "[a-zA-Z0-9_/:.-]*produceDeepTau_rawNtuple_[a-zA-Z0-9_/:.-]+.root",
}

binning_pt  = "20, 25, 30, 35, 40, 50, 60, 80, 120, 1000"
binning_eta = "0., 0.575, 1.15, 1.725, 2.3"

# CV: produce ROOT files for each tau type (tau_h, e, mu, jet), pT, and eta bin
for sample in [ "qqH_htt", "minbias" ]:
    command = '%s --output %s --input-dir %s --n-threads 12 --pt-bins "%s" --eta-bins "%s" --file-name-pattern "%s"' % \
      (executable_CreateBinnedTuples, os.path.join(outputDir_CreateBinnedTuples, sample), inputDir_sample[sample], binning_pt, binning_eta, regexp_sample[sample])
    ##run_command(command)

# CV: count number of entries in each ROOT file
run_command('rm -f %s' % os.path.join(outputDir_CreateBinnedTuples, outputFile_size_list))
command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/CreateTupleSizeList.py --input %s >& %s' % \
  (outputDir_CreateBinnedTuples, os.path.join(outputDir_CreateBinnedTuples, outputFile_size_list))
##run_command(command)

# CV: randomly sample tau candidates of different type, pT, and eta to produce "big training tuple"
for type in [ "tau", "e", "mu", "jet" ]:
    command = 'ShuffleMerge --cfg $CMSSW_BASE/src/TauMLTools/Analysis/config/training_inputs_%s_Phase2HLT.cfg --input %s --output %s/all/%s_pt_20_eta_0.000.root --pt-bins "%s" --eta-bins "%s" --mode MergeAll --calc-weights true --ensure-uniformity true --max-bin-occupancy 500000 --n-threads 12  --disabled-branches "trainingWeight"' % \
      (type, outputDir_CreateBinnedTuples, outputDir_ShuffleMerge, type, binning_pt, binning_eta)
    ##run_command(command)
  
##run_command('rm -f %s' % os.path.join(outputDir_ShuffleMerge, "training_tauTuple.root"))
##run_command('rm -f %s' % os.path.join(outputDir_ShuffleMerge, outputFile_size_list))
command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/CreateTupleSizeList.py --input %s >& %s' % \
  (outputDir_ShuffleMerge, os.path.join(outputDir_ShuffleMerge, outputFile_size_list))
##run_command(command)

command = 'ShuffleMerge --cfg $CMSSW_BASE/src/TauMLTools/Analysis/config/training_inputs_step2_Phase2HLT.cfg --input %s --output %s/training_tauTuple.root --pt-bins "20, 1000" --eta-bins "0., 2.3" --mode MergeAll --calc-weights false --ensure-uniformity true --max-bin-occupancy 100000000 --n-threads 12' % \
  (outputDir_ShuffleMerge, outputDir_ShuffleMerge)
##run_command(command)

command = 'ShuffleMerge --cfg $CMSSW_BASE/src/TauMLTools/Analysis/config/testing_inputs_Phase2HLT.cfg --input %s --output %s/testing --pt-bins "%s" --eta-bins "%s" --mode MergePerEntry --calc-weights false --ensure-uniformity false --max-bin-occupancy 20000 --n-threads 12 --disabled-branches "trainingWeight"' % \
  (outputDir_CreateBinnedTuples, outputDir_ShuffleMerge, binning_pt, binning_eta)
##run_command(command)

# CV: produce flat "TrainingTuples" 
command = 'TrainingTupleProducer --input %s/training_tauTuple.root --output %s/part_0.root' % \
  (outputDir_ShuffleMerge, outputDir_TrainingTupleProducer)
##run_command(command)

# CV: convert flat "TrainingTuples" to HDF5 format
command = 'python $CMSSW_BASE/src/TauMLTools/Analysis/python/root_to_hdf.py --input %s/part_0.root --output %s/part_0.h5 --trees taus,inner_cells,outer_cells' % \
  (outputDir_TrainingTupleProducer, outputDir_root_to_hdf)
##run_command(command)

# CV: run actual DeepTau training
print("Compiling _fill_grid_setup.py script...")
run_command('source $CMSSW_BASE/src/HLTrigger/DeepTauTraining/test/compile_fill_grid_setup.sh')
print(" Done.")
