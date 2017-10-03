*******
EXIF.py
*******

.. image:: https://travis-ci.org/ianare/exif-py.png
        :target: https://travis-ci.org/ianare/exif-py

Easy to use Python module to extract Exif metadata from tiff and jpeg files.

Originally written by Gene Cash & Thierry Bousch.


Installation
************

PyPI
====
The recommended process is to install the `PyPI package <https://pypi.python.org/pypi/ExifRead>`_,
as it allows easily staying up to date::

    $ pip install exifread

See the `pip documentation <https://pip.pypa.io/en/latest/user_guide.html>`_ for more info.

Archive
=======
Download an archive from the project's `releases page <https://github.com/ianare/exif-py/releases>`_.

Extract and enjoy.


Compatibility
*************

EXIF.py is tested on the following Python versions:

- 2.6
- 2.7
- 3.3
- 3.4
- 3.5


Usage
*****

Command line
============

Some examples::

    $ EXIF.py image1.jpg
    $ EXIF.py image1.jpg image2.tiff
    $ find ~/Pictures -name "*.jpg" -name "*.tiff" | xargs EXIF.py

Show command line options::

    $ EXIF.py

Python Script
=============
::

    import exifread
    # Open image file for reading (binary mode)
    f = open(path_name, 'rb')

    # Return Exif tags
    tags = exifread.process_file(f)

*Note:* To use this library in your project as a Git submodule, you should::

    from <submodule_folder> import exifread

Returned tags will be a dictionary mapping names of Exif tags to their
values in the file named by path_name.
You can process the tags as you wish. In particular, you can iterate through all the tags with::

    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print "Key: %s, value %s" % (tag, tags[tag])

An ``if`` statement is used to avoid printing out a few of the tags that tend to be long or boring.

The tags dictionary will include keys for all of the usual Exif tags, and will also include keys for
Makernotes used by some cameras, for which we have a good specification.

Note that the dictionary keys are the IFD name followed by the tag name. For example::

    'EXIF DateTimeOriginal', 'Image Orientation', 'MakerNote FocusMode'


Tag Descriptions
****************

Tags are divided into these main categories:

- ``Image``: information related to the main image (IFD0 of the Exif data).
- ``Thumbnail``: information related to the thumbnail image, if present (IFD1 of the Exif data).
- ``EXIF``: Exif information (sub-IFD).
- ``GPS``: GPS information (sub-IFD).
- ``Interoperability``: Interoperability information (sub-IFD).
- ``MakerNote``: Manufacturer specific information. There are no official published references for these tags.


Processing Options
******************

These options can be used both in command line mode and within a script.

Faster Processing
=================

Don't process makernote tags, don't extract the thumbnail image (if any).

Pass the ``-q`` or ``--quick`` command line arguments, or as::

    tags = exifread.process_file(f, details=False)

Stop at a Given Tag
===================

To stop processing the file after a specified tag is retrieved.

Pass the ``-t TAG`` or ``--stop-tag TAG`` argument, or as::

    tags = exifread.process_file(f, stop_tag='TAG')

where ``TAG`` is a valid tag name, ex ``'DateTimeOriginal'``.

*The two above options are useful to speed up processing of large numbers of files.*

Strict Processing
=================

Return an error on invalid tags instead of silently ignoring.

Pass the ``-s`` or ``--strict`` argument, or as::

    tags = exifread.process_file(f, strict=True)

Usage Example
=============

This example shows how to use the library to correct the orientation of an image (using PIL for the transformation) before e.g. displaying it.

::

    import exifread
    from PIL import Image
    
    def _read_img_and_correct_exif_orientation(path):
        im = Image.open(path)
        tags = {}
        with open(path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        if "Image Orientation" in tags.keys():
            orientation = tags["Image Orientation"]
            logging.debug("Orientation: %s (%s)", orientation, orientation.values)
            val = orientation.values
            if 5 in val:
                val += [4,8]
            if 7 in val:
                val += [4, 6]
            if 3 in val:
                logging.debug("Rotating by 180 degrees.")
                im = im.transpose(Image.ROTATE_180)
            if 4 in val:
                logging.debug("Mirroring horizontally.")
                im = im.transpose(Image.FLIP_TOP_BOTTOM)
            if 6 in val:
                logging.debug("Rotating by 270 degrees.")
                im = im.transpose(Image.ROTATE_270)
            if 8 in val:
                logging.debug("Rotating by 90 degrees.")
                im = im.transpose(Image.ROTATE_90)

        return im
