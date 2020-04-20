#libraries
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import argparse
import cv2
import numpy as np
from collections import namedtuple
from math import sqrt
import random

def centroid_histogram(clt):
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins = numLabels)
    hist = hist.astype("float")
    hist /= hist.sum()
    return hist

def plot_colors(hist, centroids):
    bar = np.zeros((50, 300, 3), dtype = "uint8")
    startX = 0
    for (percent, color) in zip(hist, centroids):
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
            color.astype("uint8").tolist(), -1)
        startX = endX
    return bar

diagram_image = cv2.imread('diagram_example.png')
num_clasters = 2
diagram_image = cv2.cvtColor(diagram_image, cv2.COLOR_BGR2RGB)
image = diagram_image
image = image.reshape((image.shape[0] * image.shape[1], 3))
clt = KMeans(num_clasters)
clt.fit(image)

hist = centroid_histogram(clt)
bar = plot_colors(hist, clt.cluster_centers_)
barhsv = cv2.cvtColor(bar, cv2.COLOR_RGB2HSV)
if (bar[0, 0, 0] > 250):
    color = bar[-1, -1]
else:
    color = bar[0, 0]
hsv_diagram_image = cv2.cvtColor(diagram_image, cv2.COLOR_RGB2HSV)
H = color[0]
V = color[2]
S = color[1]
R = int(color[0])
G = int(color[1])
B = int(color[2])
low = (R - 30, G - 30, B - 30)
high = (R + 30, G + 30, B + 30)
new_picture = cv2.inRange(diagram_image, low, high)
plt.imshow(new_picture)