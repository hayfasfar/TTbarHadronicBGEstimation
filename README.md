# **TTbar Hadronic Background Estimation**

## **Requirements**
This directory requires the **2DAlphabet** package to run. You can find it [here](<Add link>).

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

Coming soon

### Fit Diagnostics 
Run the Fit diagnostics to check the sanity of the fit and systematic uncertainties: you can do it per category, per year or for combined run2:
Example using combined 2017 i.e central and forward 2017 combined categories: 
```bash 
text2workspace.py  output/cards_combined_17/signalRSGluon2000_area/signalRSGluon2000_card.txt  -o workspace.root
combine -M FitDiagnostics workspace.root -m 1 --rMin -1 --rMax 2 --saveShapes --saveWithUncertainties -n .combined2017
```
### Impact plot

To get Run2 Impact plot run the following command lines, if you want to run it only for one year, consider changing the datacard accordingly. For unblinded Impact remove -t -1 : 
```bash
text2workspace.py  output/cards_combined_run2/signalRSGluon2000_area/signalRSGluon2000_card_combined.txt  -o workspace.root
combineTool.py -M Impacts -d workspace.root -m 1 --doInitialFit --robustFit 1 --expectSignal=1 --rMin -1 --rMax 2 -t -1  --job-mode condor 
combineTool.py -M Impacts -d workspace.root -m 1 --robustFit 1 --doFits --parallel 16 --expectSignal=1  --rMin -1 --rMax 2 -t -1  --job-mode condor
combineTool.py -M Impacts -d workspace.root -m 1 -o impacts.json
plotImpacts.py -i impacts.json -o impacts  --units pb
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
