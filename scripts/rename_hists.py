import ROOT
import optparse
import glob 

def rename_hists(options):
    filenames = glob.glob( options.filenames )
    if options.verbose: print(" filenames = ", filenames )

    for ifile, filename in enumerate(filenames):
        fin = ROOT.TFile.Open(filename)
        if options.verbose: print("Opened file " , filename)
        foutname = filename.replace(".root", "_comb.root")
        fout = ROOT.TFile.Open(foutname, "RECREATE")
        if options.verbose: print("Made file ", foutname )
        keys = fin.GetListOfKeys()
        for key in keys: 
            if options.verbose: print("Getting key ", key.GetName() )
            obj_in = fin.Get(key.GetName())
            n = obj_in.GetName()
            nout = n.replace( options.fromstr, options.tostr )
	    if "TTAG" in n: nout = nout.replace( "TTAG", "TTAG"+str(options.fromstr) )
	    if "JES" in n: nout = nout.replace( "JES", "JES"+str(options.fromstr) )
	    if "JER" in n: nout = nout.replace( "JER", "JER"+str(options.fromstr) )
	    if "PILEUP" in n: nout = nout.replace( "PILEUP", "PILEUP"+str(options.fromstr) )
            if options.verbose: print("Changing name to ", nout)
            obj_out = obj_in.Clone( nout )
            fout.cd()
            obj_out.Write()
        fout.Close()
        fin.Close()
    return 

if __name__ == "__main__":    
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="filenames", metavar="FILES", help="input from FILES")
    parser.add_option("--from", dest="fromstr")
    parser.add_option("--to", dest="tostr")
    parser.add_option("--verbose", dest="verbose", default=False)
    (options,args) = parser.parse_args()
    rename_hists(options)
