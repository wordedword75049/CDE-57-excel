#-------------------------

#ГЛОБАЛЬНЫЕ ПАРАМЕТРЫ ГЕНЕРАТОРА

#базовый размер создаваемой диаграммы в excel. Этот параметр задан библиотекой xlsxwriter
DiagramSize = 480

#вручную подобранный коэффициент для ширины "чистой" области графика диаграммы(без осей)
PurePlotWidth = 0.94

#параметры для увеличения размера диаграммы и шрифта подписей при большом числе столбцов
#с ростом количества столбцов увеличение диаграммы сильно улучшает ее читаемость
ScalingCounterWidth = 20
ScalingCounterFontSize = 30
ScalingMultiplier = 0.5

#начальный размер шрифта подписей оси х
BaseFontSize = 6.5

#шрифт для подписей
LabelsFontName = 'Arial'

#нижняя граница рандома при выборе количества столбцов на диаграмме
MinColumnNumber = 5

#границы рандома при выборе нижней границы значений диаграммы
RandLowLowerBound = 100
RandLowUpperBound = 500

#границы рандома при выборе верхней границы значенийдиаграммы
RandUpLowerBound = 600
RandUpUpperBound = 1000

#-------------------------

import argparse
import os
import pathlib
import random
import sys
import xlsxwriter
import csv
import win32com.client as win32
import tkinter
from tkinter import font as tkFont

def string_width(string, font_size): #определяет длину строки относительно кегеля и шрифта. Источник: https://stackoverflow.com/questions/32555015/how-to-get-the-visual-length-of-a-text-string-in-python
    tkinter.Frame().destroy()
    font_settings = tkFont.Font(family=LabelsFontName, size=int(font_size))
    width = font_settings.measure(string)
    return width                     #возвращает результат в пикселях(наиболее удобный формат)


def read_csv(rowNumber, filename):
    csv_path = filename
    extracted_data = []
    with open(csv_path, "r") as f_obj:
        reader = csv.reader(f_obj)
        for row in reader:
            extracted_data.append(row[rowNumber])
    return extracted_data

def generate_labels(size, textmode): #генеррует подписи для диаграммы случайным образом
    labels = []
    random.seed()
    mode = random.randint(1, 4) #случайный выбор режима подписей
    if mode == 1:   #числа от 1 до ColumnCount
        labels = list(range(1, size+1))
    elif mode == 2:  #названия существующих организаций
        data = read_csv(textmode, "res\constituents.csv")
        labels = random.sample(data[1:], size)
    elif mode == 3:   #номера годов (не может быть больше 2020)
        start_year = random.randint(2010, 2020)
        labels = list(range(start_year-size, start_year))
    elif mode == 4:    #месяц и номер года (не может быть больше 2020)
        months = read_csv(textmode, "res\months.csv")
        start_year = random.randint(2010-(size // 12), 2020-(size // 12))
        start_month = random.randint(1,12)
        for i in range(size):
            if textmode == 0:
                labels.append(str(months[(start_month + i) % 12]) + "." + str(start_year + ((start_month + i) // 12)))
            elif textmode == 1:
                labels.append(str(months[(start_month + i) % 12]) + " " + str(start_year+((start_month + i) // 12)))

    return labels

def set_label_orientation(mode, base_width, labels, size): #задает положение подписей в диаграмме
    if mode == 1:  #если выбран вертикальный режим
        return -90    #возвращаем угол поворота на 90 градусов
    else:
        for label in labels:  #проходим по всем подписям одной диаграммы
            toStr = str(label)
            words = toStr.split()  #делим подписи на слова (может быть больше 1 слова)
            for each_word in words:   #проверяем, что каждое слово из подписи
                if string_width(each_word, size) > (base_width - 10): #не превосходит предоставленной ширины столбца с учетом отступа
                    return -90 #если превосходит, то возвращаем угол поворота на 90 градусов
        return 0 #если все подписи достаточно короткие, то текст не будет повернут

def create_table(path, MaxColumnNumber, textmode):
    random.seed()
    ColumnCount = random.randint(MinColumnNumber, MaxColumnNumber)
    full_path = str(path) + '\source.xlsx'
    workbook = xlsxwriter.Workbook(full_path )

    worksheet = workbook.add_worksheet()
    LowerBound = random.randint(RandLowLowerBound, RandLowUpperBound)
    UpperBound = random.randint(RandUpLowerBound, RandUpLowerBound)
    x_label = generate_labels(ColumnCount, textmode[0])
    for column in range(ColumnCount):
        value = random.randint(LowerBound, UpperBound)
        worksheet.write(column, 0, x_label[column])
        worksheet.write(column, 1, value)

    chart = workbook.add_chart({'type': 'column'})
    colors = read_csv(0, "res\colors.csv")
    selected_color = random.choice(colors)
    chart.add_series({
        'categories': '=Sheet1!$A$1:$A$' + str(ColumnCount),
        'values': '=Sheet1!$B$1:$B$' + str(ColumnCount),
        'fill': {'color': selected_color},
    })
    chart.set_y_axis({
        'major_gridlines': {'visible': True,
                            'line': {'width': 0.5, 'color': 'black'},}
    })
    plotarea_width = PurePlotWidth * (1 + ScalingMultiplier * (ColumnCount // ScalingCounterWidth)) * DiagramSize #подсчет "чистой" ширины диаграммы с учетом увеличений
    eachcol_width = plotarea_width // ColumnCount #подсчет ширины одного столбика
    font_size = BaseFontSize * (1 + ScalingMultiplier*(ColumnCount//ScalingCounterFontSize)) #подсчет размера шрифта с учетом увеличения
    chart.set_x_axis({
        'num_font': {
            'name': LabelsFontName,
            'rotation': set_label_orientation(textmode[1], eachcol_width, x_label, font_size), #угол поворота текста вычисляется в функции set_label_orientation
            'size': font_size,
        }
    })
    chart.set_legend({'none': True})
    chart.set_size({'x_scale': (1 + ScalingMultiplier * (ColumnCount // ScalingCounterWidth)), #задаем размер диаграммы с учетом увеличения
                    'y_scale': (1 + ScalingMultiplier * (ColumnCount // ScalingCounterWidth))})
    worksheet.insert_chart('D3', chart)
    workbook.close()

def export_image(path):
    app = win32.Dispatch('Excel.Application')
    workbook_file_name = str(path) +  '\\source.xlsx'
    workbook = app.Workbooks.Open(Filename=workbook_file_name)
    app.DisplayAlerts = False

    for sheet in workbook.Worksheets:
        for chartObject in sheet.ChartObjects():
            chartObject.Activate()
            image_file_name=str(path) +  '\\image.png'
            chartObject.Chart.Export(image_file_name)
    workbook.Close(SaveChanges=False, Filename=workbook_file_name)


def generate(args):
    if args.TextMode == "short":
        mode = 0
    elif args.TextMode == "long":
        mode = 1
    if args.TextLayout == "horizontal":
        turn = 0
    elif args.TextLayout == "vertical":
        turn = 1
    dirpath = os.path.join(args.BasePath, args.BaseName + '\\Data')
    if not os.access(str(dirpath), os.F_OK):
        os.makedirs(str(dirpath))
    for iteration in range(args.ChartsCount):
        iteration_path = os.path.join(dirpath, str(iteration+1))
        if not os.access(iteration_path, os.F_OK):
            os.makedirs(iteration_path)
        create_table(iteration_path, args.MaxColumnsCount, (mode, turn))
        export_image(iteration_path)



def parse(argv):
    parser = argparse.ArgumentParser(description="""
     Parser of image and tables generator
        """, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('BasePath', action='store', type=pathlib.Path)
    parser.add_argument('BaseName', action='store', type=str)
    parser.add_argument('ChartsCount', action='store', type=int)
    parser.add_argument('MaxColumnsCount', action='store', type=int)
    parser.add_argument('TextMode', action='store', type=str)
    parser.add_argument('TextLayout', action='store', type=str)

    return parser.parse_args(argv[1:])


def main():
    args = parse(sys.argv)
    generate(args)


main()