########################################
# Make an elog entry with relevant plots
########################################
import argparse 
import json
import os
import shutil

'''
function: make_elog_entry
'''
def make_elog_entry(args):
    # Get the main directory
    maindir = args.maindir
    # Make sure to add trailing /
    if maindir[-1] != '/':
        maindir = maindir + '/'

    # Get the name of the output directory, and create it.
    # This will store the output markdown file and the plots we want. 
    outdir = args.outdir
    if outdir[-1] != '/':
        outdir = outdir + '/'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Get a big list of all of the files we need to add to the output directory
    list_of_plots_to_write = []

    print("About to copy files to ", args.outdir )

    # Create the output file
    with open( outdir + args.outfile,'w' ) as fout : 
        # Open the input file and load the json structure
        with open( args.plotfile ) as f: 
            figs_to_plot_json = json.load( f )
            # Get the list of signals. Each has its own directory. 
            signals = figs_to_plot_json['SIGNALS']
            fout.write("----\n")
            for isig,isig_desc in signals.items():
                fout.write("### " + isig + '\n')
                fout.write("|Plot|Description|\n")
                fout.write("|------|------|\n")

                if isig[-1] != '/':
                    isig = isig + '/'
                for iplot,idescription in figs_to_plot_json['FIGURES'].items():
                    fout.write( '| <image src="%s">x | %s |\n' % (maindir + isig + iplot, idescription )) 
                    list_of_plots_to_write.append( maindir + isig + iplot )
            for iplot,plot in enumerate(list_of_plots_to_write):
                dstfile = os.path.join( outdir , plot )
                filepathlist = plot.split('/')
                dstpathlist = [ s + '/' for s in filepathlist[0:-1] ]
                dstpathname = outdir + ''.join( dstpathlist )
                dstfilename = dstpathname + filepathlist[-1]
                print("copying file ", plot )
                print("Creating path ", dstpathname)
                print("Copying file to ", dstfilename)
                
                if not os.path.exists(dstpathname):
                    print("making directory ", dstpathname)
                    os.makedirs( dstpathname)
                    #shutil.copytree( dstpathname, outdir )
                shutil.copy( plot, dstfilename )

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="input to make an elog entry")
    parser.add_argument('--maindir', type=str, required=True, help="Input directory to parse")
    parser.add_argument('--plotfile', type=str, required=True, help="json file containing plots and descriptions")
    parser.add_argument('--outfile', type=str, required=True, help="Output file name")
    parser.add_argument("--outdir", type=str, required=True, help="Directory name to make and copy plots into")
    args = parser.parse_args()
    make_elog_entry(args)




