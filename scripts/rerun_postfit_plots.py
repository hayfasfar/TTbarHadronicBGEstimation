#!/usr/bin/env python3
"""Regenerate 2DAlphabet postfit plots from an existing fit directory.

This does not rerun Combine or rebuild the workspace. It reloads an existing
2DAlphabet output directory, applies plot-only options such as blindedPlots, and
reruns the StdPlots plotting step.
"""

import argparse
import os

from TwoDAlphabet.twoDalphabet import TwoDAlphabet


def signal_name(signal):
    if signal is None:
        return None
    return signal if signal.startswith("signal") else "signal" + signal


def select_signal(row, args):
    signame = args[0]
    if signame is None:
        return True
    if row.process_type == "SIGNAL":
        return signame in row.process
    return True


def infer_pass_regions(twoD):
    return [region for region in twoD.ledger.GetRegions() if "Pass" in region]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rerun only 2DAlphabet postfit plots, optionally blinding D/pass signal region data."
    )
    parser.add_argument(
        "savedir",
        help="2DAlphabet output directory, e.g. output/ttbarfits_fwd2024_1x1",
    )
    parser.add_argument(
        "--subtag",
        default="ttbar-signalRSGluon4000_area",
        help="Fit subdirectory containing fitDiagnosticsTest.root/card.txt.",
    )
    parser.add_argument(
        "--signal",
        default="RSGluon4000",
        help="Signal to keep in plot legends, e.g. RSGluon4000. Use --signal all to keep all signals.",
    )
    parser.add_argument(
        "--blind-region",
        action="append",
        default=[],
        help=(
            "Region to blind in plots, e.g. Fwd2024Pass or Cen2024Pass. "
            "Can be passed multiple times. Default: all Pass regions."
        ),
    )
    parser.add_argument(
        "--fit",
        choices=["b", "s", "both"],
        default="b",
        help="Which postfit plots to regenerate. Default: b.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run_config = os.path.join(args.savedir, "runConfig.json")
    if not os.path.exists(run_config):
        raise RuntimeError("Could not find {}".format(run_config))

    twoD = TwoDAlphabet(args.savedir, run_config, externalOpts={}, loadPrevious=True)
    blind_regions = args.blind_region or infer_pass_regions(twoD)

    # Re-create the object with plot blinding active. 2DAlphabet stores this in
    # options and the plotting code uses it when making postfit projections.
    twoD = TwoDAlphabet(
        args.savedir,
        run_config,
        externalOpts={"blindedPlots": blind_regions},
        loadPrevious=True,
    )

    signame = None if args.signal == "all" else signal_name(args.signal)
    ledger = twoD.ledger.select(select_signal, signame)

    print("savedir:", args.savedir)
    print("subtag:", args.subtag)
    print("blind plot regions:", ", ".join(blind_regions))
    print("signal selection:", "all" if signame is None else signame)
    print("fit plots:", args.fit)

    plot_splusb = args.fit in ["s", "both"]
    if args.fit == "b":
        twoD.StdPlots(args.subtag, ledger, plotSplusB=False)
    elif args.fit == "s":
        # StdPlots always makes b first when plotSplusB=True. Use the lower-level
        # plot call for s-only to avoid remaking b when explicitly requested.
        from TwoDAlphabet import plot
        from TwoDAlphabet.helpers import cd

        with cd(os.path.join(args.savedir, args.subtag)):
            plot.gen_post_fit_shapes()
            plot.gen_projections(ledger=ledger, twoD=twoD, fittag="s")
    else:
        twoD.StdPlots(args.subtag, ledger, plotSplusB=plot_splusb)


if __name__ == "__main__":
    main()
