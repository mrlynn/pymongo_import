'''
Created on 11 Aug 2017

@author: jdrumgoole
'''
import argparse
import sys
import os

from pymongodbimport.filesplitter import File_Splitter


__VERSION__ = "0.1"

def multiimport( args ):
    
    usage_message = '''
    
    split a text file into seperate pieces. if you specify autosplit then the program
    will use the first ten lines to calcuate an average line size and use that to determine
    the rough number of splits.
    
    if you use --splitsize then the file will be split using --splitsize chunks until it is consumed
    '''
    
    parser = argparse.ArgumentParser( usage=usage_message, version=__VERSION__ )
    
    parser.add_argument( "--autosplit", type=int, 
                         help="split file based on loooking at the first ten lines and overall file size [default : %(default)s]")
    parser.add_argument('--hasheader',  default=False, action="store_true", help="Use header line for column names [default: %(default)s]")
    parser.add_argument( "--splitsize", type=int, help="Split file into chunks of this size")
    parser.add_argument( "filenames", nargs="*", help='list of files')
    args= parser.parse_args( args )
    
    print( "Splitting file")
    if len( args.filenames ) == 0 :
        print( "No input file specified to split")
    elif len( args.filenames) > 1 :
        print( "More than one input file specified ( %s ) only splitting the first file:'%s'" % 
               ( " ".join( args.filenames ), args.filenames[ 0 ] ))
    
    splitter = File_Splitter( args.filenames[ 0 ], args.autosplit, args.hasheader )
    if args.autosplit:
        print( "Autosplitting: '%s'" % args.filenames[ 0 ] )
        files = splitter.autosplit()
    else:
        print( "Splitting '%s' using %i splitsize" % ( args.filenames[ 0 ], args.splitsize ))
        files = splitter.split_file( args.splitsize )
    #print( "Split '%s' into %i parts"  % ( args.filenames[ 0 ], len( files )))
    count = 1
    total_size = 0
    for i in files:
        size = os.path.getsize( i )
        total_size = total_size + size
        print ( "%i. %s : size: %i" % ( count, i, size ))
        count = count + 1
    
    if total_size != splitter.no_header_size():
        raise ValueError( "Filesize of original and pieces does not match: total_size: %i, no header split_size: %i" % ( total_size, splitter.no_header_size()))
   
if __name__ == '__main__':
    multiimport( sys.argv[1:] ) 
    