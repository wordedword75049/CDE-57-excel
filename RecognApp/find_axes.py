import numpy as np
import cv2
import sys
from find_text import find_text


def is_vertical(theta, delta=np.pi * 5e-3):
    return theta < delta


def is_horizontal(theta, delta=np.pi * 5e-3):
    return (theta > np.pi / 2 - delta) and (theta < np.pi / 2 + delta)


def get_vertical_axis(edges, part=3, delta=5e-3):
    """
    Функция находит вертикальную ось из предположения, что она вертикальна и левее всех прочих вертикальных линий
    Inputs:
    - edges: черно-белая картинка
    - part: минимальная доля размера оси от размера картинки возведенная в степень -1
    - delta: точность, с которой определяется угол (допустимое отличие от нуля)
    Outputs:
    - rho: расстояние от начала отсчета до линии
    - theta: угол между перпендикуляром к линии из начала отсчета и осью oX
    """
    # Функция, реализующая преобразование Хафа получает на вход ч/б картинку, точность определения rho в пикселях,
    # точность определения угла в радианах, минимальный порог чила пикселей на линии,
    # при котором линия попадет в output, в итоге возвращает массив из значений вида [[rho, theta]],
    # отсортированный по убыванию числа точек, соответствующих данной линии
    image_height, image_width = edges.shape
    lines = cv2.HoughLines(edges, 1, np.pi / 180, image_height // part)
    data_min = {}
    data_max = {}
    # min_shift - минимальное расстояние от границы картинки, при котором линия может считаться осью
    min_shift = image_width / 100
    # lines отсортирован по убыванию числа голосов,
    # меньший индекс в этом списке означает большее число голосов
    for i, [[rho, theta]] in enumerate(lines):
        if is_vertical(theta, delta):
            if ('rho' not in data_min or data_min['rho'] > rho) and rho > min_shift:
                data_min['rho'] = rho
                data_min['theta'] = theta
                data_min['i'] = i
            if ('rho' not in data_max or data_max['rho'] < rho) and rho < image_width - min_shift:
                data_max['rho'] = rho
                data_max['theta'] = theta
                data_max['i'] = i

    return [[data_min['rho'], data_min['theta']], [data_max['rho'], data_max['theta']]]


def get_horizontal_axis(edges, part=2, delta=5e-3):
    """
    Функция находит горизонтальную ось из предположения, что она горизонтальна и длиннее всех горизнотальных линий
    Inputs:
    - edges: черно-белая картинка
    - part: минимальная доля размера оси от размера картинки возведенная в степень -1
    - delta: точность, с которой определяется угол (допустимое отличие от нуля)
    Outputs:
    - rho: расстояние от начала отсчета до линии
    - theta: угол между перпендикуляром к линии из начала отсчета и осью oX
    """
    # Функция, реализующая преобразование Хафа получает на вход ч/б картинку, точность определения rho в пикселях,
    # точность определения угла в радианах, минимальный порог чила пикселей на линии,
    # при котором линия попадет в output, в итоге возвращает массив из значений вида [[rho, theta]],
    # отсортированный по убыванию числа точек, соответствующих данной линии
    image_height, image_width = edges.shape
    lines = cv2.HoughLines(edges, 1, np.pi / 180, image_width // part)

    # min_shift - минимальное расстояние от границы картинки, при котором линия может считаться осью
    min_shift = image_height / 100
    for [[rho, theta]] in lines:
        if is_horizontal(theta, delta) and image_height / 2 < rho < image_height - min_shift:
            return [[rho, theta]]

    return [[edges.shape[0], np.pi / 2]]


def draw_lines_on_image(img, lines):
    scale = 10 ** 3
    for [[rho, theta]] in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 - scale * b)
        y1 = int(y0 + scale * a)
        x2 = int(x0 + scale * b)
        y2 = int(y0 - scale * a)

        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)


def find_axes(name):
    img = cv2.imread(name)

    # Получаем черно-белую картинку
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Оставляем на картике только границы областей
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    lines = []

    vert = get_vertical_axis(edges)
    for line in vert:
        lines.append([line])

    hor = get_horizontal_axis(edges)
    for line in hor:
        lines.append([line])

    return lines
