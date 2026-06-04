# **TTbar Hadronic Background Estimation**

## **Requirements**
This directory requires the **2DAlphabet** and **TTbarAllHadUproot** packages to run. You can find instructions to run it [here](https://github.com/b2g-nano/TTbarAllHadUproot/tree/optimize). 

---

## **Setup Instructions**

1. **Set up CMSSW, Combine, CombineHarvester, and 2DAlphabet**

   Start from the directory where you want the CMSSW release area to live:

   ```bash
   cmsrel CMSSW_14_1_0_pre4
   cd CMSSW_14_1_0_pre4/src
   cmsenv

   git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
   cd HiggsAnalysis/CombinedLimit
   git fetch origin
   git checkout v10.0.1
   cd ../../

   git clone --branch CMSSW_14_1_0_pre4 git@github.com:JHU-Tools/CombineHarvester.git

   scramv1 b clean
   scramv1 b -j 4

   git clone git@github.com:JHU-Tools/2DAlphabet.git
   python3 -m virtualenv twoD-env
   source twoD-env/bin/activate
   cd 2DAlphabet/
   python setup.py develop
   ```

2. **Clone This Repository**  
   Clone the repository using:
   ```bash
   git clone --branch cmslpc-el9 git@github.com:mandalaritra1/bgestimation.git
   ``` 

Alternatively, fork the repository first and then clone your fork:
```bash
git clone --branch cmslpc-el9 <your-fork-url>
```

## **Samples**

The 2DAlphabet input ROOT files needed for background estimation are located in:

```bash
/eos/user/a/amandal/ttbarhad_root_files/2dAlphabetInputs
```


## **Running Fits**

To obtain fit results for both central and forward categories for each year (2016, 2017, and 2018), simply run:

```bash
source run_fit.sh
```
This will execute the ttbar.py script for different scenarios. You can choose to run fits, limits, and goodness-of-fit (GOF) tests using the "--all" argument, or adjust the argument based on your needs.

Fit results for a given category will be stored under the "output/" directory.

For the 2024 single-year workflow, run central and forward with the 2024 inputs and the transfer functions currently stored in `jsons/TransferFunctions.json`:

```bash
cd /uscms_data/d3/amandal2/bg_ttbar/CMSSW_14_1_0_pre4/src/bgestimation
LOCAL_INPUT="/eos/user/a/amandal/ttbarhad_root_files/2dAlphabetInputs"

python -u ttbar.py --cat cen2024 --senario RSGluon --input "$LOCAL_INPUT" --signal RSGluon4000 --study all 2>&1 | tee output_2024_cen_all.log
python -u ttbar.py --cat fwd2024 --senario RSGluon --input "$LOCAL_INPUT" --signal RSGluon4000 --study all 2>&1 | tee output_2024_fwd_all.log
```

If the fit/postfit plotting has already run and only the limit/GOF card directories are missing, run `--study limit` for each category instead of rerunning the full fit. The combined-card step below uses the plain `signalRSGluon4000_area/card.txt` cards made by `perform_limit`, not the `ttbar-signalRSGluon4000_area/card.txt` cards made by `ML_fit`.

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

For 2024, combine only central plus forward. After the `cen2024` and `fwd2024` `signalRSGluon4000_area/card.txt` files exist, run:

```bash
cd output/
source combine_cards24.sh
```

This reads `cen2024` and `fwd2024` from `../jsons/TransferFunctions.json`, writes `cards_combined_24/signalRSGluon4000_area/signalRSGluon4000_card_combined.txt`, builds a masked workspace, runs the blind saturated GOF with pass-region masks, collects the toys, and writes `gof_blind.json` plus `gof_plot_blind_2024.pdf/png`. Set `NTOYS` to override the default 200 toys, for example `NTOYS=50 source combine_cards24.sh` for a quick test.

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

For the 2024 combined central+forward card, first run the Combine limit inside the combined-card directory:

```bash
cd output/cards_combined_24/signalRSGluon4000_area
combineTool.py -M AsymptoticLimits -d signalRSGluon4000_card_combined.txt --run blind --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001 -v 0
```

Then plot from the `bgestimation` directory:

```bash
cd ../../..
python3 plot_limits.py --signal RSGluon --width "" --output limits --year 2024 --blind True
```

The `--run blind`/`--blind True` path gives expected-only limits and does not require unblinding. For observed limits, remove `--run blind` from the Combine command and use `--blind False` in `plot_limits.py`. A mass-limit crossing is only meaningful once the combined limit outputs exist for multiple signal masses; with only `RSGluon4000` present, the plot is a single available point/check.

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

For blinded 2024 impacts, use the combined 2024 workspace and keep `-t -1`:

```bash
cd output/cards_combined_24/signalRSGluon4000_area
combineTool.py -M Impacts -d workspace.root -m 4000 --doInitialFit --robustFit 1 --expectSignal=1 --rMin -1 --rMax 2 --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 -t -1
combineTool.py -M Impacts -d workspace.root -m 4000 --robustFit 1 --doFits --parallel 16 --expectSignal=1 --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rMin -1 --rMax 2 -t -1 --job-mode condor
combineTool.py -M Impacts -d workspace.root -m 4000 -o impacts_2024_blind.json
python ../../../remove_constraints.py -i impacts_2024_blind.json -o impacts_2024_blind.json
plotImpacts.py -i impacts_2024_blind.json -o impacts_2024_blind --units pb
```

For observed/unblinded impacts, build an unmasked workspace from `signalRSGluon4000_card_combined.txt`, use that workspace in the commands above, and remove `-t -1`.

### Transfer functions 

The transfer functions (TFs) are stored in `jsons/TransferFunctions.json`.

To re-determine them for the 2024 central and forward categories, first run the F-test fit scan:

```bash 
cd /uscms_data/d3/amandal2/bg_ttbar/CMSSW_14_1_0_pre4/src/bgestimation
LOCAL_INPUT="/eos/user/a/amandal/ttbarhad_root_files/2dAlphabetInputs"

python -u fit_ftest.py --preset 2024 --input "$LOCAL_INPUT" --signal RSGluon4000 2>&1 | tee output_ftest_2024.log
```

This runs `ttbar.py --study ftest` for the candidate transfer-function forms and writes the fit work areas under `ftest/`. To perform the F-test comparisons and plot the results, run:

```bash 
python -u results_ftest.py --preset 2024 --signal RSGluon4000 2>&1 | tee output_ftest_results_2024.log
```

All F-test summary CSVs and plots will be stored in the `ftest_results/` directory.






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
