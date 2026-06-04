#!/usr/bin/env bash
set -euo pipefail

# LPC access to CERNBox EOS.
BASE_INPUT="/eos/user/a/amandal/ttbarhad_root_files/2dAlphabetInputs"

run_fit() {
  local cat="$1"
  local log="$2"

  python -u ttbar.py --cat "${cat}" --senario RSGluon --input "${BASE_INPUT}" --signal RSGluon4000 2>&1 \
    | tee "${log}" \
    | sed "s/^/[${cat}] /"
}

run_fit cen2024 output_2024_cen.log &
cen_pid=$!

run_fit fwd2024 output_2024_fwd.log &
fwd_pid=$!

wait "${cen_pid}" "${fwd_pid}"
