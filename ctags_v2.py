#!/usr/bin/env python

import logging
import os
import sys

try:
    import pyctags
except ImportError:
    message = "This script requires that pyctags be installed on the "\
              "system. (\'pip install pyctags\')"
    raise ImportError(message)

try:
    import argparse
except ImportError:
    import _argparse as argparse

if sys.platform == "win32":
    home = os.getenv('USERPROFILE')
else:
    home = os.getenv('HOME')
#-----------------------------------------------------------------------------
# validate input versions
#-----------------------------------------------------------------------------
def validate_input(options):
    global home
    # Start logging
    formatting = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=formatting)
    if options.log:
        file_handler = logging.FileHandler(options.log)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(formatting)
        file_handler.setFormatter(formatter)
        logging.getLogger('').addHandler(file_handler)

    if not options.tmp:
        logging.info("Creating temporary directory (~/tmp)")
        tmp_dir = home + os.sep + "tmp"
        if os.path.exists(tmp_dir):

#
#    if options.old == options.new:

#-----------------------------------------------------------------------------
# Arguments parser
# -v, --versions    Two different versions to compare
# -t, --tmp         Temporary directory
# -l, --log         Log file
#-----------------------------------------------------------------------------

def add_arguments(parser):
    parser.add_argument("-v", "--versions", type=str, nargs=2, required=True,
        metavar=('old', 'new'), help="Versions to compare")
    parser.add_argument("-t", "--tmp", type=str, default="",
        help="Path for directory where temporary git checkouts will be made. "\
             "The user should have write access to this directory. "\
             "(default=~/tmp)")
    parser.add_argument("-l", "--log", type=str, default="",
        help="Log output to this file (default=None)")
    return parser

def start(argv=None,
        description="Get semantically aware differences between two source "\
                "tree versions"):
    parser = argparse.ArgumentParser(description=description)
    add_arguments(parser)
    args = parser.parse_args(argv)
    validate_input(args)

if __name__ == "__main__":
    start()
