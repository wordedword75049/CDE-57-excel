import argparse
import os
import time
import xml.etree.ElementTree as ET
import cv2
import sys

from AbbyyOnlineSdk import *

processor = None


def setup_processor():
    if "ABBYY_APPID" in os.environ:
        processor.ApplicationId = os.environ["ABBYY_APPID"]

    if "ABBYY_PWD" in os.environ:
        processor.Password = os.environ["ABBYY_PWD"]

    # Proxy settings
    if "http_proxy" in os.environ:
        proxy_string = os.environ["http_proxy"]
        print("Using http proxy at {}".format(proxy_string))
        processor.Proxies["http"] = proxy_string

    if "https_proxy" in os.environ:
        proxy_string = os.environ["https_proxy"]
        print("Using https proxy at {}".format(proxy_string))
        processor.Proxies["https"] = proxy_string


# Recognize a file at filePath and save result to resultFilePath
def recognize_file(file_path, result_file_path, language, output_format, region):
    print("Uploading..")
    settings = ProcessingSettings()
    settings.Language = language
    settings.OutputFormat = output_format
    task = processor.process_image(file_path, settings, region)
    if task is None:
        print("Error")
        return
    if task.Status == "NotEnoughCredits":
        print("Not enough credits to process the document. Please add more pages to your application's account.")
        return

    # print("Id = {}".format(task.Id))
    # print("Status = {}".format(task.Status))

    # Wait for the task to be completed
    print("Waiting..")
    # Note: it's recommended that your application waits at least 2 seconds
    # before making the first getTaskStatus request and also between such requests
    # for the same task. Making requests more often will not improve your
    # application performance.
    # Note: if your application queues several files and waits for them
    # it's recommended that you use listFinishedTasks instead (which is described
    # at https://ocrsdk.com/documentation/apireference/listFinishedTasks/).

    while task.is_active():
        time.sleep(5)
        print(".")
        task = processor.get_task_status(task)

    print("Status = {}".format(task.Status))

    if task.Status == "Completed":
        if task.DownloadUrl is not None:
            processor.download_result(task, result_file_path)
            # print("Result was written to {}".format(result_file_path))
    else:
        print("Error processing task")


def parse_xml(target):
    tree = ET.parse(target)
    root = tree.getroot()
    return [line.attrib for line in root.iter('{@link}line')], \
        len([char for char in root.iter('{@link}char')]),\
        [''.join([char.text for char in line.iter('{@link}char')]) for line in root.iter('{@link}line')]


def draw_rectangles(img, bounds):
    for b in bounds:
        for rectangle in b:
            cv2.rectangle(img,
                          (int(rectangle['left']), int(rectangle['top'])),
                          (int(rectangle['right']), int(rectangle['bottom'])),
                          (0, 255, 0),
                          2)


def find_text(source_file, axes, language="English", output_format="xml", target_file = "result.xml"):
    global processor
    processor = AbbyyOnlineSdk()

    setup_processor()

    img = cv2.imread(source_file)

    max_y, max_x = img.shape[:2]
    min_y, min_x = 0, 0
    # отсутп от границ, нужен для корректной работы с регионами
    shift = 1
    min_x += shift
    min_y += shift
    max_x -= shift
    max_y -= shift

    left_region = [str(elem) for elem in [min_x, min_y, axes['left'], max_y]]
    right_region = [str(elem) for elem in [axes['right'], min_y, max_x, max_y]]
    bottom_region = [str(elem) for elem in [min_x, axes['bottom'], max_x, max_y]]

    regions = [', '.join(left_region),
               ', '.join(right_region),
               ', '.join(bottom_region)]

    if os.path.isfile(source_file):
        bounds = []
        counts = []
        text = []
        for region in regions:
            recognize_file(source_file, target_file, language, output_format, region)
            bound, count, line = parse_xml(target_file)
            target_file += '___.xml'
            bounds.append(bound)
            counts.append(count)
            text.append(line)
        #os.remove(target_file)
        return bounds, counts, text
    else:
        print("No such file: {}".format(source_file))