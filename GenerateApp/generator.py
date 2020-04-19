import sys
import argparse
import pathlib
import xlsxwriter
import random
import os


def generate(args):
    if not os.access(str(args.BasePath), os.F_OK):
              os.mkdir(str(args.BasePath))
    os.chdir(str(args.BasePath))
    for iteration in range(args.ChartsCount):
        random.seed()
        ColumnCount = random.randint(5, 12)
        workbook = xlsxwriter.Workbook('Table'+str(iteration+1)+'.xlsx')
        worksheet = workbook.add_worksheet()
        LowerBound = random.randint(100, 500)
        UpperBound = random.randint(600, 1000)
        for column in range(ColumnCount):
            value = random.randint(LowerBound, UpperBound)
            worksheet.write(0, column, column+1)
            worksheet.write(1, column, value)
        workbook.close()



def parse(argv):
    parser = argparse.ArgumentParser(description="""
     Parser of image and tables generator
        """, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('ChartsCount', action='store', type=int)
    parser.add_argument('BasePath', action='store', type=pathlib.Path)
    parser.add_argument('BaseName', action='store', type=str)

    return parser.parse_args(argv[1:])


def main():
    args = parse(sys.argv)
    generate(args)


main()

