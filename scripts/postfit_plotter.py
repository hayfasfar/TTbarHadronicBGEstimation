import math
import  ROOT 
from style import *
import json
projy = "projy1"
year="combined"
cat = "cen"
def get_transfer_function(cat):
    with open("jsons/TransferFunctions.json", "r") as file:
        transfer_functions = json.load(file)
    return transfer_functions[cat]


def _make_pull_plot(data, bkg):
    pull = data.Clone(data.GetName()+"_pull")
    pull.Add(bkg,-1)
    
    sigma = 0.0
    for ibin in range(1,pull.GetNbinsX()+1):
        d = data.GetBinContent(ibin)
        b = bkg.GetBinContent(ibin)
        if d >= b:
            derr = data.GetBinErrorLow(ibin)
            berr = bkg.GetBinErrorUp(ibin)
        elif d < b:
            derr = data.GetBinErrorUp(ibin)
            berr = bkg.GetBinErrorLow(ibin)
        
        if d == 0:
            derr = 1

        sigma = math.sqrt(derr*derr - berr*berr)
        if sigma != 0:
            pull.SetBinContent(ibin, (pull.GetBinContent(ibin))/sigma)
        else:
            pull.SetBinContent(ibin, 0.0 )

    pull.SetFillColor(ROOT.kOrange+9)
    pull.SetLineColor(ROOT.kOrange+9)
    return pull


fits = ["postfit"]
categories = ["cen","fwd"]

for fit in fits : 

  #for cat in categories :


  file_1_name = "postfitShapes.root"
  file_1 = ROOT.TFile.Open(file_1_name)
  
  dict = {0:16 , 1:17 , 2:18}
  directories = ["ZeroLep_Name1_Name1_cen16Pass_SIG_postfit", "ZeroLep_Name2_Name1_cen17Pass_SIG_postfit", "ZeroLep_Name3_Name1_cen18Pass_SIG_postfit"]

  #directories = ["ZeroLep_Name1_Name1_cen16Pass_SIG_postfit"]
  for i, directory  in enumerate(directories): 
    print ("i is " , i , " directory is: ", directory )
    hist_TTbar = file_1.Get(str(directory)+"/"+str(dict[i])+"_TTbar")
    print ("hist_TTbar is ", hist_TTbar.GetName())
    print ("hist_TTbar integral is  ", hist_TTbar.Integral())
    hist_QCD = file_1.Get(str(directory)+"/"+"QCD")
    hist_totb = file_1.Get(str(directory)+"/"+"TotalBkg")
    hist_data = file_1.Get(str(directory)+"/"+"data_obs")
    print ("hist_data is ", hist_data.GetName())
    print ("hist_data integral is  ", hist_data.Integral())
    hist_sig2000 = file_1.Get(str(directory)+"/"+str(dict[i])+"_signalZPrime2000")

    if i == 0 :
      
     hist_TTbar_sum = hist_TTbar.ProjectionY() 
     print ("integral iteration TTbar ", i , " is ", hist_TTbar_sum.Integral())
     hist_QCD_sum = hist_QCD.ProjectionY("QCD"+str(i))
     hist_totb_sum = hist_totb.ProjectionY("totb_obs"+str(i))
     hist_data_sum = hist_data.ProjectionY("data_obs"+str(i))
     print ("integral iteration data ", i , " is ", hist_data_sum.Integral())
     hist_sig2000_sum = hist_sig2000.ProjectionY()

    else: 
  
     hist_TTbar_sum.Add(hist_TTbar.ProjectionY()) 
     print ("integral iteration TTbar ", i , " is ", hist_TTbar_sum.Integral())
     hist_QCD_sum.Add(hist_QCD.ProjectionY("QCD"+str(i)))
     hist_totb_sum.Add(hist_totb.ProjectionY("totb_obs"+str(i)))
     hist_data_sum.Add(hist_data.ProjectionY("data_obs"+str(i)))
     print ("integral iteration data ", i , " is ", hist_data_sum.Integral())
     hist_sig2000_sum.Add(hist_sig2000.ProjectionY())
    

##%%%%%%%%%%%% normalisation per bin width  %%%%%%%%%%%%%%%%%%%%%%


  '''  
  for hist in [ hist_TTbar_sum, hist_QCD_sum , hist_totb_sum , hist_data_sum , hist_sig2000_sum] : 
    for i in range(1, hist.GetNbinsX() + 1):  # Loop over bins
      bin_content = hist.GetBinContent(i)
      bin_error = hist.GetBinError(i)  # Get the bin error
      bin_width = hist.GetBinWidth(i)
      #print ("bin width is ", bin_width, "bin_error is ", bin_error)
      if bin_width > 0:  
          hist.SetBinContent(i,bin_content /(1.e-3 * bin_width))  # Normalize by bin width
          hist.SetBinError(i, bin_error /(1.e-3 * bin_width))  # Normalize bin error as well
      #print("after normalisation bin content is ",  bin_content / bin_width , "bin_error is ", bin_error / bin_width )
  '''
  canvas = makeCanvas()
  canvas.cd()

  canvas.SetBottomMargin(0.1)
  canvas.SetLeftMargin(0.13)
  canvas.SetRightMargin(0.1)



  pad1 = ROOT.TPad("pad1","pad1",0, 0.33, 1, 1)
  pad1.SetBottomMargin(0.01)
  pad1.SetLeftMargin(0.16)
  pad1.SetRightMargin(0.01)
  pad1.SetBorderMode(0)


  pad2 = ROOT.TPad("pad2","pad2",0, 0, 1, 0.33)
  pad2.SetFillStyle(4000)
  pad2.SetTopMargin(0.0)
  pad2.SetBottomMargin(0.4)
  pad2.SetLeftMargin(0.16)
  pad2.SetRightMargin(0.01)
  pad2.SetBorderMode(0)


  pad1.Draw()
  pad2.Draw()

  year= 'combined'
  makeCMSText(0.20, 0.90, additionalText=" Preliminary")
  lumi = {"2016": 36, "2017": 41.5, "2018": 60, "combined": 138}
  makeLumiText(0.99, 0.96, year=year, lumi=lumi[year])

  if projy=="projy0" and cat == "cen" :

    text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| < 1, 25 < m_{t}< 105 GeV" ,29,43 , "")
  elif  projy=="projy0" and cat == "fwd":
    text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| > 1, 25 < m_{t}< 105 GeV" ,29,43 , "")
 
  elif  projy=="projy1" and cat == "cen":
    text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| < 1, 105 < m_{t}< 210 GeV" ,29,43 , "")

  elif  projy=="projy1" and cat == "fwd":
    text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| > 1, 105 < m_{t}< 210 GeV" ,29,43 , "")


  elif  projy=="projy2" and cat == "cen":
    text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| < 1, 210 < m_{t}< 475 GeV" ,29,43 , "")

  elif  projy=="projy2" and cat == "fwd" : 
    text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| > 1, 210 < m_{t}< 475 GeV" ,29,43 , "")
  else : 
   print ("something is wrong") 
   
  '''
    text = makeText(0.2, 0.76, 0.7, 0.87, "25 < m_{t}< 105 GeV ")

  elif projy=="projy1" :
    text = makeText(0.2, 0.76, 0.7, 0.87, "105 < m_{t}< 210 GeV ")

  elif projy=="projy2" :
    text = makeText(0.2, 0.76, 0.7, 0.87, "210 < m_{t}< 475 GeV ")

  if cat == "cen":
	  text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| < 1" ,29,43 , "")
  elif cat== "fwd": 
	  text = makeText(0.2, 0.82, 0.7, 0.87, "|#Deltay| > 1" ,29,43, "")
  '''
  pad1.cd()
  #pad1.SetLogy() 



  hist_QCD_sum.SetFillColor(ROOT.kYellow)
  hist_QCD_sum.SetLineColor(ROOT.kYellow)


  hist_TTbar_sum.SetFillColor(ROOT.kRed)
  hist_TTbar_sum.SetLineColor(ROOT.kRed)
  ############# THSTack 


  hs =  ROOT.THStack("hs","")
  hs.Add(hist_TTbar_sum)
  if fit != "prefit" :
    hs.Add(hist_QCD_sum)



  hist_data_sum.SetMarkerStyle(8) 
  hist_data_sum.SetMarkerSize(1.3) 

  hist_data_sum.SetBinErrorOption(ROOT.TH1.kPoisson)
  #hist_data_sum.SetTitleOffset(1.15,"xy")
  hist_data_sum.GetYaxis().SetLabelSize(0.07)
  hist_data_sum.GetYaxis().SetTitleSize(0.08)
  hist_data_sum.GetXaxis().SetLabelSize(0.07)
  hist_data_sum.GetXaxis().SetTitleSize(0.09)
  hist_data_sum.GetXaxis().SetLabelOffset(0.05)
  hist_data_sum.GetXaxis().SetNdivisions(505)
  hist_data_sum.GetYaxis().SetNdivisions(505)
  hist_data_sum.GetXaxis().SetLabelSize(0)
  hist_data_sum.GetYaxis().SetTitle("Events / TeV")
  hist_data_sum.GetYaxis().SetTitleOffset(0.7)



  if projy == "projy1":
    hist_data_sum.SetMaximum(2.3*hist_data_sum.GetMaximum())
    hist_data_sum.SetMinimum(1e-3)
  else : 
    hist_data_sum.SetMaximum(1.6*hist_data_sum.GetMaximum())
    hist_data_sum.SetMinimum(1e-3)



  pull = _make_pull_plot(hist_data_sum, hist_totb_sum)

  hist_totb_sum.SetMarkerStyle(0)
  if fit == "prefit" : 
    hist_totb_sum = hist_TTbar_sum.Clone()
  else : 
    hist_totb_sum = hist_totb_sum.Clone()
  hist_totb_sum.SetLineColor(0)
  hist_totb_sum.SetLineColor(ROOT.kGray)
  #hist_totb_sum.SetLineWidth(0)
  hist_totb_sum.SetFillColor(ROOT.kGray)
  hist_totb_sum.SetFillStyle(3354)

  hist_sig2000_sum.SetLineColor(ROOT.kBlue -6)
  #hist_sig2000_sum2.SetLineColor(ROOT.kGreen+2)
  hist_sig2000_sum.SetLineWidth(3)
  #hist_sig2000_sum2.SetLineWidth(3)

  hist_sig2000_sum.SetLineStyle(2)
  #hist_sig2000_sum2.SetLineStyle(2)

  hist_sig2000_sum.Scale(0.5)
  #hist_sig2000_sum2.Scale(5)

  hist_data_sum.Draw("pe X0")
  hs.Draw("hist SAME")
  hist_totb_sum.Draw("HIST SAME")
  hist_totb_sum.Draw("E2 SAME")
  hist_data_sum.Draw("pe X0 SAME")
  if projy == "projy1":
    hist_sig2000_sum.Draw("HIST SAME")
    ##hist_sig2000_sum2.Draw("HIST SAME")
  pad2.cd()
  
  xmin = pull.GetXaxis().GetXmin()
  xmax = pull.GetXaxis().GetXmax()
  line = ROOT.TLine(xmin, 0, xmax,0)
  pull.SetStats(0)
  pull.SetTitleOffset(1.15,"xy")
  
  pull.GetXaxis().SetLabelSize(0.13)
  pull.GetXaxis().SetTitleSize(0.16)
  pull.GetXaxis().SetTitleOffset(1.2)  
  pull.GetYaxis().SetTitleOffset(0.3) 
  pull.GetYaxis().SetLabelSize(0.13)
  pull.GetXaxis().SetNdivisions(505)
  pull.GetYaxis().SetNdivisions(505)
  pull.GetYaxis().SetTitle("(Data-bkg.) / #sigma")
  pull.GetYaxis().SetTitleSize(0.16)
  pull.GetYaxis().SetRangeUser(-5,5)
  pull.GetXaxis().SetTitle("m_{t#bar{t}} [TeV]")
  pull.SetLineColor(ROOT.kBlue)
  pull.SetFillColor(ROOT.kBlue)
  pull.SetFillStyle(3354)
  line.SetLineColor(4)
  pull.Draw("hist")
  line.Draw("same")
  
##%%%%%%%%%%%%% LEGEND
  pad1.cd()

  #pad1.SetLogy()
  legend = makeLegend(0.8, 0.5, 0.88, 0.88)
  legend.SetBorderSize(0)
  legend.AddEntry(hist_data_sum,'Data',"P EX0")
  if fit != "prefit" :
    legend.AddEntry(hist_QCD_sum,'QCD',"F")
  legend.AddEntry(hist_TTbar_sum,'t#bar{t}',"F")
  legend.AddEntry(hist_totb_sum,'Unc.',"F")
  legend.Draw()
  if projy == "projy1":
    legend2 = makeLegend(0.2, 0.45, 0.45, 0.65)
    legend2.AddEntry(hist_sig2000_sum,"Z', 1% width, M = 2 TeV","l")
    #legend2.AddEntry(#hist_sig2000_sum2,"Z', 1% width, M = 4 TeV","l")
    legend2.Draw()
  canvas.SaveAs("closure_results/"+str(year)+"_"+str(cat)+"_"+str(projy)+"_"+str(fit)+"_s_diff.pdf")

