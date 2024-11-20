from time import time
import os
import sys

# Default year is 2016, or use the one passed via command line argument
if (len(sys.argv) > 1) and (sys.argv[1] in ['2016', '2017', '2018']):
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
        wdir = os.path.join(year, region)

        # Construct the json file name
        #jsonfile = 'ttbar_' + region + year + '.json'

        print "Using JSON file:", jsonfile
        print "Changing directory to:", wdir

        # Change to the region's directory
        os.chdir(wdir)
        os.system('pwd')

        # Loop over the parameters and run the ftest for each
        for i,params in enumarate(params_list):
            print "Running ftest for", region, year, "with params:", params
            os.system('nohup python ../../ttbar.py  --cat ' + region + year + ' --tf'+ params + '--study ftest --senario RSGluon --path /eos/home-h/hrejebsf/2Dalphabet_files/files_loosetomedium_Sep24 --signal RSGluon2000 ' + '> output'+i+'.log 2>&1 &' )

            # Move only the ftest outputs to the 'ftests' folder
            os.system('mv *_ftest* ftests')

            # Optionally remove temporary files, like 'new.json'
            os.system('rm new.json')

        # After processing the region, go back to the parent directory
        os.chdir('../../')
        os.system('pwd')

# Run the fits
run_fits()

