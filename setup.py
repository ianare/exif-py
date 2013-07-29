#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "ExifRead",
    version = "1.3.1",
    author = "Ianaré Sévi",
    author_email = "ianare@gmail.com",
    packages = ["exifread"],
    scripts = ["EXIF.py"],
    url = "https://github.com/ianare/exif-py",
    license = "BSD",
    keywords = "exif image metadata photo",
    description = "Read Exif metadata from tiff and jpeg files.",
    long_description = open("README.rst", "rt").read(),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
)