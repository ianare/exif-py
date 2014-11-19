# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import exifread

readme_file = open("README.rst", "rt").read()

setup(
    name="ExifRead",
    version=exifread.__version__,
    author="Ianaré Sévi",
    author_email="ianare@gmail.com",
    packages=find_packages(),
    scripts=["EXIF.py"],
    url="https://github.com/ianare/exif-py",
    license="BSD",
    keywords="exif image metadata photo",
    description=" ".join(exifread.__doc__.splitlines()).strip(),
    long_description=readme_file,
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Utilities",
    ),
)
