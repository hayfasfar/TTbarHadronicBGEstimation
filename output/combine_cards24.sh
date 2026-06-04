#!/bin/sh

set -e

dir=$PWD
savedir=cards_combined_24
signal=RSGluon4000
mass=4000
ntoys=${NTOYS:-200}

tag0=$(jq -r '.cen2024' ../jsons/TransferFunctions.json)
tag1=$(jq -r '.fwd2024' ../jsons/TransferFunctions.json)

card_cen=$dir/ttbarfits_cen2024_$tag0/signal${signal}_area/card.txt
card_fwd=$dir/ttbarfits_fwd2024_$tag1/signal${signal}_area/card.txt
outdir=$dir/$savedir/signal${signal}_area
combined_card=$outdir/signal${signal}_card_combined.txt

if [ ! -f "$card_cen" ]; then
  echo "Missing central card: $card_cen"
  echo "Run ttbar.py with --study limit or --study all for cen2024 first."
  exit 1
fi

if [ ! -f "$card_fwd" ]; then
  echo "Missing forward card: $card_fwd"
  echo "Run ttbar.py with --study limit or --study all for fwd2024 first."
  exit 1
fi

mkdir -p "$outdir"

echo "Combining 2024 cards"
echo "  cen2024 TF: $tag0"
echo "  fwd2024 TF: $tag1"
combineCards.py \
  cen="$card_cen" \
  fwd="$card_fwd" \
  > "$combined_card"

cd "$outdir"

echo "Building masked workspace"
text2workspace.py "signal${signal}_card_combined.txt" -o workspace.root --channel-masks

echo "Finding pass-region masks"
masks=$(python -c 'import ROOT
f = ROOT.TFile("workspace.root")
w = f.Get("w")
items = []
for v in ROOT.RooArgList(w.allVars()):
    name = v.GetName()
    if name.startswith("mask_") and "Pass" in name:
        items.append(name + "=1")
print(",".join(items))')

if [ -z "$masks" ]; then
  echo "Could not find pass-region channel masks in workspace.root"
  exit 1
fi

echo "Using masks: $masks"

echo "Running blind GOF on data"
combineTool.py -M GoodnessOfFit -d workspace.root --algo saturated -n _blind -m "$mass" \
  --setParameterRanges r=-5.0,5.0 \
  --setParameters "$masks"

echo "Running blind GOF toys: $ntoys"
combineTool.py -M GoodnessOfFit -d workspace.root --algo saturated -n _blind -m "$mass" \
  --setParameterRanges r=-5.0,5.0 \
  --toysFreq -t "$ntoys" -s -1 \
  --setParameters "$masks"

echo "Collecting blind GOF"
combineTool.py -M CollectGoodnessOfFit \
  --input higgsCombine_blind.GoodnessOfFit.mH${mass}.root higgsCombine_blind.GoodnessOfFit.mH${mass}.*.root \
  -m "$mass" -o gof_blind.json

echo "Plotting blind GOF"
plotGof.py gof_blind.json --statistic saturated --mass "${mass}.0" \
  -o gof_plot_blind_2024 --title-right="2024 blind"

echo "DONE"
