#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser(description="Dump number of tau, electron, muon, and jet entries contained in txt file produced by 'CreateTupleSizeList.py' command.")
parser.add_argument('--input', required=True, type=str, help="Input file")
args = parser.parse_args()

import os
import re

##line_regex = r"(?P<sample>[a-zA-Z0-9-_]+)\/(?P<tau_type>tau|e|mu|jet|other)[a-zA-Z0-9-_]*\s(?P<entries>[0-9]+)\s"
##line_regex = r"(?P<sample>[a-zA-Z0-9-_]+)\/[a-zA-Z0-9-_.]*\s+(?P<entries>[0-9]+)\s*"
line_regex = r"(?P<sample>[a-zA-Z0-9-_]+)\/(?P<tau_type>tau|e|mu|jet|other)[a-zA-Z0-9-_.]*\s+(?P<entries>[0-9]+)\s*"
line_matcher = re.compile(line_regex)

if not os.path.isfile(args.input):
    raise ValueError("Input file = '%s' does not exist !!" % args.input)

print("Reading number of entries from file = '%s'..." % args.input)
input_file = open(r"%s" % args.input, "r+")
lines = input_file.readlines()
input_file.close()
print(" Done.")

entries_per_tau_type = {}
entries_per_sample = {}
entries_per_tau_type_and_sample = {}

def addToDict(dict, keys, value):
    if len(keys) > 1:
        key0 = keys[0]
        if not key0 in dict.keys():
            dict[key0] = {}
        addToDict(dict[key0], keys[1:], value)
    else:
        key0 = keys[0]
        if not key0 in dict.keys():
            dict[key0] = 0
        dict[key0] += value

for line in lines:
    match = line_matcher.match(line)
    if match:
       sample = match.group('sample')
       tau_type = match.group('tau_type')
       entries = int(match.group('entries'))
       addToDict(entries_per_tau_type, [ tau_type ], entries)
       addToDict(entries_per_sample, [ sample ], entries)
       addToDict(entries_per_tau_type_and_sample, [ tau_type, sample ], entries)

print("Entries per tau type:")
total = 0
for tau_type, entries in entries_per_tau_type.items():
    print(" %s: %i" % (tau_type, entries))
    total += entries
print("Total number of entries = %s" % total)
print("")

print("Entries per sample:")
total = 0
for sample, entries in entries_per_sample.items():
    print(" %s: %i" % (sample, entries))
    total += entries
print("Total number of entries = %s" % total)
print("")

print("Entries per tau type and sample:")
total = 0
for tau_type in entries_per_tau_type_and_sample.keys():
    for sample, entries in entries_per_tau_type_and_sample[tau_type].items():
        print(" %s, %s: %i" % (tau_type, sample, entries))
        total += entries
print("Total number of entries = %s" % total)
print("")
