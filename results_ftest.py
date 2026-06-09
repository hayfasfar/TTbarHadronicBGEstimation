#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1]
LOCAL_TWODALPHABET = SRC_DIR / '2DAlphabet'
if LOCAL_TWODALPHABET.exists():
    sys.path.insert(0, str(LOCAL_TWODALPHABET))

ROOT = None
TF1 = None
TH1F = None
TLegend = None
TPaveText = None
TLatex = None
TArrow = None
TCanvas = None
kBlue = None
gStyle = None
cd = None
execute_cmd = None
FstatCalc = None
TwoDAlphabet = None


DEFAULT_TFS = ['0x0', '0x1', '0x2', '1x0', '1x1', '1x2', '2x1', '2x2']
DEFAULT_REGIONS = ['cen', 'fwd']

N_PARAMS = {
    '0x0': 1,
    '0x1': 2,
    '1x0': 2,
    '0x2': 3,
    '2x0': 3,
    '1x1': 3,
    '0x3': 4,
    '2x1': 4,
    '1x2': 4,
    'sqrtexp': 4,
    '1x3': 5,
    '2x2': 5,
    '3x1': 5,
    'sqrtexplog': 5,
    '2x3': 6,
    '3x2': 6,
    '3x3': 7,
    '4x4': 9,
    '5x5': 11,
    'sqrt': 3,
}


def signal_name(signal):
    return signal if signal.startswith('signal') else 'signal' + signal


def raw_signal_name(signal):
    return signal[len('signal'):] if signal.startswith('signal') else signal


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run data GOF for fitted transfer-function candidates and make F-test comparisons.'
    )
    parser.add_argument(
        'years',
        nargs='*',
        help='Years/eras to compare. Backward-compatible positional form, e.g. 2017. Defaults depend on --preset.',
    )
    parser.add_argument(
        '--preset',
        choices=['run2', '2024'],
        default='run2',
        help='Convenience defaults. run2 preserves old defaults; 2024 uses year 2024 and RSGluon4000.',
    )
    parser.add_argument('--regions', nargs='+', default=DEFAULT_REGIONS, help='Region prefixes to compare.')
    parser.add_argument('--tfs', nargs='+', default=DEFAULT_TFS, help='Transfer-function forms to compare.')
    parser.add_argument('--output-base', default='ftest', help='Base directory containing F-test work areas.')
    parser.add_argument('--results-dir', default='ftest_results', help='Directory for F-test summaries and plots.')
    parser.add_argument('--signal', default=None, help='Signal used to make the F-test cards.')
    parser.add_argument('--force-gof', action='store_true', help='Re-run GOF even if the output ROOT file already exists.')
    parser.add_argument('--skip-missing', action='store_true', help='Skip missing or failed TF work areas instead of exiting.')
    return parser.parse_args()


def load_analysis_deps():
    global ROOT, TF1, TH1F, TLegend, TPaveText, TLatex, TArrow, TCanvas, kBlue, gStyle
    global cd, execute_cmd, FstatCalc, TwoDAlphabet

    import ROOT as root_module
    from ROOT import TF1 as root_TF1
    from ROOT import TH1F as root_TH1F
    from ROOT import TLegend as root_TLegend
    from ROOT import TPaveText as root_TPaveText
    from ROOT import TLatex as root_TLatex
    from ROOT import TArrow as root_TArrow
    from ROOT import TCanvas as root_TCanvas
    from ROOT import kBlue as root_kBlue
    from ROOT import gStyle as root_gStyle
    from TwoDAlphabet.helpers import cd as twod_cd
    from TwoDAlphabet.helpers import execute_cmd as twod_execute_cmd
    from TwoDAlphabet.ftest import FstatCalc as twod_FstatCalc
    from TwoDAlphabet.twoDalphabet import TwoDAlphabet as twod_TwoDAlphabet

    ROOT = root_module
    TF1 = root_TF1
    TH1F = root_TH1F
    TLegend = root_TLegend
    TPaveText = root_TPaveText
    TLatex = root_TLatex
    TArrow = root_TArrow
    TCanvas = root_TCanvas
    kBlue = root_kBlue
    gStyle = root_gStyle
    cd = twod_cd
    execute_cmd = twod_execute_cmd
    FstatCalc = twod_FstatCalc
    TwoDAlphabet = twod_TwoDAlphabet


def defaults_for(args):
    if args.preset == '2024':
        years = args.years or ['2024']
        signal = args.signal or 'RSGluon4000'
    else:
        years = args.years or ['2016', '2017', '2018', 'Comb']
        signal = args.signal or 'RSGluon2000'
    return years, signal_name(signal)


def candidate_subtags(signal):
    named = signal_name(signal)
    raw = raw_signal_name(signal)
    return [
        'ttbar-{}_area'.format(named),
        'ttbar-{}_area'.format(raw),
        '{}_area'.format(named),
        '{}_area'.format(raw),
    ]


def tf_area(output_base, year, region, tf):
    category = '{}{}'.format(region, year)
    return Path(output_base) / str(year) / region / 'ttbarfits_{}_ftest{}'.format(category, tf)


def load_two_d(area):
    run_config = area / 'runConfig.json'
    if not run_config.exists():
        raise FileNotFoundError('Missing {}'.format(run_config))
    return TwoDAlphabet(str(area), str(run_config), loadPrevious=True)


def find_subtag(area, signal):
    for subtag in candidate_subtags(signal):
        if (area / subtag / 'card.txt').exists():
            return subtag
    raise FileNotFoundError(
        'No card.txt found for signal {} in any expected subtag under {}'.format(signal, area)
    )


def gof_for_ftest(two_d, subtag, force=False, card_or_w='card.txt'):
    run_dir = Path(two_d.tag) / subtag
    gof_file = run_dir / 'higgsCombine_gof_data.GoodnessOfFit.mH120.root'

    if gof_file.exists() and not force:
        print('Reusing {}'.format(gof_file))
        return str(gof_file)

    with cd(str(run_dir)):
        command = ' '.join([
            'combine -M GoodnessOfFit',
            '-d {}'.format(card_or_w),
            '--algo=saturated',
            '-n _gof_data',
        ])
        execute_cmd(command)

    if not gof_file.exists():
        raise RuntimeError('GOF command did not produce {}'.format(gof_file))

    return str(gof_file)


def n_bins_for(two_d):
    binning = two_d.binnings['default']
    return (len(binning.xbinList) - 1) * (len(binning.ybinList) - 1)


def safe_pvalue(fdist, f_value):
    cdf = fdist.Integral(0.0, f_value)
    pvalue = 1.0 - cdf
    return max(0.0, min(1.0, pvalue))


def plot_ftest(row, results_dir):
    gStyle.SetOptStat(0)

    f_value = row['f_value']
    plot_max = max(10.0, 1.3 * f_value)
    fdist_name = 'fDist_{region}_{year}_{tf1}_{tf2}'.format(**row).replace('-', '_')
    hist_name = 'Fhist_{region}_{year}_{tf1}_{tf2}'.format(**row).replace('-', '_')

    fdist = TF1(fdist_name, '[0]*TMath::FDist(x, [1], [2])', 0, plot_max)
    fdist.SetParameter(0, 1)
    fdist.SetParameter(1, row['p2'] - row['p1'])
    fdist.SetParameter(2, row['n_bins'] - row['p2'])

    canvas = TCanvas('c_{}'.format(hist_name), 'c', 800, 600)
    canvas.SetLeftMargin(0.12)
    canvas.SetBottomMargin(0.12)
    canvas.SetRightMargin(0.1)
    canvas.SetTopMargin(0.1)

    ftest_hist = TH1F(hist_name, '', 30, 0, plot_max)
    ftest_hist.GetXaxis().SetTitle('F = #frac{-2log(#lambda_{1}/#lambda_{2})/(p_{2}-p_{1})}{-2log#lambda_{2}/(n-p_{2})}')
    ftest_hist.GetXaxis().SetTitleSize(0.025)
    ftest_hist.GetXaxis().SetTitleOffset(2)
    ftest_hist.GetYaxis().SetTitleOffset(0.85)
    ftest_hist.Draw('pez')

    fdist.Draw('same')
    arrow = TArrow(f_value, 0.25, f_value, 0)
    arrow.SetLineColor(kBlue + 1)
    arrow.SetLineWidth(2)
    arrow.Draw()

    legend = TLegend(0.6, 0.73, 0.89, 0.89)
    legend.SetLineWidth(0)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.03)
    legend.AddEntry(arrow, 'observed = {:.3f}'.format(f_value), 'l')
    legend.AddEntry(fdist, 'F-dist, ndf = ({:.0f}, {:.0f})'.format(fdist.GetParameter(1), fdist.GetParameter(2)), 'l')
    legend.Draw('same')

    model_info = TPaveText(0.2, 0.6, 0.4, 0.8, 'brNDC')
    model_info.AddText('simple = {}'.format(row['tf1']))
    model_info.AddText('complex = {}'.format(row['tf2']))
    model_info.AddText('p-value = {:.3f}'.format(row['p_value']))
    model_info.Draw('same')

    latex = TLatex()
    latex.SetTextAlign(11)
    latex.SetTextSize(0.06)
    latex.SetTextFont(62)
    latex.SetNDC()
    latex.DrawLatex(0.12, 0.91, 'CMS')
    latex.SetTextSize(0.05)
    latex.SetTextFont(52)
    latex.DrawLatex(0.22, 0.91, 'Work in Progress')
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)
    latex.DrawLatex(0.68, 0.91, lumi_label(row['year']))

    output = Path(results_dir) / 'FTest_{tf1}_{tf2}_{year}_{region}.png'.format(**row)
    canvas.SaveAs(str(output))


def lumi_label(year):
    if '2016' in str(year):
        return '2016 (13 TeV)'
    if '2017' in str(year):
        return '2017 (13 TeV)'
    if '2018' in str(year):
        return '2018 (13 TeV)'
    if '2024' in str(year):
        return '2024 (13.6 TeV)'
    return '2016-2018 (13 TeV)'


def write_summary(rows, results_dir, year, region):
    summary = Path(results_dir) / 'ftest_results_{}{}.csv'.format(region, year)
    with open(summary, 'w') as handle:
        handle.write('region,year,tf1,tf2,p1,p2,n_bins,f_value,p_value\n')
        for row in rows:
            handle.write(
                '{region},{year},{tf1},{tf2},{p1},{p2},{n_bins},{f_value:.8g},{p_value:.8g}\n'.format(**row)
            )
    print('Wrote {}'.format(summary))


def prepare_inputs(args, year, region, signal):
    prepared = {}
    for tf in args.tfs:
        if tf not in N_PARAMS:
            raise KeyError('No parameter count is defined for TF {}. Add it to N_PARAMS.'.format(tf))

        area = tf_area(args.output_base, year, region, tf)
        try:
            two_d = load_two_d(area)
            subtag = find_subtag(area, signal)
            gof_file = gof_for_ftest(two_d, subtag, force=args.force_gof)
            prepared[tf] = {
                'area': area,
                'two_d': two_d,
                'subtag': subtag,
                'gof_file': gof_file,
                'n_params': N_PARAMS[tf],
                'n_bins': n_bins_for(two_d),
            }
        except Exception as exc:
            if not args.skip_missing:
                raise
            print('Skipping {}: {}'.format(tf, exc))

    return prepared


def compare_pairs(prepared, tfs, year, region, results_dir):
    rows = []
    for i, tf1 in enumerate(tfs):
        for tf2 in tfs[i + 1:]:
            if tf1 not in prepared or tf2 not in prepared:
                continue

            tf1_params = prepared[tf1]['n_params']
            tf2_params = prepared[tf2]['n_params']
            if tf1_params == tf2_params:
                print('Skipping {} vs {} because both have {} RPF params'.format(tf1, tf2, tf1_params))
                continue

            if tf1_params < tf2_params:
                simple_tf, complex_tf = tf1, tf2
            else:
                simple_tf, complex_tf = tf2, tf1

            p1 = prepared[simple_tf]['n_params']
            p2 = prepared[complex_tf]['n_params']
            n_bins = prepared[simple_tf]['n_bins']
            f_values = FstatCalc(prepared[simple_tf]['gof_file'], prepared[complex_tf]['gof_file'], p1, p2, n_bins)
            f_value = f_values[0] if f_values else 0.0

            fdist = TF1('pval_{}_{}_{}_{}'.format(region, year, tf1, tf2), '[0]*TMath::FDist(x, [1], [2])', 0, max(10.0, 1.3 * f_value))
            fdist.SetParameter(0, 1)
            fdist.SetParameter(1, p2 - p1)
            fdist.SetParameter(2, n_bins - p2)
            p_value = safe_pvalue(fdist, f_value)

            row = {
                'region': region,
                'year': year,
                'tf1': simple_tf,
                'tf2': complex_tf,
                'p1': p1,
                'p2': p2,
                'n_bins': n_bins,
                'f_value': f_value,
                'p_value': p_value,
            }
            rows.append(row)
            print('{region}{year}: {tf1} vs {tf2}, F={f_value:.4g}, p={p_value:.4g}'.format(**row))
            plot_ftest(row, results_dir)

    return rows


def main():
    args = parse_args()
    load_analysis_deps()
    years, signal = defaults_for(args)
    Path(args.results_dir).mkdir(parents=True, exist_ok=True)
    ROOT.gROOT.SetBatch(True)

    print('Years: {}'.format(', '.join(years)))
    print('Regions: {}'.format(', '.join(args.regions)))
    print('Transfer functions: {}'.format(', '.join(args.tfs)))
    print('Signal: {}'.format(signal))
    print('Input work areas: {}'.format(args.output_base))
    print('Results directory: {}'.format(args.results_dir))

    for year in years:
        for region in args.regions:
            print('Preparing {}{}...'.format(region, year))
            prepared = prepare_inputs(args, year, region, signal)
            rows = compare_pairs(prepared, args.tfs, year, region, args.results_dir)
            write_summary(rows, args.results_dir, year, region)


if __name__ == '__main__':
    main()
