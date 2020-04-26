#libraries
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import argparse
import cv2
import numpy as np
import math
from collections import namedtuple
import random#import data

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


path = 'diagram_example.png'
num_clasters = 10
diagram_image = cv2.imread(path)
diagram_image = cv2.cvtColor(diagram_image, cv2.COLOR_BGR2RGB)
plt.figure()
plt.axis("off")
plt.imshow(diagram_image)
image = diagram_image
image = image.reshape((image.shape[0] * image.shape[1], 3))
clt = KMeans(num_clasters)
clt.fit(image)
hist = centroid_histogram(clt)
bar = plot_colors(hist, clt.cluster_centers_)
barhsv = cv2.cvtColor(bar, cv2.COLOR_RGB2HSV)
#выводим все цвета на картинке
plt.figure()
plt.axis("off")
plt.imshow(bar)
plt.show()
#выделяем цвета в отдельный массив
cluster = np.zeros((10, 3), dtype = int)
l = 0
for i in bar[-1]:
    if (cluster[np.max(l - 1, 0)][0] != i[0]):
        cluster[l] = i
        l += 1

img = diagram_image
boarder = [[[]]]
max_y = 0
for i in range(1, 10):
    color = cluster[i]
    R = int(color[0])
    G = int(color[1])
    B = int(color[2])
    low = (R - 10, G - 10, B - 10)
    high = (R + 10, G + 10, B + 10)
    new_picture = cv2.inRange(img, low, high)
    contours, hierarchy = cv2.findContours(new_picture.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        center = (int(rect[0][0]),int(rect[0][1]))
        area = int(rect[1][0]*rect[1][1])
        edge1 = np.int0((box[1][0] - box[0][0],box[1][1] - box[0][1]))
        edge2 = np.int0((box[2][0] - box[1][0], box[2][1] - box[1][1]))
        np.append(answer, box)
        usedEdge = edge1
        if cv2.norm(edge2) > cv2.norm(edge1):
            usedEdge = edge2
        reference = (1,0)
        a = reference[0]*usedEdge[0] + reference[1]*usedEdge[1]
        b = cv2.norm(reference) * cv2.norm(usedEdge)
        angle = 180.0/math.pi * math.acos(a / b)
        if area > 500 and area < 100000 and (angle == 90.0 or angle == 180.0 or angle == 0.0):
            boarder.append(box)
            if (max(box[0][1], max(box[1][1], max(box[2][1], box[3][1]))) > max_y):
                max_y =  max(box[0][1], max(box[1][1], max(box[2][1], box[3][1])))
boarder.remove([[]])
column = [[[]]]
for i in range(len(boarder)):
    cur = boarder[i]
    if (max(cur[0][1], max(cur[1][1], max(cur[2][1], cur[3][1]))) != max_y):
        column.append(cur)
        boarder[i] = [[]]
column.remove([[]])

distance = [[]]
for i in range(len(boarder)):
    cur_b = boarder[i]
    if(cur_b != [[]]):
        for j in range(len(column)):
            cur_c = column[j]
            if (cur_c != [[]]):
                min_x_boarder = min(cur_b[0][0], min(cur_b[1][0], min(cur_b[2][0], cur_b[3][0])))
                min_x_column = min(cur_c[0][0], min(cur_c[1][0], min(cur_c[2][0], cur_c[3][0])))
                max_x_boarder = max(cur_b[0][0], max(cur_b[1][0], max(cur_b[2][0], cur_b[3][0])))
                min_y_boarder = min(cur_b[0][1], min(cur_b[1][1], min(cur_b[2][1], cur_b[3][1])))
                min_y_column = min(cur_c[0][1], min(cur_c[1][1], min(cur_c[2][1], cur_c[3][1])))
                if (abs(min_x_column - min_x_boarder) < 2):
                    boarder[i][0][0] = min_x_boarder
                    boarder[i][1][0] = max_x_boarder
                    boarder[i][2][0] = max_x_boarder
                    boarder[i][3][0] = min_x_boarder
                    boarder[i][0][1] = max_y
                    boarder[i][1][1] = max_y
                    boarder[i][2][1] = min(min_y_boarder, min_y_column)
                    boarder[i][3][1] = min(min_y_boarder, min_y_column)
                    column[j] = [[]]
                    
for i in boarder:
    if (i != [[]]):
        cv2.drawContours(img,[i],0,(255,0,0),2)
        mid = min(i[0][0], min(i[2][0], min(i[3][0], i[1][0])))-10
        range_ = i[0][1] - i[3][1]
        mid_range = i[3][1]-15
        cv2.putText(img, "%d" % int( range_), (int(mid), int(mid_range)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

plt.imshow(img)