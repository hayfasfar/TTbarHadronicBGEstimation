#!/usr/bin/env python

import json
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', help='input json file')
parser.add_argument('--output', '-o', help='name of the output file to create')

args = parser.parse_args()

# Load the json output of combineTool.py -M Impacts
with open(args.input,"r") as impacts:
  impacts_info = json.load(impacts)
Nparams = len(impacts_info["params"])
print"Nparams:",Nparams

##-- Locate Unconstrained Params
params_to_remove = []
for param_i in range(0,Nparams):
    param_info = impacts_info["params"][param_i]
    if "bin" in param_info["name"]:
        params_to_remove.append(param_i)
        print"Removing param:",param_i

params_to_remove.reverse() ## to avoid trying to delete not accessible element (already removed elements, shortens length of dictionary)

##-- Remove Unconstrained Params
for param_to_remove in params_to_remove:
    print"removing param:",param_to_remove
    #print json.dumps(impacts_info["params"][param_to_remove], indent=4)
    del(impacts_info["params"][param_to_remove])


with open(args.output,"w") as updatedJson:
      json.dump(impacts_info, updatedJson)
