from optparse import OptionParser
import subprocess
import array
from  array import array
import numpy as np
import json
import ROOT
from ROOT import TGraph, TLatex, TFile, TLine, TColor, TLegend, TCanvas, kOrange, kGreen, kTRUE, gStyle, gROOT
import header
from header import WaitForJobs, make_smooth_graph, Inter
from style import * 
gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)
import argparse





# Initialize arrays to eventually store the points on the TGraph
x_mass = array('d')
y_limit = array('d')
y_mclimit  = array('d')
y_mclimitlow68 = array('d')
y_mclimitup68 = array('d')
y_mclimitlow95 = array('d')
y_mclimitup95 = array('d')


def Get_limits(tag, signal_mass, signal_names, blind=False) :
 # For each signal
 for this_index, this_name in enumerate(signal_names):
    print ("signal name is ", this_name )
    # Setup call for one of the signal
    this_xsec = signal_xsecs[this_index]
    this_mass = signal_mass[this_index]
    if "run2" in directory :
      print "it enters the loop"
      this_output = TFile.Open(this_name+'/higgsCombine.Test.AsymptoticLimits.mH120.root')
    else : 
      this_output = TFile.Open(this_name+'/higgsCombine_combined.AsymptoticLimits.mH120.root')
    if not this_output: continue
    this_tree = this_output.Get('limit')
    
    this_xsec = this_xsec
    
    
    # Set the mass (x axis)
    x_mass.append(this_mass)
    # Grab the cross section limits (y axis)
    for ievent in range(int(this_tree.GetEntries())):
        this_tree.GetEntry(ievent)
        
        
        
        # Nominal expected
        if this_tree.quantileExpected == 0.5:
            print("mass is, ", this_mass, "expected is : ", this_tree.limit *this_xsec)
            y_mclimit.append(this_tree.limit*this_xsec)
        # -1 sigma expected
        if round(this_tree.quantileExpected,2) == 0.16:
            y_mclimitlow68.append(this_tree.limit*this_xsec)
        # +1 sigma expected
        if round(this_tree.quantileExpected,2) == 0.84:
            y_mclimitup68.append(this_tree.limit*this_xsec)
        # -2 sigma expected
        if round(this_tree.quantileExpected,3) == 0.025:
            y_mclimitlow95.append(this_tree.limit*this_xsec)
        # +2 sigma expected
        if round(this_tree.quantileExpected,3) == 0.975:
            y_mclimitup95.append(this_tree.limit*this_xsec)

        # Observed (plot only if unblinded)
        if this_tree.quantileExpected == -1:
            if  blind == False:
                #print('DEBUG : appending to y_limit')
                #print('appending: {} to y_limit'.format(this_tree.limit*this_xsec))
                y_limit.append(this_tree.limit*this_xsec)
            else:
                y_limit.append(0.0)

def plot_limit(blind=False):
 # Make Canvas and TGraphs (mostly stolen from other code that formats well)
 climits = TCanvas("climits", "climits",700, 600)
 climits.SetLogy(True)
 climits.SetLeftMargin(.15)
 climits.SetBottomMargin(.15)  
 climits.SetTopMargin(0.1)
 climits.SetRightMargin(0.05)


 # Expected
 #print('---------DEBUG-----------')
 #print('x_mass: {}'.format(x_mass))
 #print('len x_mass: {}'.format(len(x_mass)))
 #print('y_mclimit: {}'.format(y_mclimit))
 g_mclimit = TGraph(len(x_mass), x_mass, y_mclimit)
 g_mclimit.SetTitle("")
 g_mclimit.SetMarkerStyle(21)
 g_mclimit.SetMarkerColor(1)
 g_mclimit.SetLineColor(1)
 g_mclimit.SetLineStyle(2)
 g_mclimit.SetLineWidth(3)
 g_mclimit.SetMarkerSize(0.)


 ymax = 1e4
 ymin = 1e-4

 xmin = signal_mass[0]
 xmax = signal_mass[-1]


 linestyle = "l"
 fillstyle = "lf"

 # Observed
 if  blind == False:
    print 'Not blinded'
    print ("it enters where you want")
    #print('---------------DEBUG---------------------')
    #print('x_mass: {}'.format(x_mass))
    #print('len x_mass: {}'.format(len(x_mass)))
    #print('y_limit: {}'.format(y_limit))
    g_limit = TGraph(len(x_mass), x_mass, y_limit)
    g_limit.SetTitle("")
    g_limit.SetMarkerStyle(7)
    g_limit.SetMarkerColor(1)
    g_limit.SetLineColor(2)
    g_limit.SetLineWidth(2)
    g_limit.SetMarkerSize(1) #0.5
    g_limit.GetYaxis().SetRangeUser(0., 80.)
    g_limit.GetXaxis().SetRangeUser(xmin, xmax)
    #g_limit.SetMinimum(0.3e-2) #0.005
    g_limit.SetMaximum(ymax)
    g_limit.SetMinimum(ymin)

 else:
    print 'Blinded'
    g_mclimit.GetYaxis().SetRangeUser(0., 80.)
    g_mclimit.GetXaxis().SetRangeUser(xmin, xmax)
    #g_mclimit.SetMinimum(0.3e-2) #0.005
    g_mclimit.SetMaximum(ymax)  
    g_mclimit.SetMinimum(ymin)
    

 # Will later be 1 and 2 sigma expected
 g_mcplus = TGraph(len(x_mass), x_mass, y_mclimitup68)
 g_mcminus = TGraph(len(x_mass), x_mass, y_mclimitlow68)

 g_mc2plus = TGraph(len(x_mass), x_mass, y_mclimitup95)
 g_mc2minus = TGraph(len(x_mass), x_mass, y_mclimitlow95)


 # Theory line
 graphWP = ROOT.TGraph()
 graphWP.SetTitle("")
 graphWP.SetMarkerStyle(23)
 graphWP.SetMarkerColor(4)
 graphWP.SetMarkerSize(0.5)
 graphWP.GetYaxis().SetRangeUser(0., 80.)
 graphWP.GetXaxis().SetRangeUser(xmin, xmax)
 graphWP.SetMinimum(0.3e-2) #0.005
 graphWP.SetMaximum(ymax)
 for index,mass in enumerate(signal_mass):
    xsec = theory_xsecs[index] * 1.3 ##k factor.
    graphWP.SetPoint(index,    mass,   xsec    )
 graphWP.SetLineWidth(3)
 graphWP.SetLineColor(4)

 # 2 sigma expected
 g_error95 = make_smooth_graph(g_mc2minus, g_mc2plus)
 g_error95.SetFillColor(TColor.GetColor("#F5BB54"))
 g_error95.SetLineColor(0)

 # 1 sigma expected
 g_error = make_smooth_graph(g_mcminus, g_mcplus)
 g_error.SetFillColor(TColor.GetColor("#607641"))
 g_error.SetLineColor(0)

 # Finally calculate the intercept
 expectedMassLimit, expectedCrossLimit = Inter(g_mclimit,graphWP) #if len(Inter(g_mclimit,graphWP)) > 0 else -1.0
 upLimit,trash = Inter(g_mcminus,graphWP) if len(Inter(g_mcminus,graphWP)) > 0 else -1.0
 lowLimit,trash = Inter(g_mcplus,graphWP) if len(Inter(g_mcplus,graphWP)) > 0 else -1.0

 print 'expectedMassLimit', expectedMassLimit
 print 'expectedCrossLimit', expectedCrossLimit

 if not blind:
    g_limit.GetXaxis().SetTitle("m_{"+signal_string[signal]+"} [TeV]")  # NOT GENERIC
    g_limit.GetYaxis().SetTitle("#sigma_{"+signal_string[signal]+"} #times B("+signal_string[signal]+" #rightarrow t #bar{t}) [pb]") # NOT GENERIC

    g_limit.Draw('ap')
    g_error95.Draw(fillstyle)
    g_error.Draw(fillstyle)
    g_mclimit.Draw("SAME")
    g_limit.Draw("SAME")
    graphWP.Draw(linestyle)
    g_limit.GetYaxis().SetTitleOffset(1.3)
    g_limit.GetXaxis().SetTitleOffset(1.15)

 else:
    g_mclimit.GetXaxis().SetTitle("m_{"+signal_string[signal]+"} [TeV]")  # NOT GENERIC
    g_mclimit.GetYaxis().SetTitle("#sigma_{"+signal_string[signal]+"} #times B("+signal_string[signal]+" #rightarrow t #bar{t}) [pb]") # NOT GENERIC
    g_mclimit.GetXaxis().SetTitleSize(0.055)
    g_mclimit.GetYaxis().SetTitleSize(0.05)
    g_mclimit.Draw("ap")
    g_error95.Draw(fillstyle)
    g_error.Draw(fillstyle)
    g_mclimit.Draw(linestyle)
    graphWP.Draw(linestyle)
    g_mclimit.GetYaxis().SetTitleOffset(1.5)
    g_mclimit.GetXaxis().SetTitleOffset(1.25)
    g_mclimit.GetXaxis().SetTitle("m_{"+signal_string[signal]+" [TeV]")  # NOT GENERIC
    g_mclimit.GetYaxis().SetTitle("#sigma_{"+signal_string[signal]+" #times B("+signal_string[signal]+" #rightarrow t #bar{t}) [pb]") # NOT GENERIC
        
 # graphWP.Draw("c")



 if drawIntersection:
    expLineLabel = TPaveText(expectedMassLimit-300, expectedCrossLimit*2, expectedMassLimit+300, expectedCrossLimit*15, "NB")
    expLineLabel.SetFillColorAlpha(kWhite,0)
    expLineLabel.AddText(str(int(expectedMassLimit))+' TeV')
    expLineLabel.Draw()

 print 'Expected limit: '+str(expectedMassLimit) + ' +'+str(upLimit-expectedMassLimit) +' -'+str(expectedMassLimit-lowLimit) + ' TeV' # NOT GENERIC
 if not blind:
    obsMassLimit,obsCrossLimit = Inter(g_limit,graphWP) if len(Inter(g_limit,graphWP)) > 0 else -1.0
    print 'Observed limit: '+str(obsMassLimit) + ' TeV'

    obsLine = TLine(obsMassLimit,g_mclimit.GetMinimum(),obsMassLimit,obsCrossLimit)
    obsLine.SetLineStyle(2)
    obsLine.Draw()

    if drawIntersection:
        obsLineLabel = TPaveText(obsMassLimit-300, obsCrossLimit*3, obsMassLimit+300, obsCrossLimit*12,"NB")
        obsLineLabel.SetFillColorAlpha(kWhite,0)
        obsLineLabel.AddText(str(int(obsMassLimit))+' TeV')
        obsLineLabel.Draw()

        
        
         
 # Legend and draw


 makeLumiText(0.9, 0.93, year=year, lumi=lumi[year])
 makeCMSText(0.2, 0.85, additionalText=" Preliminary")
 gStyle.SetLegendFont(42)
 legend = TLegend(0.60, 0.60, 0.91, 0.87, '')
 legend.SetHeader("95% CL upper limits")
 if not blind:
    legend.AddEntry(g_limit, "Observed", "l")
 legend.AddEntry(g_mclimit, "Median expected","l")
 legend.AddEntry(g_error, "68% expected", "f")
 legend.AddEntry(g_error95, "95% expected", "f")
 legend.AddEntry(graphWP, "Theory "+signal_string[signal]+" "+legend_string[width], "l")   # NOT GENERIC

 legend.SetBorderSize(0)
 legend.SetFillStyle(0)
 legend.SetLineColor(0)
 legend.Draw("same")
 climits.RedrawAxis()
 savefilename = output+'/limits'+'_' + signal +width+"_" + year +str(blind)+'.pdf'

 climits.SaveAs(savefilename)
 climits.SaveAs(savefilename.replace('pdf', 'png'))
 print 'saving ' + savefilename
 print 'saving ' + savefilename.replace('pdf', 'png')

drawIntersection = False


#directory where signal directories are located
if __name__ == "__main__":    
  parser = argparse.ArgumentParser(description="input to plotting limits")
  parser.add_argument('--year', type=str,choices=["16","17","18","run2"], default="run2", help="plot limits for single year or combined run2")
  parser.add_argument('--output', type=str, default='limits', help="output directory")
  parser.add_argument('--signal', choices=["RSGluon","ZPrime","ZPrime_DM"], help='Specify signal scenario to plot')
  parser.add_argument('--width', choices=["1","10","30","DM",""] ,help='Specify width of signal to plot')
  parser.add_argument('--blind',default=False, help='Specify signal scenario to plot')
  args = parser.parse_args()
  year = args.year 
  width=args.width
  signal=args.signal
  output=args.output
  blind=args.blind
  
  signal_df = json.load(open('jsons/signal_xs.json'))
  directory = 'output/cards_combined_'+year
  print directory
  signal_mass  = signal_df[signal+width]['mass']
  theory_xsecs = signal_df[signal+width]['theory']
  signal_xsecs = signal_df[signal+width]['expected']
  lumi = {"16": 36, "17": 41.5, "18": 60, "run2": 138}
  signal_string = {"RSGluon": "g_{KK}" , "ZPrime":"Z'", "ZPrime_DM": "Z_{DM}"}
  legend_string = {"" :"", "1" : "1% Width", "10":"10% Width" , "30":"30% Width", "DM":"" }
  if width != "" : tag = "_"+width
  else : tag = ""
  if width == "1" : tag ="" 
  signal_names = [directory + '/signal' + signal + str(int(s*1000)) + tag + '_area' for s in signal_mass]
  print("signal names are ", signal_names)
  Get_limits(tag, signal_mass, signal_names,blind)
  plot_limit(blind) 

### The command to run is : python plot_limits..py --signal RSGluon --width "" --blind False --output limits --year run2  
