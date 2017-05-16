#!/usr/bin/python

import sys

import exifread


# Open image file for reading (binary mode)
with open(sys.argv[1], 'rb') as stream:
    # Return Exif tags
    tags = exifread.process_file(stream)
    for name, value in tags.items():
        print "{name}: {value}".format(name=name, value=value)
    # Close stream
    stream.close()
