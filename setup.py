#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

readme_file = open("README.rst", "rt").read()

v_index = readme_file.index(":Version:") + 10
version = readme_file[v_index:v_index + 5]

setup(
    name = "ExifRead",
    version = version,
    author = "Ianaré Sévi",
    author_email = "ianare@gmail.com",
    packages = ["exifread"],
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