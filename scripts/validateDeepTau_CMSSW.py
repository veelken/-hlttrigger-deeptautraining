#!/usr/bin/env python

import pandas
import numpy as np
import uproot
import matplotlib.pyplot as plt
import os

##inputFileName_hdf5 = '%s/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5-classified/tuple_DEBUG_qqH_htt_pred.h5' %  os.environ['CMSSW_BASE']
inputFileName_hdf5 = '%s/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5/tuple_DEBUG_qqH_htt.h5' %  os.environ['CMSSW_BASE']
df_hdf5 = pandas.read_hdf(inputFileName_hdf5, "taus")
inputFileName_hdf5_classified = '%s/src/HLTrigger/DeepTauTraining/test/DEBUG/hdf5-classified/tuple_DEBUG_qqH_htt_pred.h5' %  os.environ['CMSSW_BASE']
df_hdf5_classified = pandas.read_hdf(inputFileName_hdf5_classified)

df_hdf5_merged = pandas.concat([ df_hdf5, df_hdf5_classified ], axis=1)

def ProcessDF(df):
    df['deepId_tau_vs_jet'] = pandas.Series(df['deepId_tau'] / (df['deepId_tau'] + df['deepId_jet']), index=df.index)
    df['deepId_tau_vs_mu']  = pandas.Series(df['deepId_tau'] / (df['deepId_tau'] + df['deepId_mu']), index=df.index)
    df['deepId_tau_vs_e']   = pandas.Series(df['deepId_tau'] / (df['deepId_tau'] + df['deepId_e']), index=df.index)
    df['deepId_tau_vs_all'] = pandas.Series(df['deepId_tau'] / (df['deepId_tau'] + df['deepId_e'] + df['deepId_mu'] + df['deepId_jet']), index=df.index)

ProcessDF(df_hdf5_merged)

def ReadBrancesToDataFrame(file_name, tree_name):
    with uproot.open(file_name) as file:
        tree = file[tree_name]
        df = tree.arrays(outputtype=pandas.DataFrame)
        df.columns = [ c.decode('utf-8') for c in df.columns ]
    return df

inputFileName_cmssw = '%s/src/HLTrigger/DeepTauTraining/test/deepTauTest_qqH_htt.root' %  os.environ['CMSSW_BASE']
df_cmssw = ReadBrancesToDataFrame(inputFileName_cmssw, 'taus')

print("df_hdf5 shape:", df_hdf5_merged.shape)
print("df_cmssw shape:", df_cmssw.shape)
print("")

print("df_hdf5:")
for index, row in df_hdf5_merged.iterrows():
    result = ( int(row['run']), int(row['lumi']), int(row['evt']), row['spectator_tau_pt'], row['spectator_tau_eta'], row['spectator_tau_phi'], row['deepId_tau_vs_jet'] )
    print("index = %i: result = %s" % (index, result))
    print(" e = %1.4f, mu = %1.4f, tau = %1.4f, jet = %1.4f" % (row['deepId_e'], row['deepId_mu'], row['deepId_tau'], row['deepId_jet']))
print("")

print("df_cmssw:")
for index, row in df_cmssw.iterrows():
    result = ( int(row['run']), int(row['lumi']), int(row['evt']), row['pt'], row['eta'], row['phi'], row['byDeepTau2017v2VSjetraw'] )
    print("index = %i: result = %s" % (index, result))
print("")

##raise ValueError("STOP.")

acc = 1e-4
bins = np.linspace(-acc, acc, num=100)
var_hdf5 = 'deepId_tau_vs_jet'
var_cmssw = 'byDeepTau2017v2VSjetraw'
x = df_cmssw[var_cmssw] - df_hdf5_merged[var_hdf5]
print("x = %s" % x)
for index, row in df_cmssw.iterrows():
    result = ( int(row['run']), int(row['lumi']), int(row['evt']), row['pt'], row['eta'], row['phi'], x[index] )
    print("index = %i: diff = %s" % (index, result))
##print('max: ', np.abs(x).max())
##print('within acc:', np.count_nonzero(np.abs(x) < acc)/x.shape[0])
##plt.hist(x, bins=bins)
##plt.xlim([bins[0], bins[-1]]);
