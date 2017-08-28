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
from pymongodbimport.filesplitter import File_Splitter


def pwc( *argv ):
    parser = argparse.ArgumentParser()
    parser.add_argument( "filenames", nargs="*", help='list of files')
    args= parser.parse_args( *argv )
    
    line_count = 0
    total_count = 0
    for filename in args.filenames:
        line_count = File_Splitter.count_lines( filename )
        total_count = total_count + line_count
        print( "%i\t%s" % ( line_count, filename ))
        
    if len( args.filenames ) > 1 :
        print( "%i\ttotal" % total_count )
            
if __name__ == "__main__" :
    pwc( sys.argv[1:])
    

    