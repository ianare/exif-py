#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Library to extract Exif information from digital camera image files.
# https://github.com/ianare/exif-py
#
#
# Copyright (c) 2002-2007 Gene Cash
# Copyright (c) 2007-2013 Ianaré Sévi and contributors
#
# See LICENSE.txt file for licensing information
# See CHANGES.txt file for all contributors and changes
#

import sys
import getopt
import logging
import timeit
from exifread.tags import DEFAULT_STOP_TAG, FIELD_TYPES
from exifread import process_file

logger = logging.getLogger('exifread')

def usage(exit_status):
    """Show command line usage."""
    msg = 'Usage: EXIF.py [OPTIONS] file1 [file2 ...]\n'
    msg += 'Extract EXIF information from digital camera image files.\n\nOptions:\n'
    msg += '-h --help               Display usage information and exit.\n'
    msg += '-v --version            Display version information and exit.\n'
    msg += '-q --quick              Do not process MakerNotes.\n'
    msg += '-t TAG --stop-tag TAG   Stop processing when this tag is retrieved.\n'
    msg += '-s --strict             Run in strict mode (stop on errors).\n'
    msg += '-d --debug              Run in debug mode (display extra info).\n'
    print(msg)
    sys.exit(exit_status)


def show_version():
    readme_file = open("README.rst", "rt").read()
    v_index = readme_file.index(":Version:") + 10
    version = readme_file[v_index:v_index + 5]
    print('Version %s' % version)
    sys.exit(0)


def main():
    # parse command line options/arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvqsdct:v", ["help", "version", "quick", "strict", "debug", "stop-tag="])
    except getopt.GetoptError:
        usage(2)

    detailed = True
    stop_tag = DEFAULT_STOP_TAG
    debug = False
    strict = False
    color = False

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(0)
        if o in ("-v", "--version"):
            show_version()
        if o in ("-q", "--quick"):
            detailed = False
        if o in ("-t", "--stop-tag"):
            stop_tag = a
        if o in ("-s", "--strict"):
            strict = True
        if o in ("-d", "--debug"):
            debug = True

    if args == []:
        usage(2)

    ## Configure the logger
    if debug:
        log_level = logging.DEBUG
        log_format = '%(levelname)-5s  %(message)s'
    else:
        log_level = logging.INFO
        log_format = '%(message)s'
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(log_format))
    logger.setLevel(log_level)
    ch.setLevel(log_level)
    logger.addHandler(ch)

    # output info for each file
    for filename in args:
        file_start = timeit.default_timer()
        try:
            file = open(str(filename), 'rb')
        except:
            logger.error("'%s' is unreadable", filename)
            continue
        logger.info("Opening: %s", filename)

        tag_start = timeit.default_timer()

        # get the tags
        data = process_file(file, stop_tag=stop_tag, details=detailed, strict=strict, debug=debug)

        tag_stop = timeit.default_timer()

        if not data:
            logger.warning("No EXIF information found\n")
            continue

        if 'JPEGThumbnail' in data:
            logger.info('File has JPEG thumbnail')
            del data['JPEGThumbnail']
        if 'TIFFThumbnail' in data:
            logger.info('File has TIFF thumbnail')
            del data['TIFFThumbnail']

        tag_keys = data.keys()
        tag_keys.sort()

        for i in tag_keys:
            try:
                logger.info('%s (%s): %s', i, FIELD_TYPES[data[i].field_type][2], data[i].printable)
            except:
                logger.error("%s : %s", i, str(data[i]))

        file_stop = timeit.default_timer()

        logger.debug("Tags processed in %s seconds", tag_stop - tag_start)
        logger.debug("File processed in %s seconds", file_stop - file_start)
        print("")


if __name__ == '__main__':
    main()
