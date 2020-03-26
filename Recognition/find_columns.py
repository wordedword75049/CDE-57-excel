import sys
import argparse
from pathlib import Path
import numpy
import cv2


def find_mask(image):
    hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    light_white = (0, 0, 200)
    dark_white = (145, 60, 255)

    mask_white = cv2.inRange(hsv_img, light_white, dark_white)

    img_res_mask = 255 * numpy.ones(mask_white.shape) - mask_white
    return img_res_mask


def find_columns(name):
    pass
