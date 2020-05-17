#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import pprint
import shutil
import optparse
import tempfile

from bootstrap.unittesting import TestLoader, TextTestRunner
from bootstrap.ext.os_data import GRAINS
from bootstrap.ext.HTMLTestRunner import HTMLTestRunner
try:
    from bootstrap.ext import console
    width, height = console.getTerminalSize()
    PNUM = width
except:
    PNUM = 70

try:
    import xmlrunner
except ImportError:
    xmlrunner = None


TEST_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_RESULTS = []
XML_OUTPUT_DIR = os.environ.get(
    'XML_TEST_REPORTS', os.path.join(
        tempfile.gettempdir(), 'xml-test-reports'
    )
)
HTML_OUTPUT_DIR = os.environ.get(
    'HTML_OUTPUT_DIR', os.path.join(
        tempfile.gettempdir(), 'html-test-results'
    )
)


def run_suite(opts, path, display_name, suffix='[!_]*.py'):

    loader = TestLoader()
    if opts.name:
        tests = loader.loadTestsFromName(display_name)
    else:
        tests = loader.discover(path, suffix, TEST_DIR)

    header = '{0} Tests'.format(display_name)
    print_header('Starting {0}'.format(header))

    if opts.xmlout:
        if not os.path.isdir(XML_OUTPUT_DIR):
            os.makedirs(XML_OUTPUT_DIR)
        runner = xmlrunner.XMLTestRunner(
            output=XML_OUTPUT_DIR,
            verbosity=opts.verbosity
        ).run(tests)
    elif opts.html_out:
        if not os.path.isdir(HTML_OUTPUT_DIR):
            os.makedirs(HTML_OUTPUT_DIR)
        runner = HTMLTestRunner(
            stream=open(
                os.path.join(
                    HTML_OUTPUT_DIR, 'bootstrap_{0}.html'.format(
                        header.replace(' ', '_')
                    )
                ),
                'w'
            ),
            verbosity=opts.verbosity,
            title=header,
        ).run(tests)
        TEST_RESULTS.append((header, runner))
    else:
        runner = TextTestRunner(
            verbosity=opts.verbosity
        ).run(tests)
        TEST_RESULTS.append((header, runner))
    return runner.wasSuccessful()


def run_integration_suite(opts, display_name, suffix='[!_]*.py'):

    path = os.path.join(TEST_DIR, 'bootstrap')
    return run_suite(opts, path, display_name, suffix)

if __name__ == '__main__':
    main()
