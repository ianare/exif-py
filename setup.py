#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from exifread import __version__

readme_file = open("README.rst", "rt").read()


setup(
    name = "ExifRead",
    version = __version__,
    author = "Ianaré Sévi",
    author_email = "ianare@gmail.com",
    packages = ["exifread", "exifread.tags"],
    scripts = ["EXIF.py"],
    url = "https://github.com/ianare/exif-py",
    license = "BSD",
    keywords = "exif image metadata photo",
    description = "Read Exif metadata from tiff and jpeg files.",
    long_description = readme_file,
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
