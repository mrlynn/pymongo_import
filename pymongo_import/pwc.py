'''
=======================================
pwc - python word count
=======================================
Created on 27 Aug 2017

A program to count lines as opposed to \n characters. The *wc* program will often miss
the last line of programs that do not terminate their last line with a \n.

This uses the Python readline() function to count lines correctly and opens files
in universal mode.

@author: jdrumgoole
'''

import sys
import argparse
from pymongo_import.filesplitter import File_Splitter


def pwc( *argv ):
    parser = argparse.ArgumentParser()
    parser.add_argument( "filenames", nargs="*", help='list of files')
    args= parser.parse_args( *argv )
    
    line_count = 0
    total_count = 0
    total_size = 0
    size = 0
    if args.filenames:
        print( "lines\tbytes\tfilename")
    for filename in args.filenames:
        (line_count, size) = File_Splitter.wc( filename )
        total_count = total_count + line_count
        total_size  = total_size  + size
        print( "%i\t%i\t%s" % ( line_count, size, filename ))
    if len( args.filenames ) > 1 :

        print( "%i\t%i\ttotal" % (total_count, total_size ))
            
if __name__ == "__main__" :
    pwc( sys.argv[1:])
    

    