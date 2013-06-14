from setuptools import setup, find_packages
import sys, os

version = '1.2'

setup(name='exif-py',
      version=version,
      description="for metadata",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='exif metadaten',
      author='Peter Reimer',
      author_email='peter@4pi.org',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
