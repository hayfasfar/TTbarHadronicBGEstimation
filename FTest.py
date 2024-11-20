from time import time
import os
import sys

# Default year is 2016, or use the one passed via command line argument
if (len(sys.argv) >= 1) and (sys.argv[1] in ['2016', '2017', '2018']):
    year = sys.argv[1]
else:
    year = '2016'

# Define regions and parameters
regions = ['cen', 'fwd']
params_list = ['0x0', '0x1', '0x2', '1x0', '1x1', '1x2', '2x1', '2x2']

# Simplified function just to run the ftests and move files
def run_fits():
    for region in regions:
        # Construct the working directory for each region
        wdir = os.path.join('ftest',year, region)
        if not os.path.exists(wdir):
	   os.makedirs(wdir)


        print "output directory is:", wdir

        os.system('pwd')
        # Loop over the parameters and run the ftest for each
        for i,params in enumerate(params_list):
            print "Running ftest for", region, year, "with params:", params
            os.system('nohup python ttbar.py  --cat ' + region + year + ' --tf '+ params + ' --study ftest --senario RSGluon --input /eos/home-h/hrejebsf/2Dalphabet_files/files_loosetomedium_Sep24 --output '+str(wdir)+' --signal RSGluon2000 ' + '> output'+str(i)+'.log 2>&1 &' )


# Run the fits
run_fits()

