"""EXIF.py setup"""

from setuptools import find_packages, setup  # pylint: disable=import-error

import exifread

with open("README.rst", "rt", encoding="utf-8") as fh:
    readme_file = fh.read()

dev_requirements = [
    "pre-commit==2.21.0",
    "pylint==3.0.4",
]

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
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    extras_require={
        "dev": dev_requirements,
    },
)
