from time import time
import os
import sys
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball, cd, execute_cmd
from TwoDAlphabet.ftest import FstatCalc
import multiprocessing
from ROOT import TF1, TH1F, TLegend, TPaveText, TLatex, TArrow, TCanvas, kBlue, gStyle

# Define regions and parameters
regions = ['cen','fwd']

nParams_dict = {
    '0x0': 1,
    '0x1': 2,
    '1x0': 2,
    '0x2': 3,
    '2x0': 3,
    '1x1': 3,
    '2x1': 4,
    '1x2': 4,
    '2x2': 4,
}



def ensure_input_directory(directory):
    """Create directory if it does not exist."""
    if os.path.exists(directory):
        print("Directory {}".format(directory))
    else : print ("FATAL: no directory for the given configuration")
def create_output_directory(output): 
    if os.path.exists(output): 
       print("output directory {} already exist")
    else: 
       os.mkdir(output)

def _select_signal(row, args):
    """Helper function to filter signal rows."""
    signame = args[0]
    if row.process_type == 'SIGNAL':
        return signame in row.process
    elif 'Background' in row.process:
        return row.process == 'QCD'
    else:
        return True


def _gof_for_FTest(twoD, subtag, card_or_w='card.txt'):
    """Run Goodness-of-Fit test."""
    run_dir = twoD.tag + '/' + subtag
    with cd(run_dir):
        gof_data_cmd = [
            'combine -M GoodnessOfFit',
            '-d ' + card_or_w,
            '--algo=saturated',
            '-n _gof_data'
        ]
        gof_data_cmd = ' '.join(gof_data_cmd)
        execute_cmd(gof_data_cmd)



def FTest(poly1, poly2, directory, regionby, year):
    '''
    Perform an F-test to compare the goodness-of-fit between two transfer function parameterizations using existing working areas
    Arguments:
    poly1 (str): e.g. '0x0', '1x1', ...
    poly2 (str): e.g. '0x0', '1x1', ...
    '''
    area1 = directory + '/ttbarfits_' + regionby + str(year) + '_ftest{}'.format(poly1)
    area2 = directory + '/ttbarfits_' + regionby + str(year) + '_ftest{}'.format(poly2)

    print('getting file {}/runConfig.json'.format(area1))

    # Load TwoDAlphabet objects
    twoD1 = TwoDAlphabet(area1, '{}/runConfig.json'.format(area1), loadPrevious=True)
    twoD2 = TwoDAlphabet(area2, '{}/runConfig.json'.format(area2), loadPrevious=True)

    # Assume binnings are the same for each area
    binning = twoD1.binnings['default']
    nBins = (len(binning.xbinList) - 1) * (len(binning.ybinList) - 1)

    # Get number of RPF params and run GoF for poly1
    params1 = twoD1.ledger.select(_select_signal, 'signalRSGluon2000', '').alphaParams
    rpfSet1 = params1[params1["name"].str.contains("rratio")]
    nRpfs1 = len(rpfSet1.index)
    nRpfs1 = nParams_dict[poly1]
    
    _gof_for_FTest(twoD1, 'ttbar-RSGluon2000_area', card_or_w='card.txt')
    gofFile1 = area1 + '/ttbar-RSGluon2000_area/higgsCombine_gof_data.GoodnessOfFit.mH120.root'

    # Get number of RPF params and run GoF for poly2
    params2 = twoD2.ledger.select(_select_signal, 'signalRSGluon2000', '').alphaParams
    rpfSet2 = params2[params2["name"].str.contains("rratio")]
    nRpfs2 = len(rpfSet2.index)
    nRpfs2 = nParams_dict[poly2]
    if abs(nRpfs2 - nRpfs1) < 0.1: return 0
    _gof_for_FTest(twoD2, 'ttbar-RSGluon2000_area', card_or_w='card.txt')
    gofFile2 = area2 + '/ttbar-RSGluon2000_area/higgsCombine_gof_data.GoodnessOfFit.mH120.root'

    # Perform F-test and plot results
    base_fstat = FstatCalc(gofFile1,gofFile2,nRpfs1,nRpfs2,nBins)
    print 'base_fstat', base_fstat
    plot_FTest(base_fstat, nRpfs1, nRpfs2, nBins, poly1, poly2, regionby, year)
   



# Function to plot the results of the F-test
def plot_FTest(base_fstat, nRpfs1, nRpfs2, nBins, poly1, poly2, regionby, year):
    gStyle.SetOptStat(0000)

    if len(base_fstat) == 0:
        base_fstat = [0.0]

    ftest_p1 = min(nRpfs1, nRpfs2)
    ftest_p2 = max(nRpfs1, nRpfs2)
    ftest_nbins = nBins
    fdist = TF1("fDist", "[0]*TMath::FDist(x, [1], [2])", 0, max(10, 1.3 * base_fstat[0]))
    fdist.SetParameter(0, 1)
    fdist.SetParameter(1, ftest_p2 - ftest_p1)
    fdist.SetParameter(2, ftest_nbins - ftest_p2)

    pval = fdist.Integral(0.0, base_fstat[0])

    # Save the results to a file
    with open('ftest_results_' + regionby + str(year) + '.txt', 'a') as outfile:
        outfile.write(poly1 + ', ' + poly2 + ', ' + str(1 - pval) + '\n')

    # Plot the F-test results
    c = TCanvas('c', 'c', 800, 600)
    c.SetLeftMargin(0.12)
    c.SetBottomMargin(0.12)
    c.SetRightMargin(0.1)
    c.SetTopMargin(0.1)

    ftestHist_nbins = 30
    ftestHist = TH1F("Fhist", "", ftestHist_nbins, 0, max(10, 1.3 * base_fstat[0]))
    ftestHist.GetXaxis().SetTitle("F = #frac{-2log(#lambda_{1}/#lambda_{2})/(p_{2}-p_{1})}{-2log#lambda_{2}/(n-p_{2})}")
    ftestHist.GetXaxis().SetTitleSize(0.025)
    ftestHist.GetXaxis().SetTitleOffset(2)
    ftestHist.GetYaxis().SetTitleOffset(0.85)
    ftestHist.Draw("pez")

    ftestobs = TArrow(base_fstat[0], 0.25, base_fstat[0], 0)
    ftestobs.SetLineColor(kBlue + 1)
    ftestobs.SetLineWidth(2)
    fdist.Draw('same')

    ftestobs.Draw()

    # Add legend and model info
    tLeg = TLegend(0.6, 0.73, 0.89, 0.89)
    tLeg.SetLineWidth(0)
    tLeg.SetFillStyle(0)
    tLeg.SetTextFont(42)
    tLeg.SetTextSize(0.03)
    tLeg.AddEntry(ftestobs, "observed = %.3f" % base_fstat[0], "l")
    tLeg.AddEntry(fdist, "F-dist, ndf = (%.0f, %.0f) " % (fdist.GetParameter(1), fdist.GetParameter(2)), "l")
    tLeg.Draw("same")

    model_info = TPaveText(0.2, 0.6, 0.4, 0.8, "brNDC")
    model_info.AddText('p1 = ' + poly1)
    model_info.AddText('p2 = ' + poly2)
    model_info.AddText("p-value = %.2f" % (1 - pval))
    model_info.Draw('same')

    latex = TLatex()
    latex.SetTextAlign(11)
    latex.SetTextSize(0.06)
    latex.SetTextFont(62)
    latex.SetNDC()
    latex.DrawLatex(0.12, 0.91, "CMS")
    latex.SetTextSize(0.05)
    latex.SetTextFont(52)
    latex.DrawLatex(0.22, 0.91, "Work in Progress")
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)

    if '2016' in year:
        latex.DrawLatex(0.72, 0.91, "2016 (13 TeV)")
    elif '2017' in year:
        latex.DrawLatex(0.72, 0.91, "2017 (13 TeV)")
    elif '2018' in year:
        latex.DrawLatex(0.72, 0.91, "2018 (13 TeV)")
    else:
        latex.DrawLatex(0.72, 0.91, "2016-2018 (13 TeV)")

    c.SaveAs('{}/FTest_{}_{}_{}_{}.png'.format(output,poly1, poly2, year, regionby))

if (len(sys.argv) > 1) :
    years = sys.argv[1]
else:
    years = ['2016','2017','2018']

output = 'ftest_results'
params_list = [
                '0x0',
                '0x1',
                '0x2',
                '1x0',
                '1x1',
                '1x2',
                '2x1',
                '2x2'
            ]

if __name__ == "__main__":
  for year in years :
    for region in regions:
        directory = os.path.abspath('ftest/{}/{}/'.format(year, region))
        ensure_input_directory(directory)
        create_output_directory(output)
        for i in range(len(params_list)):
            for j in range(i + 1, len(params_list)):
                FTest(params_list[i], params_list[j], directory, region, year)


