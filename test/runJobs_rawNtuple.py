#!/usr/bin/env python

import getpass
import os

from HLTrigger.TallinnHLTPFTauAnalyzer.tools.jobTools import getInputFileNames, build_sbatchManagerFile, build_Makefile

signal_and_background_samples = {
  'qqH_htt' : {
    'samples' : {
      'offlinePrimaryVertices' : { 
        'inputFilePath' : '/hdfs/cms/store/user/rdewanje/VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5/HLTConfig_VBFHToTauTau_M125_14TeV_powheg_pythia8_correctedGridpack_tuneCP5_wOfflineVtx_DeepTau/200729_084644/',
        'numEvents' : 273588
      }
    },
    'numJobs' : 15
  },
  'minbias' : {
    'samples' : {
      'offlinePrimaryVertices' : { 
        'inputFilePath' : '/hdfs/cms/store/user/rdewanje/MinBias_TuneCP5_14TeV-pythia8/HLTConfig_MinBias_TuneCP5_14TeV-pythia8_wOfflineVtx_DeepTau/200729_084837/',
        'numEvents' : 648832
      }
    },
    'numJobs' : 50
  }
}

run_hlt_algorithms = [ "hps" ]
##run_hlt_srcVertices = [ "offlinePrimaryVertices", "hltPhase2PixelVertices" ]
run_hlt_srcVertices = [ "offlinePrimaryVertices" ]
##run_hlt_srcVertices = [ "hltPhase2PixelVertices" ]
##run_hlt_isolation_maxDeltaZOptions = [ "primaryVertex", "leadTrack" ]
run_hlt_isolation_maxDeltaZOptions = [ "primaryVertex" ]
##run_hlt_isolation_minTrackHits = [ 3, 5, 8 ]
run_hlt_isolation_minTrackHits = [ 8 ]
cfgFileName_original = "produceDeepTau_rawNtuple_cfg.py"

version = "2020Aug05"

configDir  = os.path.join("/home",       getpass.getuser(), "Phase2HLT/DeepTauTraining", version)
outputDir  = os.path.join("/hdfs/local", getpass.getuser(), "Phase2HLT/DeepTauTraining", version, "raw-tuples")
workingDir = os.getcwd()
cmsswDir   = os.getenv('CMSSW_BASE')

def run_command(command):
    #print("executing command = '%s'" % command)
    os.system(command)

run_command('mkdir -p %s' % configDir)
run_command('mkdir -p %s' % outputDir)
for sampleName in signal_and_background_samples.keys(): 
    run_command('mkdir -p %s' % os.path.join(outputDir, sampleName))

def build_cfgFile(cfgFileName_original, cfgFileName_modified, 
                  inputFileNames, process, 
                  hlt_srcVertices, hlt_algorithm, hlt_isolation_maxDeltaZOption, hlt_isolation_minTrackHits,
                  outputFileName):
    print("Building configFile = '%s'" % cfgFileName_modified)

    rmCommand   = 'rm -f %s' % cfgFileName_modified
    run_command(rmCommand)
 
    sedCommand  = 'sed'
    sedCommand += ' "s/##inputFilePath/inputFilePath/; s/\$inputFilePath/None/;'
    sedCommand += '  s/##inputFileNames/inputFileNames/; s/\$inputFileNames/%s/;' % [ inputFileName.replace("/", "\/") for inputFileName in inputFileNames ]
    sedCommand += '  s/##processName/processName/; s/\$processName/%s/;' % process
    sedCommand += '  s/##hlt_srcVertices/hlt_srcVertices/; s/\$hlt_srcVertices/%s/;' % hlt_srcVertices
    sedCommand += '  s/##hlt_algorithm/hlt_algorithm/; s/\$hlt_algorithm/%s/;' % hlt_algorithm
    sedCommand += '  s/##hlt_isolation_maxDeltaZOptions/hlt_isolation_maxDeltaZOptions/; s/\$hlt_isolation_maxDeltaZOption/%s/;' % hlt_isolation_maxDeltaZOption
    sedCommand += '  s/##hlt_isolation_minTrackHits/hlt_isolation_minTrackHits/; s/\$hlt_isolation_minTrackHits/%s/;' % hlt_isolation_minTrackHits
    sedCommand += '  s/##outputFileName/outputFileName/; s/\$outputFileName/%s/"' % outputFileName
    sedCommand += ' %s > %s' % (cfgFileName_original, cfgFileName_modified)
    run_command(sedCommand)

jobOptions = {} # key = sampleName + hlt_algorithm + hlt_isolation_maxDeltaZOption + hlt_isolation_minTrackHits (all separated by underscore)
for sampleName, sample in signal_and_background_samples.items(): 
    for hlt_srcVertices in run_hlt_srcVertices:
        print("processing sample = '%s': hlt_srcVertices = '%s'" % (sampleName, hlt_srcVertices)) 
        inputFilePath = sample['samples'][hlt_srcVertices]['inputFilePath']
        print(" inputFilePath = '%s'" % inputFilePath)
        inputFileNames = None
        numInputFiles = None
        if os.path.exists(inputFilePath):
            inputFileNames = getInputFileNames(inputFilePath)
            numInputFiles = len(inputFileNames)
            print("Found %i input files." % numInputFiles)
        else:
            print("Path = '%s' does not exist --> skipping !!" % inputFilePath)
            continue
        numJobs = sample['numJobs']
        for jobId in range(numJobs):
            idxFirstFile = jobId*numInputFiles/numJobs
            idxLastFile = (jobId + 1)*numInputFiles/numJobs - 1
            inputFileNames_job = inputFileNames[idxFirstFile:idxLastFile + 1]
            #print("job #%i: inputFiles = %s" % (jobId, inputFileNames_job))
            for hlt_algorithm in run_hlt_algorithms:
                for hlt_isolation_maxDeltaZOption in run_hlt_isolation_maxDeltaZOptions:
                    for hlt_isolation_minTrackHits in run_hlt_isolation_minTrackHits:
                        job_key = '%s_%s_%s_dz_wrt_%s_%iHits' % (sampleName, hlt_algorithm, hlt_srcVertices, hlt_isolation_maxDeltaZOption, hlt_isolation_minTrackHits)
                        if not job_key in jobOptions.keys():
                            jobOptions[job_key] = []        
                        cfgFileName_modified = os.path.join(configDir, "produceDeepTau_rawNtuple_%s_%i_cfg.py" % \
                          (job_key, jobId))
                        outputFileName = "produceDeepTau_rawNtuple_%s_%i.root" % \
                          (job_key, jobId)
                        build_cfgFile(
                          cfgFileName_original, cfgFileName_modified, 
                          inputFileNames_job, sampleName,
                          hlt_srcVertices, hlt_algorithm, hlt_isolation_maxDeltaZOption, hlt_isolation_minTrackHits,
                          outputFileName)
                        logFileName = cfgFileName_modified.replace("_cfg.py", ".log")
                        jobOptions[job_key].append({
                          'inputFileNames' : inputFileNames_job,
                          'cfgFileName'    : cfgFileName_modified,
                          'outputFilePath' : os.path.join(outputDir, sampleName),
                          'outputFileName' : outputFileName,
                          'logFileName'    : logFileName,
                        })

sbatchManagerFileName = os.path.join(configDir, "sbatch_produceDeepTau_rawNtuple.py")
jobOptions_sbatchManager = []
for job_key, jobs in jobOptions.items():
    jobOptions_sbatchManager.extend(jobs)
build_sbatchManagerFile(sbatchManagerFileName, jobOptions_sbatchManager, workingDir, cmsswDir, version)

jobOptions_Makefile_sbatch = []
jobOptions_Makefile_sbatch.append({
  'target'          : "phony",
  'dependencies'    : [],
  'commands'        : [ 'python %s' % sbatchManagerFileName ],
  'outputFileNames' : [ os.path.join(job['outputFilePath'], job['outputFileName']) for job in jobOptions_sbatchManager ],
})
makeFileName_sbatch = os.path.join(configDir, "Makefile_sbatch")
build_Makefile(makeFileName_sbatch, jobOptions_Makefile_sbatch)

message  = "Finished building config files."
message += " Now execute 'make -f %s' to submit the jobs to the batch system." % makeFileName_sbatch
print(message)
