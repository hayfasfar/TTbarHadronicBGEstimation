from time import time
import os
import sys
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball, cd, execute_cmd
from TwoDAlphabet.ftest import FstatCalc
import multiprocessing

# Default year is 2016, or use the one passed via command line argument
if (len(sys.argv) >= 1) and (sys.argv[1] in ['2016', '2017', '2018']):
    year = sys.argv[1]
else:
    year = '2016'

# Define regions and parameters
regions = ['cen', 'fwd']
params_list = ['0x0', '0x1', '0x2', '1x0', '1x1', '1x2', '2x1', '2x2']

def run_fits():
    for region in regions:
        # Construct the working directory for each region
        wdir = os.path.join('ftest',year, region)
        if not os.path.exists(wdir):
	   os.makedirs(wdir)
        print "output directory is:", wdir
        os.system('pwd')
        # Loop over the parameters and run the fit for each
        for i,params in enumerate(params_list):
            print "Running ftest for", region, year, "with params:", params
            cmd = (
                'nohup python ttbar.py '
                '--cat {}{} --tf {} --study ftest --scenario RSGluon '
                '--input /eos/home-h/hrejebsf/2Dalphabet_files/files_loosetomedium_Sep24 '
                '--output {} --signal RSGluon2000 > output{}.log 2>&1 &'
            ).format(region, year, params, wdir, i)
            os.system(cmd)

	run_fits()

