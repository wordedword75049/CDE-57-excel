import color_recogn
import find_axes
import find_text
import parse_text
import column
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import argparse
import cv2
import xlsxwriter
import numpy as np
import math
from collections import namedtuple
import random
import sys


def coordinate_key(person):
    return person.x_coordinate

def x_val_for_column(array_of_column):
    a = sorted(array_of_column, key=coordinate_key)
    cur = ''
    count = 0
    for j in text[-1][0]:
        if (j != ' '):
            cur += j
        else:
            a[count].x_val = cur
            count += 1
            cur = ''
    a[count].x_val = cur
    return a


def table_creation(data):
    full_path = "./" + sys.argv[1].split(".")[0] + ".xlsx"
    workbook = xlsxwriter.Workbook(full_path)

    worksheet = workbook.add_worksheet()
    for column in range(len(data)):
        worksheet.write(column, 0, data[column].x_val)
        worksheet.write(column, 1, data[column].y_val)
    workbook.close()

color_black = (0, 0, 0)
#нахождение границ столбиков
diagram_image = cv2.imread(sys.argv[1])
boarder = color_recogn.recogn_column(diagram_image, 10)
#нахождение осей
lines = find_axes.find_axes(sys.argv[1])

axes = {'left': int(lines[0][0][0]),
        'right': int(lines[1][0][0]),
        'bottom': int(lines[2][0][0])}
#нахождение текста на диаграммах
bounds, counts, text = find_text.find_text(sys.argv[1], axes, language='English')
if counts[1] > counts[0]:
    lines.pop(0)
    bounds.pop(0)
    text.pop(0)
else:
    lines.pop(1)
    bounds.pop(1)
    text.pop(1)



#отрисовка
find_axes.draw_lines_on_image(diagram_image, lines)
find_text.draw_rectangles(diagram_image, bounds)
array_of_column = color_recogn.drow_boarder(diagram_image, boarder)

#заполнение значений столбиков
final_answer_column = x_val_for_column(array_of_column)


parse_text.set_coefficients(bounds[0], text[0])

for i in range(len(final_answer_column)):
    final_answer_column[i].y_val = parse_text.get_value(final_answer_column[i].y_coordinate)

#печать всех столбиков и их значение в консоль
for i in range(len(final_answer_column)):
    print('№', i, '| название', final_answer_column[i].x_val, '| знаечние', final_answer_column[i].y_val, '\n')
table_creation(final_answer_column)


#печать финального ответа на изображение
for i in final_answer_column:
    cv2.putText(diagram_image, i.y_val, (int(i.x_coordinate + 10), int(i.y_coordinate-10)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        color_black, 2)

cv2.imshow('image', diagram_image)
cv2.waitKey(0)