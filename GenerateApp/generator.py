import sys
import argparse
import pathlib
import xlsxwriter
import random
import os


def generate(args):
    # Create an new Excel file and add a worksheet.
    #print(args.ChartsCount)
    if not os.access(str(args.BasePath), os.F_OK):
              os.mkdir(str(args.BasePath))
    os.chdir(str(args.BasePath))
    for iteration in range(args.ChartsCount):
        random.seed()
        ColumnCount = random.randint(5, 10)
        #print('In table number ' + str(iteration+1))
        workbook = xlsxwriter.Workbook('Table'+str(iteration+1)+'.xlsx')
        worksheet = workbook.add_worksheet()
        #print('Got ' + str(ColumnCount)+' columns ')
        LowerBound = random.randint(100, 500)
        UpperBound = random.randint(600, 1000)
        #print('Values will be between '+str(LowerBound)+' and '+str(UpperBound))
        for column in range(ColumnCount):
            value = random.randint(LowerBound, UpperBound)
            #print('Value for column number '+str(column+1)+' is '+str(value))
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

