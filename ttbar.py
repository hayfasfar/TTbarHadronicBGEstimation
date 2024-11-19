from time import time
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball
import ROOT
import os, sys
import numpy as np
import json
import argparse
from collections import OrderedDict


parser = argparse.ArgumentParser(description="input to the 2DAlphabet")
parser.add_argument("--cat", type=str, help="category")
parser.add_argument("--path", type=str, required=True, help="root files input path.")

parser.add_argument('--senario', choices=['RSGluon', 'ZPrime'], required=True, help='Specify the signal senario to process limits: RSGluon or ZPrime.')
parser.add_argument('--signal', help='Specify a single signal to process (e.g., RSGluon2000).')
parser.add_argument('--senario_fit', choices=['RSGluon', 'ZPrime'], help='Specify the signal senario to process the fit: RSGluon or ZPrime.')


args = parser.parse_args()


cat = args.cat
senario = args.senario
path = args.path
json_file='jsons/config/ttbar_'+str(cat)+'.json'



def load_signals_from_json(json_signals, senario):
    """Load signals from the provided JSON file."""
    with open(json_signals, 'r') as file:
        data = json.load(file)
    if senario in data:
        signals_with_prefix = ['signal' + signal for signal in data[senario]]
        return signals_with_prefix
    else:
        print("Error: Scenario", senario, " not found in the JSON file.")
        return []

signals = load_signals_from_json('jsons/signals.json', senario)


with open(json_file, 'r') as file:
    data = json.load(file, object_pairs_hook=OrderedDict)


if 'GLOBAL' in data :
	data['GLOBAL']['path'] = path
        data['GLOBAL']['SIGNAME']= signals
  
with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

def get_transfer_function(cat):
    with open("jsons/TransferFunctions.json", "r") as file:
        transfer_functions = json.load(file)
    return transfer_functions[cat]



def process_signals(signals):
    """Process the given list of signals."""
    for sig in signals:
        ML_fit(sig)
        plot_fit(sig)
        perform_limit(sig)
        GoF(sig)


dname= ''
params = get_transfer_function(cat) 
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
savedirname = 'output/ttbarfits_'+cat+'_'+dname+params

print 'saving to {0}'.format(savedirname)

def _generate_constraints(nparams):
    out = {}
    for i in range(nparams):
        if i == 0:
            out[i] = {"MIN":-1000,"MAX":1000}
        else:
            out[i] = {"MIN":-1000,"MAX":1000}
    return out

_rpf_options = {
    '0x0': {
        'form': '0.1*(@0)',
        'constraints': _generate_constraints(1)
    },
    '1x0': {
        'form': '0.1*(@0+@1*x)',
        'constraints': _generate_constraints(2)
    },
    '0x1': {
        'form': '0.1*(@0+@1*y)',
        'constraints': _generate_constraints(2)
    },
    '0x2': {
        'form': '0.1*(@0+@1*y+@2*y*y)',
        'constraints': _generate_constraints(3)
    },
    '0x3': {
        'form': '0.1*(@0+@1*y+@2*y*y+@3*y*y*y)',
        'constraints': _generate_constraints(4)
    },
    '1x1': {
        'form': '0.1*(@0+@1*x)*(1+@2*y)',
        'constraints': _generate_constraints(3)
    },
    '1x2': {
        'form': '0.1*(@0+@1*x)*(1+@2*y+@3*y*y)',
        'constraints': _generate_constraints(4)
    },
    '1x3': {
        'form': '0.1*(@0+@1*x)*(1+23*y+@3*y*y+@4*y*y*y)',
        'constraints': _generate_constraints(5)
    },
    '2x1': {
        'form': '0.1*(@0+@1*x+@2*x**2)*(1+@3*y)',
        'constraints': _generate_constraints(4)
    },
    '2x2': {
        'form': '0.1*(@0+@1*x+@2*x**2)*(1+@3*y+@4*y**2)',
        'constraints': _generate_constraints(5)
    },
    '2x3': {
        'form': '0.1*(@0+@1*x+@2*x*x)*(1+@3*y+@4*y*y+@5*y*y*y)',
        'constraints': _generate_constraints(6)
    },
    '3x2': {
        'form': '0.1*(@0+@1*x+@2*x*x+@3*x*x*x)*(1+@4*y+@5*y*y)',
        'constraints': _generate_constraints(6)
    },
    '3x1': {
        'form': '0.1*(@0+@1*x+@2*x*x+@3*x*x*x)*(1+@4*y)',
        'constraints': _generate_constraints(5)
    },
    '3x3': {
        'form': '0.1*(@0+@1*x+@2*x*x+@3*x*x*x)*(1+@4*y+@5*y*y+@6*y*y*y)',
        'constraints': _generate_constraints(7)
    },
    'tf1': {
        'form': '0.1*(@0+@1*x+@2*x**2+@3*sqrt(x)*log(x))*(1+@4*y+@5*y*y+@6*y*y*y)',
        'constraints': _generate_constraints(7)
    }
}



    
rmin = -6
rmax = 6
extra='--robustFit=1'


# for b*, the P/F regions are named MtwvMtPass and MtwvMtFail
# so, just need to find and replace Pass/Fail depending on which region we want
def _get_other_region_names(pass_reg_name):
    return pass_reg_name, pass_reg_name.replace('Pass','Fail')

def _select_signal(row, args):
    '''Used by the Ledger.select() method to create a subset of a Ledger.
    This function provides the logic to determine which entries/rows of the Ledger
    to keep for the subset. The first argument should always be the row to process.
    The arguments that follow will be the other arguments of Ledger.select().
    This function should ALWAYS return a bool that signals whether to keep (True)
    or drop (False) the row.

    To check if entries in the Ledger pass, we can access a given row's
    column value via attributes which are named after the columns (ex. row.process
    gets the "process" column). One can also access them as keys (ex. row["process"]).

    In this example, we want to select for signals that have a specific string
    in their name ("process"). Thus, the first element of `args` contains the string
    we want to find.

    We also want to pick a TF to use so the second element of `args` contains a
    string to specify the Background_args[1] process we want to use.

    Args:
        row (pandas.Series): The row to evaluate.
        args (list): Arguments to pass in for the evaluation.

    Returns:
        Bool: True if keeping the row, False if dropping.
    '''
    signame = args[0]
    if row.process_type == 'SIGNAL':
        if signame in row.process:
            return True
        else:
            return False
    else:
        return True

def make_workspace():
    '''
    Constructs the workspace for all signals listed in the "SIGNAME" list in the 
    "GLOBAL" object in the json config file. This allows for one complete workspace to be
    created in which all the desired signals exist for you to select from later. 
    '''

    # Create the twoD object which starts by reading the JSON config and input arguments to
    # grab input simulation and data histograms, rebin them if needed, and save them all
    # in one place (organized_hists.root). The modified JSON config (with find-replaces applied, etc)
    # is also saved as runConfig.json. This means, if you want to share your analysis with
    # someone, they can grab everything they need from this one spot - no need to have access to
    # the original files! (Note though that you'd have to change the config to point to organized_hists.root).
    
    
    
    
    twoD = TwoDAlphabet(savedirname,json_file, loadPrevious=False)
    
    # Create the data - BKGs histograms
    qcd_hists = twoD.InitQCDHists()

    # There are only 'Pass' and 'Fail' in twoD.ledger.GetRegions(), 
    # since we only have a 'Pass' and a 'Fail' region in the input histos.
    # Therefore, this loop will only run once. 
    for p, f in [_get_other_region_names(r) for r in twoD.ledger.GetRegions() if 'Pass' in r]:
        # Gets the Binning object and some meta information (stored in `_`) that we don't care about
        # The Binning object is needed for constructing the Alphabet objects.
        # If one wanted to be very robust, they could get the binning for `p` as well and check 
        # that the binning is consistent between the two.
        
        print('regions', p, f)
        
        binning_f, _ = twoD.GetBinningFor(f)
        
        # Next we construct the Alphabet objects which all inherit from the Generic2D class.
        # This class constructs and stores RooAbsArg objects (RooRealVar, RooFormulaVar, etc)
        # which represent each bin in the space.

        # First we make a BinnedDistribution which is a collection of RooRealVars built from a starting
        # histogram (`qcd_hists[f]`). These can be set to be constants but, if not, they become free floating
        # parameters in the fit.
        fail_name = 'QCD_'+f
        qcd_f = BinnedDistribution(
                    fail_name, qcd_hists[f],
                    binning_f, constant=False
                )

        # Next we'll book a constant transfer function to transfer from Fail -> Pass
        qcd_rpf = ParametricFunction(
                        fail_name.replace('Fail','rpf'),
                        binning_f, _rpf_options[params]['form'],
                        constraints= _rpf_options[params]['constraints']
                   )

        # We add it to `twoD` so its included when making the RooWorkspace and ledger.
        # We specify the name of the process, the region it lives in, and the object itself.
        # The process is assumed to be a background and colored yellow but this can be changed
        # with optional arguments.
        twoD.AddAlphaObj('QCD',f,qcd_f,title='NTMJ')

        qcd_p = qcd_f.Multiply(fail_name.replace('Fail','Pass'), qcd_rpf)
        twoD.AddAlphaObj('QCD', p, qcd_p, title='NTMJ')

    # save the workspace!
    twoD.Save()

def ML_fit(signal):
    '''
    signal [str] = any of the signal masses, as a string. 
    Masses range from [1400,4000], at 200 GeV intervals

    Loads a TwoDAlphabet object from an existing project area, selects
    a subset of objects to run over (a specific signal and TF), makes a sub-directory
    to store the information, and runs the fit in that sub-directory. To make clear
    when a directory/area is being specified vs when a signal is being selected,
    I've redundantly prepended the "subtag" argument with "_area".
    '''

    # the default workspace directory, created in make_workspace(), is called ttbarfits16_3x1/
    twoD = TwoDAlphabet(savedirname,json_file, loadPrevious=True)

    # Create a subset of the primary ledger using the select() method.
    # The select() method takes as a function as its first argument
    # and any args to pass to that function as the remiaining arguments
    # to select(). See _select_signal for how to construct the function.
    subset = twoD.ledger.select(_select_signal, 'signal{}'.format(signal))

    # Make card reads the ledger and creates a Combine card from it.
    # The second argument specifices the sub-directory to save the card in.
    # MakeCard() will also save the corresponding Ledger DataFrames as csvs
    # in the sub-directory for later reference/debugging. By default, MakeCard()
    # will reference the base.root workspace in the first level of the project directory
    # (../ relative to the card). However, one can specify another path if a different
    # workspace is desired. Additionally, a different dataset can be supplied via
    # toyData but this requires supplying almost the full Combine card line and
    # is reserved for quick hacks by those who are familiar with Combine cards.
    twoD.MakeCard(subset, 'ttbar-{}_area'.format(signal))

    # Run the fit! Will run in the area specified by the `subtag` (ie. sub-directory) argument
    # and use the card in that area. Via the cardOrW argument, a different card or workspace can be
    # supplied (passed to the -d option of Combine).
    twoD.MLfit('ttbar-{}_area'.format(signal),rMin=rmin,rMax=rmax,verbosity=0,extra=extra)
    
    print 'twoD.GetParamsOnMatch()'
    fitparams = twoD.GetParamsOnMatch(regex='', subtag='ttbar-{}_area'.format(signal), b_or_s='b')
    print 'ttbar_xsec', fitparams['ttbar_xsec']
    
    with open("fitparams.json", "w") as outfile: 
        json.dump(fitparams, outfile)
    
def plot_fit(signal):
    '''
    Plots the fits from ML_fit() using 2DAlphabet
    '''
    twoD = TwoDAlphabet(savedirname, json_file , loadPrevious=True)
    subset = twoD.ledger.select(_select_signal, 'signal{}'.format(signal))
    twoD.StdPlots('ttbar-{}_area'.format(signal), subset)
#     twoD.StdPlots('ttbar-{}_area'.format(signal), subset, prefit=True)

def perform_limit(signal):
    '''
    Perform a blinded limit. To be blinded, the Combine algorithm (via option `--run blind`)
    will create an Asimov toy dataset from the pre-fit model. Since the TF parameters are meaningless
    in our true "pre-fit", we need to load in the parameter values from a different fit so we have
    something reasonable to create the Asimov toy.
    '''
    # Returns a dictionary of the TF parameters with the names as keys and the post-fit values as dict values.
    twoD = TwoDAlphabet(savedirname, json_file , loadPrevious=True)

    # GetParamsOnMatch() opens up the workspace's fitDiagnosticsTest.root and selects the rratio for the background
    params_to_set = twoD.GetParamsOnMatch('rratio*', 'ttbar-{}_area'.format(signal), 'b')
    params_to_set = {k:v['val'] for k,v in params_to_set.items()}

    # The iterWorkspaceObjs attribute stores the key-value pairs in the JSON config
    # where the value is a list. This allows for later access like here so the user
    # can loop over the list values without worrying if the config has changed over time
    # (necessitating remembering that it changed and having to hard-code the list here).
    for signame in twoD.iterWorkspaceObjs['SIGNAME']:
        # signame is going too look like 16_<what we want> so drop the first three characters
        print ('Performing limit for %s'%signame)

        # Make a subset and card as in ML_fit()
        subset = twoD.ledger.select(_select_signal, signame)
        twoD.MakeCard(subset, signame+'_area')
        # Run the blinded limit with our dictionary of TF parameters
        # NOTE: we are running without blinding (blinding seems to cause an issue with the limit plotting script...)
        twoD.Limit(
             subtag=signame+'_area',
             blindData=False,
             verbosity=0,
             setParams=params_to_set,
             condor=False
         )
        
        
def GoF(signal, tf='', nToys=20, condor=False):
    '''
    Calculates the value of the saturated test statistic in data and compares to the 
    distribution obtained from 500 toys (by default).
    '''
    # Load an existing workspace for a given TF parameterization (e.g., 'tWfits_1x1')
    fitDir = savedirname
    twoD = TwoDAlphabet(fitDir, '{}/runConfig.json'.format(fitDir), loadPrevious=True)
    # Creates a Combine card if not already existing (it should exist if you've already fitted this workspace)
    if not os.path.exists(twoD.tag+'/'+'signal{}_area/card.txt'.format(signal)):
        print('{}/signal{}_area/card.txt does not exist, making card'.format(twoD.tag,signal))
        subset = twoD.ledger.select(_select_signal, 'signal{}'.format(signal), tf)
        twoD.MakeCard(subset, 'signal{}_area'.format(signal))

    # Now run Combine's Goodness of Fit method, either on Combine or locally. 
    if condor == False:
        twoD.GoodnessOfFit(
            'signal{}_area'.format(signal), ntoys=nToys, freezeSignal=0,
            condor=False
        )
	# Once finished, we can plot the results immediately from the output rootfile.
	plot_GoF(signal, tf, condor)
    else:
	# 500 (default) toys, split across 50 condor jobs
        twoD.GoodnessOfFit(
            'signal{}_area'.format(signal), ntoys=nToys, freezeSignal=0,
            condor=False, njobs=50
        )
	# If submitting GoF jobs on condor, you must first wait for them to finish before plotting. 
	print('Jobs successfully submitted - you can run plot_GoF after the jobs have finished running to plot results')
    
def doSignalInjection(signal, tf='', injectedAmount=2000.000, nToys=500, condor=False):
    '''
    Calculates the value of the saturated test statistic in data and compares to the 
    distribution obtained from 500 toys (by default).
    '''
    # Load an existing workspace for a given TF parameterization (e.g., 'tWfits_1x1')
    fitDir = savedirname
    twoD = TwoDAlphabet(fitDir, '{}/runConfig.json'.format(fitDir), loadPrevious=True)
    # Creates a Combine card if not already existing (it should exist if you've already fitted this workspace)
    if not os.path.exists(twoD.tag+'/'+'signal{}_area/card.txt'.format(signal)):
        print('{}/signal{}_area/card.txt does not exist, making card'.format(twoD.tag,signal))
        subset = twoD.ledger.select(_select_signal, 'signal{}'.format(signal), tf)
        twoD.MakeCard(subset, 'signal{}_area'.format(signal))

    # Now run Combine's Goodness of Fit method, either on Combine or locally. 
    if condor == False:
        twoD.SignalInjection(
            'signal{}_area'.format(signal), ntoys=nToys, injectAmount=injectedAmount,
            condor=False
        )
	# Once finished, we can plot the results immediately from the output rootfile.
    else:
	# 500 (default) toys, split across 50 condor jobs
        twoD.SignalInjection(
            'signal{}_area'.format(signal), ntoys=nToys, injectAmount=injectedAmount,
            condor=True, njobs=50
        )
	# If submitting GoF jobs on condor, you must first wait for them to finish before plotting. 
	print('Jobs successfully submitted - you can run plot_GoF after the jobs have finished running to plot results')
    
    
def plot_GoF(signal, tf='', condor=False):
    '''
    Plot the Goodness of Fit as the measured saturated test statistic in data 
    compared against the distribution obtained from the toys. 
    '''
    plot.plot_gof(savedirname, 'signal{}_area'.format(signal), condor=condor)

    
def plot_signalinjection(signal, tf='', injectedAmount=2000.000, nToys=500, condor=False):
    '''
    Plot the Goodness of Fit as the measured saturated test statistic in data 
    compared against the distribution obtained from the toys. 
    '''

#     plot.plot_signalInjection(savedirname, 'signal{}_area'.format(signal), condor=condor)
    plot.plot_signalInjection(savedirname, 'signal{}_area'.format(signal), injectedAmount=injectedAmount, seed=123456, stats=True, condor=False)
    
    
    
if __name__ == "__main__":
   
   make_workspace()
   

   if args.signal:
	print("Processing single signal: {}...".format(args.signal))
        process_signals([args.signal])

   elif args.senario_fit == 'RSGluon':
        print("Processing RSGluon signals...")
        RSGluon_signals = load_signals_from_json('jsons/signals.json', args.senario_fit)
        process_signals(RSGluon_signals)
   elif args.senario_fit == 'ZPrime':
        print("Processing ZPrime signals...")
        ZPrime_signals = load_signals_from_json('jsons/signals.json', args.senario_fit)
        process_signals(ZPrime_signals)
 


