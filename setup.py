from setuptools import setup, find_packages
import exifread

readme_file = open("README.rst", "rt").read()

dev_requirements = [
    "mypy==0.950",
    "pylint==2.13.8",
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
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    extras_require={
        "dev": dev_requirements,
    },
)
