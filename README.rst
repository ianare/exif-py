EXIF.py
=======

:Version: 1.3.3

Python library to extract EXIF data from tiff and jpeg files.

Originally written by Gene Cash / Thierry Bousch.

************
Installation
************

PyPI
****
This is the recomended process, it allows easily staying up to date.
::

    $ pip install exifread

See https://pypi.python.org/pypi/pip for more info.

Archive
*******
Download an archive from the releases page: https://github.com/ianare/exif-py/releases

Extract and enjoy.

*****
Usage
*****

Command line
************
::

$ EXIF.py image.jpg

Show command line options::

$ EXIF.py

Python Script
*************
::

    import exifread
    # Open image file for reading (binary mode)
    f = open(path_name, 'rb')

    # Return Exif tags
    tags = exifread.process_file(f)

*Note:* if you use this library in your project as a Git submodule, you may need to do::

    from <submodule_folder> import EXIF

or::

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


******************
Processing Options
******************

These options can be used both in command line mode and within a script.

Ignore MakerNote Tags
*********************
Pass the ``-q`` or ``--quick`` command line arguments, or as::

    tags = exifread.process_file(f, details=False)

Stop at Given Tag
*****************
To stop processing the file after a specified tag is retrieved.

Pass the ``-t TAG`` or ``--stop-tag TAG`` argument, or as::

    tags = exifread.process_file(f, stop_tag='TAG')

where ``TAG`` is a valid tag name, ex ``'DateTimeOriginal'``.

*The two above options are useful to speed up processing of large numbers of files.*

Strict Processing
*****************
Return an error on invalid tags instead of silently ignoring.

Pass the ``-s`` or ``--strict`` argument, or as::

    tags = exifread.process_file(f, strict=True)
