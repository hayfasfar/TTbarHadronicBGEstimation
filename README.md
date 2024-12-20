# **TTbar Hadronic Background Estimation**

## **Requirements**
This directory requires the **2DAlphabet** and **TTbarAllHadUproot** packages to run. You can find instructions to run it [here](https://github.com/b2g-nano/TTbarAllHadUproot/tree/optimize). 

---

## **Setup Instructions**

1. **Install the 2DAlphabet Package**  
   Follow the instructions provided in the 2DAlphabet package repository to install it.

2. **Clone This Repository**  
   Clone the repository using:
   ```bash
   git clone git@github.com:hayfasfar/TTbarHadronicBGEstimation.git
   ``` 

Alternatively, fork the repository first and then clone your fork:
```bash
git clone <your-fork-url>
```

## **Samples**

All samples needed for background estimation are located in the following directory: 

Per year 
```bash

/eos/home-h/hrejebsf/2Dalphabet_files/files_loosetomedium_Sep24
```
Combined run2 :
```bash
/eos/home-h/hrejebsf/2Dalphabet_files/combined_run2_files
```


## **Running Fits**

To obtain fit results for both central and forward categories for each year (2016, 2017, and 2018), simply run:

```bash
source run_fit.sh
```
This will execute the ttbar.py script for different scenarios. You can choose to run fits, limits, and goodness-of-fit (GOF) tests using the "--all" argument, or adjust the argument based on your needs.

Fit results for a given category will be stored under the "output/" directory.

### Combining datacards

To combine cards for a specific year:

```bash
cd output/
source combined_cards16.sh
source combined_cards17.sh
source combined_cards18.sh
```
Once these cards are combined, you can run the Run-2 combination using:

```bash 
source combined_cards_run2.sh
```
### Goodness of fit (GOF) 

These are run2 GOF command, to run it on a specific category or year please change the card  accordingly. 

Blind : 

```bash
1- text2workspace.py  output/cards_combined_run2/signalRSGluon2000_area/signalRSGluon2000_card_combined.txt  -o workspace.root --channel-masks 
2- combineTool.py -M GoodnessOfFit -d workspace.root --algo saturated -n _blind  -m 2000 --setParameterRanges r=-5.0,5.0  --setParameters mask_Name1_Name1_cen16Pass_SIG=1,mask_Name1_Name2_fwd16Pass_SIG=1,mask_Name2_Name1_cen17Pass_SIG=1,mask_Name2_Name2_fwd17Pass_SIG=1,mask_Name3_Name1_cen18Pass_SIG=1,mask_Name3_Name2_fwd18Pass_SIG=1
3- combineTool.py -M GoodnessOfFit -d workspace.root --algo saturated -n _blind  -m 2000 --setParameterRanges r=-5.0,5.0 --toysFreq -t 200 -s -1 --setParameterRanges r=-5.0,5.0  -setParameters mask_Name1_Name1_cen16Pass_SIG=1,mask_Name1_Name2_fwd16Pass_SIG=1,mask_Name2_Name1_cen17Pass_SIG=1,mask_Name2_Name2_fwd17Pass_SIG=1,mask_Name3_Name1_cen18Pass_SIG=1,mask_Name3_Name2_fwd18Pass_SIG=1
4- combineTool.py -M CollectGoodnessOfFit --input higgsCombine_blind.GoodnessOfFit.mH2000.root higgsCombine_blind.GoodnessOfFit.mH2000.969972814.root -m 2000 -o gof_blind.json
5- plotGof.py gof_blind.json --statistic saturated --mass 2000.0 -o gof_plot_blind_run2 --title-right="Combined run2 blind"
```

Unblind: 
```bash
1- text2workspace.py  output/cards_combined_run2/signalRSGluon2000_area/signalRSGluon2000_card_combined.txt  -o workspace.root
2- combineTool.py -M GoodnessOfFit -d workspace.root --algo saturated -n _unblind  -m 2000 --setParameterRanges r=-5.0,5.0
3- combineTool.py -M GoodnessOfFit -d workspace.root --algo saturated -n _unblind  -m 2000 --setParameterRanges r=-5.0,5.0 --toysFreq -t 200 -s -1 
4- combineTool.py -M CollectGoodnessOfFit --input higgsCombine_unblind.GoodnessOfFit.mH2000.root higgsCombine_unblind.GoodnessOfFit.mH2000.969972814.root -m 2000 -o gof_unblind.json
5- plotGof.py gof_unblind.json --statistic saturated --mass 2000.0 -o gof_plot_unblind_run2 --title-right="Combined run2 unblind"
```
### Fit Diagnostics 
Run the Fit diagnostics to check the sanity of the fit and systematic uncertainties: you can do it per category, per year or for combined run2:
Example using combined 2017 i.e central and forward 2017 combined categories: 
```bash 
text2workspace.py  output/cards_combined_17/signalRSGluon2000_area/signalRSGluon2000_card.txt  -o workspace.root
combine -M FitDiagnostics workspace.root -m 1 --rMin -1 --rMax 2 --saveShapes --saveWithUncertainties -n .combined2017
```

### Limits 
To plot limits run the following command: 
```bash 
python plot_limits.py --signal RSGluon --width ""  --output limits --year run2  
```
this will plot unblinded limits if you want blind ones you should add the option --blind True 

### Impact plot

To get Run2 Impact plot run the following command lines, if you want to run it only for one year, consider changing the datacard accordingly. For unblinded Impact remove -t -1 : 
```bash
text2workspace.py  output/cards_combined_run2/signalRSGluon2000_area/signalRSGluon2000_card_combined.txt  -o workspace.root
combineTool.py -M Impacts -d workspace.root -m 2000 --doInitialFit --robustFit 1 --expectSignal=1 --rMin -1 --rMax 2  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  -t -1 
combineTool.py -M Impacts -d workspace.root -m 2000 --robustFit 1 --doFits --parallel 16 --expectSignal=1 --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rMin -1 --rMax 2 -t -1  --job-mode condor
combineTool.py -M Impacts -d workspace.root -m 2000  -o impacts.json
plotImpacts.py -i impacts.json -o impacts  --units pb
```
To remove QCD bins from the impact plot for visualisation purpose, you can do this before plotting it: 
```bash
python remove_constraints.py -i impact.json -o impact.json
```

### Transfer functions 

The transfer functions (TFs) are stored in jsons/TransferFunctions.json. If you need to re-determine them, first run:

```bash 

python fit_ftest.py
```
This will perform the fit using different transfer functions. To perform an F-test and plot the results second run:

```bash 
python results_ftest.py
```
All F-test results will be stored in the "ftest_results/" directory.






## Running all years combined

To run on all years/eras combined, you can go to the directory where your histograms are and execute: 

```
source rename_all_hists.sh
source hadd_files.sh
```

Then you can execute

```
nohup python ttbar.py --cat cenComb --senario RSGluon --input /afs/cern.ch/user/s/srappocc/TTBarRes/CMSSW_10_6_14/src/TTbarHadronicBGEstimation/files_loosetomedium_Sep24_Comb --signal RSGluon2000 > output1.log 2>&1 &
nohup python ttbar.py --cat cenFwd --senario RSGluon --input /afs/cern.ch/user/s/srappocc/TTBarRes/CMSSW_10_6_14/src/TTbarHadronicBGEstimation/files_loosetomedium_Sep24_Comb --signal RSGluon2000 > output1.log 2>&1 &
```
