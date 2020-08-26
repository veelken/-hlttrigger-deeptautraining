#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser(description='Dump Panda dataframe contained in hdf5 file.')
parser.add_argument('--input', required=True, type=str, help="Input hdf5 file")
parser.add_argument('--tree', required=False, type=str, default="taus", help="Name of ROOT tree from which the Panda dataframe was created")
args = parser.parse_args()

import os
import pandas

if not os.path.isfile(args.input):
    raise ValueError("Input file = '%s' does not exist !!" % args.input)

df = pandas.read_hdf(args.input, args.tree)
print("Number of rows in Panda dataframe '%s' = %i" % (args.tree, df['run'].count()))

if args.tree == "taus":
    selected_columns = df[ ["run", "lumi", "evt"] ]
    first_ten_rows = selected_columns[0:10]
    print(first_ten_rows)
