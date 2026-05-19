#!/usr/bin/env python3
"""Plot data, ttbar, and data-ttbar for the six 2DAlphabet regions."""

import argparse
import os
import re

import ROOT


KEEPALIVE = []


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Make a 2x3 PNG grid from organized_hists.root. Each cell shows "
            "data_obs and TTbar projected onto m_tt, with data-TTbar below."
        )
    )
    parser.add_argument("organized_hists", help="Path to organized_hists.root")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output PNG path. Default: <organized_hists dir>/data_ttbar_grid.png",
    )
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
        "--lumi",
        default="138 fb^{-1} (13 TeV)",
        help="Luminosity label drawn on the canvas.",
    )
    parser.add_argument(
        "--logy",
        action="store_true",
        help="Use log scale in the main panels.",
    )
    parser.add_argument(
        "--signed-log-residual",
        action="store_true",
        help=(
            "Draw the bottom panel as sign(Data-TTbar)*log10(1+abs(Data-TTbar)). "
            "A normal log axis cannot show negative values."
        ),
    )
    parser.add_argument(
        "--print-nonpositive-2d",
        action="store_true",
        help="Print 2D bins where data_obs - TTbar <= 0 before projection.",
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


def project_mtt(hist, name):
    if hist.InheritsFrom("TH2"):
        proj = hist.ProjectionY(name, 1, hist.GetNbinsX(), "e")
    else:
        proj = hist.Clone(name)
    proj.SetDirectory(0)
    return proj


def region_label(hist):
    if not hist.InheritsFrom("TH2"):
        return ""
    axis = hist.GetXaxis()
    lo = axis.GetBinLowEdge(1)
    hi = axis.GetBinUpEdge(axis.GetNbins())
    return "{:g} < m_{{t}} [GeV] < {:g}".format(lo, hi)


def style_data(hist):
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(0.75)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetLineWidth(1)


def style_ttbar(hist):
    hist.SetLineColor(ROOT.kRed + 1)
    hist.SetFillColorAlpha(ROOT.kRed, 0.30)
    hist.SetLineWidth(2)


def style_residual(hist):
    hist.SetLineColor(ROOT.kGray + 2)
    hist.SetFillColor(ROOT.kGray + 1)
    hist.SetMarkerStyle(0)


def print_nonpositive_2d(region_name, data, ttbar):
    bad = []
    for ix in range(1, data.GetNbinsX() + 1):
        for iy in range(1, data.GetNbinsY() + 1):
            data_value = data.GetBinContent(ix, iy)
            ttbar_value = ttbar.GetBinContent(ix, iy)
            diff = data_value - ttbar_value
            if diff <= 0:
                bad.append(
                    (
                        ix,
                        iy,
                        data.GetXaxis().GetBinLowEdge(ix),
                        data.GetXaxis().GetBinUpEdge(ix),
                        data.GetYaxis().GetBinLowEdge(iy),
                        data.GetYaxis().GetBinUpEdge(iy),
                        data_value,
                        ttbar_value,
                        diff,
                    )
                )

    print("\n{}: {} bins with data_obs - TTbar <= 0".format(region_name, len(bad)))
    print("  ix iy  mt_low mt_high  mtt_low mtt_high  data  ttbar  data-ttbar")
    for row in bad:
        print(
            "  {:2d} {:2d}  {:7.1f} {:7.1f}  {:7.1f} {:7.1f}  {:8.3f} {:8.3f} {:9.3f}".format(
                *row
            )
        )


def max_for(data, ttbar):
    ymax = max(data.GetMaximum(), ttbar.GetMaximum())
    return ymax * 1.35 if ymax > 0 else 1.0


def residual_range(residual):
    largest = 0.0
    for ibin in range(1, residual.GetNbinsX() + 1):
        largest = max(largest, abs(residual.GetBinContent(ibin)))
    return max(1.0, 1.25 * largest)


def signed_log_transform(hist):
    for ibin in range(1, hist.GetNbinsX() + 1):
        value = hist.GetBinContent(ibin)
        if value > 0:
            hist.SetBinContent(ibin, ROOT.TMath.Log10(1.0 + value))
        elif value < 0:
            hist.SetBinContent(ibin, -ROOT.TMath.Log10(1.0 + abs(value)))
        else:
            hist.SetBinContent(ibin, 0.0)
        hist.SetBinError(ibin, 0.0)


def make_cell(
    canvas,
    idx,
    x1,
    y1,
    x2,
    y2,
    data,
    ttbar,
    title,
    draw_legend=False,
    logy=False,
    signed_log_residual=False,
):
    canvas.cd()
    main = keep(ROOT.TPad("main_{}".format(idx), "", x1, y1 + 0.28 * (y2 - y1), x2, y2))
    sub = keep(ROOT.TPad("sub_{}".format(idx), "", x1, y1, x2, y1 + 0.28 * (y2 - y1)))

    left = 0.15 if idx % 3 == 0 else 0.08
    right = 0.04
    main.SetLeftMargin(left)
    main.SetRightMargin(right)
    main.SetBottomMargin(0.02)
    main.SetTopMargin(0.12)
    sub.SetLeftMargin(left)
    sub.SetRightMargin(right)
    sub.SetTopMargin(0.02)
    sub.SetBottomMargin(0.34)
    if logy:
        main.SetLogy()

    main.Draw()
    sub.Draw()

    main.cd()
    frame = keep(data.Clone("frame_{}".format(idx)))
    frame.Reset("ICES")
    frame.SetTitle("")
    frame.SetStats(False)
    frame.GetXaxis().SetLabelSize(0)
    frame.GetYaxis().SetTitle("Events / bin")
    frame.GetYaxis().SetTitleSize(0.07)
    frame.GetYaxis().SetLabelSize(0.055)
    frame.GetYaxis().SetTitleOffset(0.85 if idx % 3 == 0 else 0.55)
    frame.SetMaximum(max_for(data, ttbar))
    frame.SetMinimum(0.1 if logy else 0.0)
    frame.Draw("hist")
    ttbar.Draw("hist same")
    data.Draw("ep same")

    text = keep(ROOT.TLatex())
    text.SetNDC(True)
    text.SetTextFont(42)
    text.SetTextSize(0.06)
    text.DrawLatex(0.18, 0.82, title)

    if draw_legend:
        legend = keep(ROOT.TLegend(0.58, 0.62, 0.94, 0.88))
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)
        legend.SetTextSize(0.055)
        legend.AddEntry(data, "Data", "ep")
        legend.AddEntry(ttbar, "t#bar{t}", "f")
        legend.Draw()

    sub.cd()
    resid = keep(data.Clone("data_minus_ttbar_{}".format(idx)))
    resid.Add(ttbar, -1.0)
    if signed_log_residual:
        signed_log_transform(resid)
    style_residual(resid)
    resid.SetTitle("")
    resid.SetStats(False)
    if signed_log_residual:
        resid.GetYaxis().SetTitle("signed log_{10}(1+|#Delta|)")
    else:
        resid.GetYaxis().SetTitle("Data - t#bar{t}")
    resid.GetYaxis().SetTitleSize(0.12)
    resid.GetYaxis().SetLabelSize(0.10)
    resid.GetYaxis().SetTitleOffset(0.45 if idx % 3 == 0 else 0.30)
    resid.GetYaxis().SetNdivisions(405)
    resid.GetXaxis().SetTitle("m_{t#bar{t}} [GeV]")
    resid.GetXaxis().SetTitleSize(0.13)
    resid.GetXaxis().SetLabelSize(0.11)
    rmax = residual_range(resid)
    resid.SetMinimum(-rmax)
    resid.SetMaximum(rmax)
    resid.Draw("hist")

    line = keep(ROOT.TLine(resid.GetXaxis().GetXmin(), 0.0, resid.GetXaxis().GetXmax(), 0.0))
    line.SetLineColor(ROOT.kBlack)
    line.SetLineWidth(1)
    line.Draw("same")


def main():
    args = parse_args()
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)

    tfile = ROOT.TFile.Open(args.organized_hists)
    if not tfile or tfile.IsZombie():
        raise RuntimeError("Could not open {}".format(args.organized_hists))

    prefix = args.prefix or infer_prefix(tfile)
    output = args.output or os.path.join(
        os.path.dirname(args.organized_hists), "data_ttbar_grid.png"
    )

    canvas = keep(ROOT.TCanvas("data_ttbar_grid", "", 1500, 950))
    canvas.SetMargin(0, 0, 0, 0)

    header = keep(ROOT.TLatex())
    header.SetNDC(True)
    header.SetTextFont(62)
    header.SetTextSize(0.030)
    header.DrawLatex(0.035, 0.975, "CMS")
    header.SetTextFont(52)
    header.SetTextSize(0.025)
    header.DrawLatex(0.081, 0.975, "Preliminary")
    header.SetTextFont(42)
    header.SetTextAlign(31)
    header.DrawLatex(0.985, 0.975, args.lumi)
    header.SetTextAlign(11)
    header.DrawLatex(0.43, 0.975, "{} data vs t#bar{{t}}".format(prefix))

    x_edges = [0.02, 0.345, 0.67, 0.995]
    y_edges = [0.03, 0.49, 0.95]
    states = ["Fail", "Pass"]
    regions = ["Region0", "Region1", "Region2"]

    idx = 0
    for row, state in enumerate(states):
        y1 = y_edges[1 - row]
        y2 = y_edges[2 - row]
        for col, region in enumerate(regions):
            reg_name = "{}{}_{}".format(prefix, state, region)
            data2d = get_hist(tfile, "data_obs_" + reg_name)
            ttbar2d = get_hist(tfile, "{}_{}".format(args.ttbar, reg_name))
            if args.print_nonpositive_2d:
                print_nonpositive_2d(reg_name, data2d, ttbar2d)
            data = keep(project_mtt(data2d, "proj_data_{}".format(reg_name)))
            ttbar = keep(project_mtt(ttbar2d, "proj_ttbar_{}".format(reg_name)))
            style_data(data)
            style_ttbar(ttbar)
            title = "{} {}  {}".format(state, region.replace("Region", "R"), region_label(data2d))
            make_cell(
                canvas,
                idx,
                x_edges[col],
                y1,
                x_edges[col + 1],
                y2,
                data,
                ttbar,
                title,
                draw_legend=(idx == 2),
                logy=args.logy,
                signed_log_residual=args.signed_log_residual,
            )
            idx += 1

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    canvas.SaveAs(output)
    print("Wrote {}".format(output))


if __name__ == "__main__":
    main()
