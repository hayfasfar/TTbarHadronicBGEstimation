# 2024 BG Estimation Debug Notes

## Context

This directory is the standalone `bgestimation` / 2DAlphabet layer for the `ttbarhadronic` all-hadronic boosted `ttbar` resonance workflow.

The 2024 test target is nominal-only:

- category configs: `jsons/config/ttbar_cen2024.json`, `jsons/config/ttbar_fwd2024.json`
- transfer-function map: `jsons/TransferFunctions.json`
- signal being tested: `RSGluon4000`
- input path used:

```bash
BASE_INPUT="root://eosuser.cern.ch//eos/user/a/amandal/ttbarhad_root_files/2dAlphabetInputs"
```

Main run commands:

```bash
python ttbar.py --cat fwd2024 --senario RSGluon --input "$BASE_INPUT" --signal RSGluon4000
python ttbar.py --cat cen2024 --senario RSGluon --input "$BASE_INPUT" --signal RSGluon4000
```

## Important Code/Config Changes Made

### 1. 2024 Region Names

The input ROOT files contain histograms with capitalized/full-year names:

```text
MttvsMtCen2024Pass
MttvsMtCen2024Fail
MttvsMtFwd2024Pass
MttvsMtFwd2024Fail
```

The 2024 JSON configs originally used names like `cen24Pass`, which caused ROOT `Get(...)` to return a null object and crash at `template.SetDirectory(0)`.

Updated:

```text
jsons/config/ttbar_cen2024.json:
  cen24Pass -> Cen2024Pass
  cen24Fail -> Cen2024Fail

jsons/config/ttbar_fwd2024.json:
  fwd24Pass -> Fwd2024Pass
  fwd24Fail -> Fwd2024Fail
```

### 2. Single-Signal Workspace

`ttbar.py` used to load all RSGluon signals into the workspace even when `--signal RSGluon4000` was passed. This made it look for missing files such as:

```text
TTbarAllHad24_signalRSGluon1000.root
```

Changed in `ttbar.py`:

```python
signals = [signal_name(args.signal)] if args.signal else load_signals_from_json('jsons/signals.json', senario)
```

This makes `--signal RSGluon4000` only request:

```text
TTbarAllHad24_signalRSGluon4000.root
```

### 3. Central Fit Signal Strength Range

For debugging central failures, `ttbar.py` was changed from:

```python
rmin = -6
rmax = 6
```

to:

```python
rmin = 0
rmax = 6
```

This confirmed that allowing negative `r` was not the only cause of the central failure.

## Forward 2024 Result

Forward category ran successfully with:

```bash
python ttbar.py --cat fwd2024 --senario RSGluon --input "$BASE_INPUT" --signal RSGluon4000
```

Output:

```text
output/ttbarfits_fwd2024_1x1/
```

Important products present:

```text
organized_hists.root
runConfig.json
base.root
binnings.p
ledger_*.csv/md
ttbar-signalRSGluon4000_area/
signalRSGluon4000_area/
```

Fit/plot products:

```text
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/FitDiagnostics.log
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/fitDiagnosticsTest.root
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/postfitshapes_b.root
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/postfitshapes_s.root
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/plots_fit_b/
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/plots_fit_s/
```

GOF/limit products:

```text
output/ttbarfits_fwd2024_1x1/signalRSGluon4000_area/higgsCombineTest.AsymptoticLimits.mH120.root
output/ttbarfits_fwd2024_1x1/signalRSGluon4000_area/gof_results.txt
output/ttbarfits_fwd2024_1x1/signalRSGluon4000_area/gof_plot.pdf
output/ttbarfits_fwd2024_1x1/signalRSGluon4000_area/gof_plot.png
```

GOF result observed:

```text
Test statistic in data = 236.51829020667356
Mean from toys = 169.30768174032164
Width from toys = 38.439693197801965
p-value = 0.04019143228286426
```

Forward fit had RooFit warnings about negative/underflow PDF evaluations but completed. Final reported best fit:

```text
Best fit r: -0.000442711  -0.00128598/+6.00044  (68% CL)
```

The forward postfit plots to inspect are mainly:

```text
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/plots_fit_b/postfit_projx.pdf
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/plots_fit_b/postfit_projy.pdf
output/ttbarfits_fwd2024_1x1/ttbar-signalRSGluon4000_area/plots_fit_b/base_figs/
```

`plots_fit_b` is background-only fit. `plots_fit_s` is signal-plus-background fit.

## Central 2024 Failure

Central was tested with several transfer functions:

```text
cen2024 = 1x1
cen2024 = 0x1
cen2024 = 0x0
```

All fail in the same family of errors.

Latest debug state:

```text
jsons/TransferFunctions.json: "cen2024": "0x0"
ttbar.py: rmin = 0, rmax = 6
```

Relevant latest log:

```text
log_cen2024_RSGluon4000_0x0_rmin0.txt
```

The first real failure is not the final Python traceback. The first real failure is Combine/RooFit:

```text
WARNING: underflow to 0 in pdf_binCen2024Pass_Region1_obsOnly for bin 52, weight 1
ERROR:Eval -- RooAbsReal::logEvalError(Cen2024Pass_Region1)
message: Number of events is negative or error
```

Then Combine cannot produce a valid background-only fit result, so 2DAlphabet crashes downstream:

```text
ValueError: Fit result "fit_b" does not exist in fit result file fitDiagnosticsTest.root
```

With `rMin = 0`, Combine command was:

```bash
combine -M FitDiagnostics card.txt --text2workspace "--channel-masks" --setParameters r=1 --saveWorkspace --cminDefaultMinimizerStrategy 0 --rMin 0 --rMax 6 -v 0 --robustFit=1
```

Best fit still pathological:

```text
Best fit r: 0.000498962  -0.000498962/+5.9995  (68% CL)
```

Conclusion so far:

- central failure is not primarily TF order, since `0x0` also fails
- central failure is not fixed by disallowing negative `r`
- issue localizes to `Cen2024Pass_Region1`
- `Region1` corresponds to the top-mass signal window:

```text
105 < m_t < 210 GeV
```

Likely causes:

1. negative/zero expected bin in the assembled model for `Cen2024Pass_Region1`
2. negative bin contents in one of the central input histograms
3. QCD construction from data/TTbar subtraction causing zero or negative bins
4. sparse bins in central pass top-window region
5. TTbar larger than data in some relevant bins, leading to negative QCD-like expectation

## Next Diagnostic To Run

Scan ROOT histograms for negative bins and for bins where `Data - TTbar <= 0`, especially in central top-window/pass.

Files to inspect:

```text
$BASE_INPUT/TTbarAllHad24_Data.root
$BASE_INPUT/TTbarAllHad24_TTbar.root
$BASE_INPUT/TTbarAllHad24_signalRSGluon4000.root
```

Histograms:

```text
MttvsMtCen2024Pass
MttvsMtCen2024Fail
```

Priority region:

```text
Cen2024Pass_Region1
105 < m_t < 210 GeV
```

The Combine log mentions failing bins like:

```text
pdf_binCen2024Pass_Region1_obsOnly bin 52
```

## Analysis Context From Wiki

The local wiki at `/mnt/extra/wsLinux/ai-wiki` says this is a boosted all-hadronic `ttbar` resonance search.

Core model:

```text
heavy resonance -> ttbar -> fully hadronic
boosted tops -> two AK8 top candidates
main observable -> m_ttbar
dominant background -> QCD multijet
background method -> 2DAlphabet pass/fail transfer function in mt vs m_tt
```

Region logic:

```text
pass / 2t:
  both selected AK8 candidates pass top tag

fail / antitag:
  leading/higher-score AK8 passes, other candidate lies in a looser fail window

central:
  |Delta y| < 1.0

forward:
  complement
```

Mass regions:

```text
Region0: low sideband, 25 < m_t < 105
Region1: top window, 105 < m_t < 210
Region2: high sideband, 210 < m_t < 475
```

QCD is estimated from data in the fail/antitag region after subtracting simulated SM `ttbar`, then transferred to pass using the fitted transfer function. SM `ttbar` remains MC-driven.

## Minor Notes

- `output_2024_fwd.log` was stale from an earlier failed nohup run and should not be used to judge the successful foreground forward run.
- Signal legend text still says `g_{RS} (2 TeV)` even for `RSGluon4000`; this appears to come from the config title and is just stale labeling.
- There are untracked/generated output directories and logs in the repo; do not treat git status noise as intentional source changes.
