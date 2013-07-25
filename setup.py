#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='ExifRead',
    version='1.3.0',
    author='Ianaré Sévi',
    author_email='ianare@gmail.com',
    packages=['exifread'],
    scripts=['EXIF.py'],
    url='http://pypi.python.org/pypi/ExifRead/',
    license='BSD',
    description='Extract Exif data from tiff and jpeg files.',
    long_description='Easy to use library to extract Exif data from tiff and jpeg files.'
)