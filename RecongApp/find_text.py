#!/usr/bin/python

# Usage: find_text.py <input file> <output file> [-l <Language>] [-pdf|-txt|-rtf|-docx|-xml]

import argparse
import os
import time
import xml.etree.ElementTree as ET
import cv2

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
def recognize_file(file_path, result_file_path, language, output_format):
    print("Uploading..")
    settings = ProcessingSettings()
    settings.Language = language
    settings.OutputFormat = output_format
    task = processor.process_image(file_path, settings)
    if task is None:
        print("Error")
        return
    if task.Status == "NotEnoughCredits":
        print("Not enough credits to process the document. Please add more pages to your application's account.")
        return

    print("Id = {}".format(task.Id))
    print("Status = {}".format(task.Status))

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
            print("Result was written to {}".format(result_file_path))
    else:
        print("Error processing task")


def create_parser():
    parser = argparse.ArgumentParser(description="Recognize a file via web service")
    parser.add_argument('source_file')
    parser.add_argument('target_file')

    parser.add_argument('-l', '--language', default='English', help='Recognition language (default: %(default)s)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-txt', action='store_const', const='txt', dest='format', default='txt')
    group.add_argument('-pdf', action='store_const', const='pdfSearchable', dest='format')
    group.add_argument('-rtf', action='store_const', const='rtf', dest='format')
    group.add_argument('-docx', action='store_const', const='docx', dest='format')
    group.add_argument('-xml', action='store_const', const='xml', dest='format')

    return parser


def parse_xml(target):
    tree = ET.parse(target)
    root = tree.getroot()
    return [line.attrib for line in root.iter('{@link}line')]


def draw_rectangles(img, bounds):
    for rectangle in bounds:
        pos = [int(rectangle['left']),
               int(rectangle['top']),
               int(rectangle['right']),
               int(rectangle['bottom'])]
        n = len(pos)
        # draw all possible combinations
        for i in range(n):
            if i % 2 == 0:
                cv2.line(img,
                         (pos[i], pos[(i + 1) % n]),
                         (pos[i], pos[(i + 3) % n]),
                         (0, 255, 0),
                         2)
            else:
                cv2.line(img,
                         (pos[(i + 1) % n], pos[i]),
                         (pos[(i + 3) % n], pos[i]),
                         (0, 255, 0),
                         2)


def main():
    global processor
    processor = AbbyyOnlineSdk()

    setup_processor()

    args = create_parser().parse_args()

    source_file = args.source_file
    img = cv2.imread(source_file)
    target_file = args.target_file
    language = args.language
    output_format = args.format

    if os.path.isfile(source_file):
        recognize_file(source_file, target_file, language, output_format)
        bounds = parse_xml(target_file)
        draw_rectangles(img, bounds)
    else:
        print("No such file: {}".format(source_file))

    cv2.imshow('image', img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
