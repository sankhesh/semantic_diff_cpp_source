#!/usr/bin/env python

import logging
import os
import subprocess
import sys

try:
    import argparse
except ImportError:
    import _argparse as argparse

if sys.platform == "win32":
    home = os.getenv('USERPROFILE')
else:
    home = os.getenv('HOME')

#------------------------------------------------------------------------------
# validate input
#------------------------------------------------------------------------------
def parse_tags(tag_file):
    with open(tag_file) as f:
        for line in f:
            if line

#------------------------------------------------------------------------------
# validate input
#------------------------------------------------------------------------------
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
    # Check if the versions provided are the same
    if options.versions[0] == options.versions[1]:
        logging.error("The versions provided to diff are the same")
        sys.exit(1)
    # Create temp directory if it does not exist
#    if not options.tmp:
#        logging.info("Creating temporary directory (~/tmp)")
#        tmp_dir = home + os.sep + "tmp"
#        options.tmp = tmp_dir
#    if not os.path.exists(options.tmp):
#        os.mkdir(tmp_dir)

#------------------------------------------------------------------------------
# Arguments parser
# -v, --versions    Two different versions to compare
# -t, --tmp         Temporary directory
# -l, --log         Log file
#------------------------------------------------------------------------------
def add_arguments(parser):
    parser.add_argument('-s', '--source', type=str)
    parser.add_argument("-v", "--versions", type=str, nargs=2, required=True,
        metavar=('old', 'new'), help="Versions to compare")
#    parser.add_argument("-t", "--tmp", type=str, default="",
#        help="Path for directory where temporary git checkouts will be made. "\
#             "The user should have write access to this directory. "\
#             "(default=~/tmp)")
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
    parse_tags(str(args.source))

if __name__ == "__main__":
    start()
