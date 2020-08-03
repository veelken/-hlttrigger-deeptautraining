#!/usr/bin/env python

import getpass
import os

version = "2020Aug03"

inputDir = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "raw-tuples")

inputDir_sample = {
  'qqH_htt' : os.path.join(inputDir, "qqH_htt"),
  'minbias' : os.path.join(inputDir, "minbias"),
}

outputDir_scratch = os.path.join("/home", getpass.getuser(), "temp/Phase2HLT_DeepTauTraining")

executable_CreateBinnedTuples = 'CreateBinnedTuples'
outputDir_CreateBinnedTuples = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "tuples")

outputFile_size_list = "size_list.txt"
outputDir_size_list = outputDir_CreateBinnedTuples

regexp_sample = {
  'qqH_htt' : "[a-zA-Z0-9_/:.-]*produceDeepTau_rawNtuple_[a-zA-Z0-9_/:.-]+.root",
  'minbias' : "[a-zA-Z0-9_/:.-]*produceDeepTau_rawNtuple_[a-zA-Z0-9_/:.-]+.root",
}

binning_pt  = "20, 25, 30, 35, 40, 50, 60, 80, 120, 1000"
binning_eta = "0., 0.575, 1.15, 1.725, 2.3"

def run_command(command):
    print("executing command = '%s'" % command)
    os.system(command)

run_command('mkdir -p %s' % outputDir_scratch)
run_command('mkdir -p %s' % outputDir_CreateBinnedTuples)

# CV: produce ROOT files for each tau type (tau_h, e, mu, jet), pT, and eta bin
for sample in [ "qqH_htt", "minbias" ]:
    command = '%s --output %s --input-dir %s --n-threads 12 --pt-bins "%s" --eta-bins "%s" --file-name-pattern "%s"' % \
      (executable_CreateBinnedTuples, outputDir_scratch, inputDir_sample[sample], binning_pt, binning_eta, regexp_sample[sample])
    run_command(command)
command = 'cp %s/*.root %s' % (outputDir_scratch, outputDir_CreateBinnedTuples)
run_command(command)
command = 'rm %s/*.root' % outputDir_scratch
run_command(command)

# CV: count number of entries in each ROOT file
command = 'python3 -u TauML/Analysis/python/CreateTupleSizeList.py --input %s >& %s' % (outputDir_CreateBinnedTuples, os.path.join(outputDir_scratch, outputFile_size_list))
##run_command(command)
command = 'cp %s %s' % (os.path.join(outputDir_scratch, outputFile_size_list), os.path.join(outputDir_size_list, outputFile_size_list))
##run_command(command)
command = 'rm %s' % os.path.join(outputDir_scratch, outputFile_size_list)
##run_command(command)
