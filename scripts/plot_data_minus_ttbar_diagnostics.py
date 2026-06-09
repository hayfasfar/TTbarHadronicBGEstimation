#!/usr/bin/env python3
"""Plot data - ttbar residual diagnostics from organized_hists.root."""

import argparse
import csv
import os
import re
from array import array

import ROOT


KEEPALIVE = []


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Make signed residual, pull, and 3D lego plots for data_obs - TTbar "
            "in the six 2DAlphabet regions."
        )
    )
    parser.add_argument("organized_hists", help="Path to organized_hists.root")
    parser.add_argument(
        "--prefix",
        default=None,
        help="Region prefix, e.g. Cen2024 or Fwd2024. Inferred if omitted.",
    )
    parser.add_argument(
        "--ttbar",
        default="24_TTbar",
        help="TTbar process name in organized_hists.root. Default: 24_TTbar",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help=(
            "Output directory. Default: "
            "<organized_hists dir>/data_minus_ttbar_diagnostics"
        ),
    )
    parser.add_argument(
        "--lumi",
        default="138 fb^{-1} (13 TeV)",
        help="Luminosity label drawn on the canvas.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of most negative bins to print in the text summary.",
    )
    return parser.parse_args()


def keep(obj):
    KEEPALIVE.append(obj)
    return obj


def infer_prefix(tfile):
    pattern = re.compile(r"^data_obs_(.+?)(Pass|Fail)_Region[0-2]$")
    prefixes = []
    for key in tfile.GetListOfKeys():
        match = pattern.match(key.GetName())
        if match:
            prefixes.append(match.group(1))
    prefixes = sorted(set(prefixes))
    if len(prefixes) != 1:
        raise RuntimeError(
            "Could not infer a unique region prefix. Found: {}. "
            "Pass --prefix explicitly.".format(prefixes)
        )
    return prefixes[0]


def get_hist(tfile, name):
    hist = tfile.Get(name)
    if not hist:
        raise RuntimeError("Missing histogram: {}".format(name))
    hist.SetDirectory(0)
    return hist


def make_residual(data, ttbar, name):
    residual = data.Clone(name)
    residual.SetDirectory(0)
    residual.Add(ttbar, -1.0)
    return residual


def make_pull(data, ttbar, name):
    pull = data.Clone(name)
    pull.SetDirectory(0)
    pull.Reset("ICES")
    for ix in range(1, data.GetNbinsX() + 1):
        for iy in range(1, data.GetNbinsY() + 1):
            diff = data.GetBinContent(ix, iy) - ttbar.GetBinContent(ix, iy)
            data_err = data.GetBinError(ix, iy)
            ttbar_err = ttbar.GetBinError(ix, iy)
            sigma2 = data_err * data_err + ttbar_err * ttbar_err
            if sigma2 <= 0.0:
                sigma2 = max(data.GetBinContent(ix, iy) + ttbar.GetBinContent(ix, iy), 1.0)
            pull.SetBinContent(ix, iy, diff / ROOT.TMath.Sqrt(sigma2))
            pull.SetBinError(ix, iy, 0.0)
    return pull


def make_signed_log(hist, name):
    signed_log = hist.Clone(name)
    signed_log.SetDirectory(0)
    for ix in range(1, signed_log.GetNbinsX() + 1):
        for iy in range(1, signed_log.GetNbinsY() + 1):
            value = signed_log.GetBinContent(ix, iy)
            if value > 0.0:
                value = ROOT.TMath.Log10(1.0 + value)
            elif value < 0.0:
                value = -ROOT.TMath.Log10(1.0 + abs(value))
            signed_log.SetBinContent(ix, iy, value)
            signed_log.SetBinError(ix, iy, 0.0)
    return signed_log


def axis_title(hist):
    xaxis = hist.GetXaxis()
    yaxis = hist.GetYaxis()
    xaxis.SetTitle("m_{t} [GeV]")
    yaxis.SetTitle("m_{t#bar{t}} [GeV]")
    xaxis.SetTitleSize(0.045)
    yaxis.SetTitleSize(0.045)
    xaxis.SetLabelSize(0.035)
    yaxis.SetLabelSize(0.035)


def set_symmetric_range(hist, floor=1.0):
    largest = 0.0
    for ix in range(1, hist.GetNbinsX() + 1):
        for iy in range(1, hist.GetNbinsY() + 1):
            largest = max(largest, abs(hist.GetBinContent(ix, iy)))
    largest = max(largest, floor)
    hist.SetMinimum(-largest)
    hist.SetMaximum(largest)
    return largest


def style_hist(hist, title, ztitle):
    hist.SetTitle(title)
    hist.SetStats(False)
    axis_title(hist)
    hist.GetZaxis().SetTitle(ztitle)
    hist.GetZaxis().SetTitleSize(0.040)
    hist.GetZaxis().SetLabelSize(0.032)
    hist.GetZaxis().SetTitleOffset(1.15)


def draw_header(canvas, prefix, lumi):
    canvas.cd()
    header = keep(ROOT.TLatex())
    header.SetNDC(True)
    header.SetTextFont(62)
    header.SetTextSize(0.030)
    header.DrawLatex(0.030, 0.975, "CMS")
    header.SetTextFont(52)
    header.SetTextSize(0.025)
    header.DrawLatex(0.075, 0.975, "Preliminary")
    header.SetTextFont(42)
    header.DrawLatex(0.390, 0.975, "{} data - t#bar{{t}} diagnostics".format(prefix))
    header.SetTextAlign(31)
    header.DrawLatex(0.985, 0.975, lumi)


def set_diverging_palette():
    """Use a blue-white-red palette where negative/positive are visually distinct."""
    stops = [0.00, 0.50, 1.00]
    red = [0.05, 1.00, 0.80]
    green = [0.20, 1.00, 0.05]
    blue = [0.75, 1.00, 0.05]
    n_contours = 255
    ROOT.TColor.CreateGradientColorTable(
        len(stops),
        array("d", stops),
        array("d", red),
        array("d", green),
        array("d", blue),
        n_contours,
    )
    ROOT.gStyle.SetNumberContours(n_contours)


def draw_grid(hists, output, prefix, lumi, draw_option, ztitle, is_lego=False):
    canvas = keep(ROOT.TCanvas(os.path.basename(output), "", 1700, 1050))
    canvas.SetMargin(0, 0, 0, 0)
    draw_header(canvas, prefix, lumi)
    canvas.Divide(3, 2, 0.002, 0.002)

    for idx, (region_name, hist) in enumerate(hists, start=1):
        canvas.cd(idx)
        pad = ROOT.gPad
        pad.SetLeftMargin(0.12)
        pad.SetRightMargin(0.15 if not is_lego else 0.08)
        pad.SetBottomMargin(0.12)
        pad.SetTopMargin(0.10)
        if is_lego:
            pad.SetTheta(28)
            pad.SetPhi(35)
        style_hist(hist, region_name, ztitle)
        hist.Draw(draw_option)

    for suffix in [".png", ".pdf"]:
        canvas.SaveAs(output + suffix)


def collect_bin_rows(region_name, data, ttbar, pull):
    rows = []
    for ix in range(1, data.GetNbinsX() + 1):
        for iy in range(1, data.GetNbinsY() + 1):
            data_value = data.GetBinContent(ix, iy)
            ttbar_value = ttbar.GetBinContent(ix, iy)
            diff = data_value - ttbar_value
            pull_value = pull.GetBinContent(ix, iy)
            rows.append(
                {
                    "region": region_name,
                    "ix": ix,
                    "iy": iy,
                    "mt_low": data.GetXaxis().GetBinLowEdge(ix),
                    "mt_high": data.GetXaxis().GetBinUpEdge(ix),
                    "mtt_low": data.GetYaxis().GetBinLowEdge(iy),
                    "mtt_high": data.GetYaxis().GetBinUpEdge(iy),
                    "data": data_value,
                    "ttbar": ttbar_value,
                    "data_minus_ttbar": diff,
                    "pull": pull_value,
                }
            )
    return rows


def write_csv(rows, path):
    fieldnames = [
        "region",
        "ix",
        "iy",
        "mt_low",
        "mt_high",
        "mtt_low",
        "mtt_high",
        "data",
        "ttbar",
        "data_minus_ttbar",
        "pull",
    ]
    with open(path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary(rows, path, top_n):
    negative = [row for row in rows if row["data_minus_ttbar"] <= 0.0]
    by_region = {}
    for row in rows:
        by_region.setdefault(row["region"], []).append(row)

    lines = []
    lines.append("data_obs - TTbar diagnostic summary")
    lines.append("")
    for region, region_rows in by_region.items():
        neg_rows = [row for row in region_rows if row["data_minus_ttbar"] <= 0.0]
        min_diff = min(region_rows, key=lambda row: row["data_minus_ttbar"])
        min_pull = min(region_rows, key=lambda row: row["pull"])
        lines.append(
            "{}: {} / {} bins non-positive".format(
                region, len(neg_rows), len(region_rows)
            )
        )
        lines.append(
            "  most negative diff: {data_minus_ttbar:.3f} in mt [{mt_low:.1f}, {mt_high:.1f}], "
            "mtt [{mtt_low:.1f}, {mtt_high:.1f}], data={data:.3f}, ttbar={ttbar:.3f}, "
            "pull={pull:.3f}".format(**min_diff)
        )
        lines.append(
            "  most negative pull: {pull:.3f} in mt [{mt_low:.1f}, {mt_high:.1f}], "
            "mtt [{mtt_low:.1f}, {mtt_high:.1f}], data={data:.3f}, ttbar={ttbar:.3f}, "
            "diff={data_minus_ttbar:.3f}".format(**min_pull)
        )
        lines.append("")

    lines.append("Most negative bins by data - TTbar")
    for row in sorted(negative, key=lambda item: item["data_minus_ttbar"])[:top_n]:
        lines.append(
            "  {region:22s} mt [{mt_low:6.1f}, {mt_high:6.1f}] "
            "mtt [{mtt_low:6.1f}, {mtt_high:6.1f}] "
            "data={data:8.3f} ttbar={ttbar:8.3f} diff={data_minus_ttbar:9.3f} "
            "pull={pull:7.3f}".format(**row)
        )

    lines.append("")
    lines.append("Most negative bins by pull")
    for row in sorted(negative, key=lambda item: item["pull"])[:top_n]:
        lines.append(
            "  {region:22s} mt [{mt_low:6.1f}, {mt_high:6.1f}] "
            "mtt [{mtt_low:6.1f}, {mtt_high:6.1f}] "
            "data={data:8.3f} ttbar={ttbar:8.3f} diff={data_minus_ttbar:9.3f} "
            "pull={pull:7.3f}".format(**row)
        )

    with open(path, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    args = parse_args()
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPaintTextFormat(".1f")
    set_diverging_palette()

    tfile = ROOT.TFile.Open(args.organized_hists)
    if not tfile or tfile.IsZombie():
        raise RuntimeError("Could not open {}".format(args.organized_hists))

    prefix = args.prefix or infer_prefix(tfile)
    output_dir = args.output_dir or os.path.join(
        os.path.dirname(args.organized_hists), "data_minus_ttbar_diagnostics"
    )
    os.makedirs(output_dir, exist_ok=True)

    residual_hists = []
    signed_log_hists = []
    pull_hists = []
    all_rows = []
    states = ["Fail", "Pass"]
    regions = ["Region0", "Region1", "Region2"]
    for state in states:
        for region in regions:
            region_name = "{}{}_{}".format(prefix, state, region)
            data = get_hist(tfile, "data_obs_" + region_name)
            ttbar = get_hist(tfile, "{}_{}".format(args.ttbar, region_name))
            residual = keep(make_residual(data, ttbar, "residual_" + region_name))
            signed_log = keep(make_signed_log(residual, "signed_log_residual_" + region_name))
            pull = keep(make_pull(data, ttbar, "pull_" + region_name))
            set_symmetric_range(residual)
            set_symmetric_range(signed_log)
            set_symmetric_range(pull)
            residual_hists.append((region_name, residual))
            signed_log_hists.append((region_name, signed_log))
            pull_hists.append((region_name, pull))
            all_rows.extend(collect_bin_rows(region_name, data, ttbar, pull))

    draw_grid(
        residual_hists,
        os.path.join(output_dir, "residual_heatmap_grid"),
        prefix,
        args.lumi,
        "COLZ TEXT",
        "data - t#bar{t}",
    )
    draw_grid(
        signed_log_hists,
        os.path.join(output_dir, "residual_signed_log_heatmap_grid"),
        prefix,
        args.lumi,
        "COLZ TEXT",
        "sign(#Delta) log_{10}(1+|#Delta|)",
    )
    draw_grid(
        pull_hists,
        os.path.join(output_dir, "pull_heatmap_grid"),
        prefix,
        args.lumi,
        "COLZ TEXT",
        "(data - t#bar{t}) / #sigma",
    )
    draw_grid(
        residual_hists,
        os.path.join(output_dir, "residual_lego_grid"),
        prefix,
        args.lumi,
        "LEGO2Z",
        "data - t#bar{t}",
        is_lego=True,
    )

    csv_path = os.path.join(output_dir, "data_minus_ttbar_bins.csv")
    summary_path = os.path.join(output_dir, "summary.txt")
    write_csv(all_rows, csv_path)
    write_summary(all_rows, summary_path, args.top_n)
    print("Wrote {}".format(output_dir))
    print("Summary: {}".format(summary_path))
    print("Bins: {}".format(csv_path))


if __name__ == "__main__":
    main()
