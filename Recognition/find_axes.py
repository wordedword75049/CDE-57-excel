import numpy as np
import cv2
import sys


def is_vertical(theta, delta=np.pi*5e-3):
    return theta < delta


def is_horizontal(theta, delta=np.pi*5e-3):
    return (theta > np.pi/2 - delta) and (theta < np.pi/2 + delta)


def get_vertical_axis(edges, part=3, delta=5e-3):
    lines = cv2.HoughLines(edges, 1, np.pi/180, edges.shape[0] // part)
    theta_min = None
    rho_min = None
    for [[rho, theta]] in lines:
        if is_vertical(theta, delta) and (not rho_min or (rho_min > rho)):
            theta_min = theta
            rho_min = rho
    return rho_min, theta_min


def get_horizontal_axis(edges, part=2, delta=5e-3):
    lines = cv2.HoughLines(edges, 1, np.pi/180, edges.shape[1] // part)
    for [[rho, theta]] in lines:
        if is_horizontal(theta, delta):
            return rho, theta
    return None, None


def draw_lines_on_image(img, lines):
    scale = 10**3
    for [[rho, theta]] in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 - scale*b)
        y1 = int(y0 + scale*a)
        x2 = int(x0 + scale*b)
        y2 = int(y0 - scale*a)

        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)


def find_axes(name):
    img = cv2.imread(name)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    lines = []

    rho_vert, theta_vert = get_vertical_axis(edges)
    lines.append([[rho_vert, theta_vert]])

    rho_hor, theta_hor = get_horizontal_axis(edges)
    lines.append([[rho_hor, theta_hor]])

    draw_lines_on_image(img, lines)

    cv2.imshow('image', img)
    cv2.waitKey(0)


find_axes(sys.argv[1])
