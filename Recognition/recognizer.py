import argparse
import sys


def recognize(args):
    pass


def parse(argv):
    parser = argparse.ArgumentParser(description="""
     Image recognizer
     Program has two modes: single(default) and batch
     Single: 
     1. Get path to picture and name of result file name.
     2. Recognize picture and save date in picture's directory name as <GivenName>.xlsx
     Batch: 
     1. Get path to directory with pictures and name of result's directory
     2. Recognize all pictures and saves results in path\\Results\\<GivenName>
        as <ChartNumber>.xlsx
        """, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--batch', action='store_true')
    parser.add_argument('path', action='store')
    parser.add_argument('name', action='store')

    return parser.parse_args(argv[1:])


def main():
    args = parse(sys.argv)
    recognize(args)


main()
