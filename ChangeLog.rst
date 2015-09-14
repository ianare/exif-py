**********
Change Log
**********

2.1.2 — 2015-09-14
    * Fix 90 CW (6) and Rotated 90 CCW (8) which were swapped with each other (Mark Hahnenberg)
    * Catch memory and overflow errors on file seek, print a warning
    * Put manufacturers' makernote definitions in separate files

2.1.1 — 2015-05-16
    * Add a CONTRIBUTING file for Github.
    * Add some FujiFilm tags.
    * Revert Canon Makernote processing modifications

2.1.0 — 2015-05-15
    * Bypass empty/unreadable Olympus MakerNote info (issue #42)
    * Suport Apple Makernote and Apple HDR details (Jesus Cea)
    * Correcty process the Makernote of some Canon models (Jesus Cea)
    * Support HDR in Canon cameras (Jesus Cea)

2.0.2 — 2015-03-29
    * Fixed bug when importing as a module (issue #31)

2.0.1 — 2014-02-09
    * Represent the IFD as a string to fix formatting errors (issue #45)
    * Fix unicode errors in python2 (issue #46)
    * Fix for tag name backwards compatibility with 1.X series

2.0.0 — 2014-11-27
    * Drop support for Python 2.5
    * Add support for Python 3.2, 3.3 and 3.4 (velis74)
    * Add Travis testing
    * Cleanup some tag definitions
    * Fix bug #30 (TypeError on invalid IFD)
    * Fix bug #33 (TypeError on invalid output characters)
    * Add basic coloring for debug mode
    * Add finding XMP tags (experimental, debug only)
    * Add some missing Exif tags
    * Use stdout for log output
    * Experimental support for dumping XMP data

1.4.2 — 2013-11-28
    * A few new Canon tags
    * Python3 fixes (velis74 and leprechaun)
    * Fix for TypeError (issue #28)
    * Pylint & PEP8 fixes

1.4.1 — 2013-10-19
    * Better version handling
    * Better PyPI packaging

1.4.0 — 2013-09-28
    * Many new tags (big thanks to Rodolfo Puig, Paul Barton, Joe Beda)
    * Do not extract thumbnail in quick mode (issue #19)
    * Put tag definitions in separate module
    * Add more timing info & version info

1.3.3 — 2013-08-03
    * Add timing info in debug mode and nicer message format
    * Fix for faster processing

1.3.2 — 2013-07-31
    * Improve PyPI package
    * fix for DeprecationWarning: classic int division
    * Improvements to debug output
    * Add some Nikon makernote tags

1.3.1 — 2013-07-29
    * More PEP8 & PEP257 improvements
    * Better logging

1.3.0 — 2013-07-27
    * Set default values in case not set (ortsed)
    * PEP8 & PEP257 improvements
    * Better score in pylint
    * Ideas and some code from Samuele Santi's and Peter Reimer's forks
    * Replace print with logging
    * Package for PyPI

1.2.0 — 2013-02-08
    * Port to Python 3 (DarkRedman)
    * Fix endless loop on broken images (Michael Bemmerl)
    * Rewrite of README.md
    * Fixed incoherent copyright notices

1.1.0 — 2012-11-30 - Gregory Dudek
    * Overflow error fixes added (related to 2**31 size)
    * GPS tags added.

1.0.10 — 2012-09-26
    * Add GPS tags
    * Add better endian debug info

2012-06-13
    * Support malformed last IFD (fhats)
    * Light source, Flash and Metering mode dictionaries (gryfik)

2008-07-31
    * Wikipedia Commons hunt for suitable test case images,
    * testing new code additions.

2008-07-09 - Stephen H. Olson
    * Fix a problem with reading MakerNotes out of NEF files.
    * Add some more Nikon MakerNote tags.

2008-07-08 - Stephen H. Olson
    * An error check for large tags totally borked MakerNotes.
      With Nikon anyway, valid MakerNotes can be pretty big.
    * Add error check for a crash caused by nikon_ev_bias being
      called with the wrong args.
    * Drop any garbage after a null character in string
      (patch from Andrew McNabb <amcnabb@google.com>).

2008-02-12
    * Fix crash on invalid MakerNote
    * Fix crash on huge Makernote (temp fix)
    * Add printIM tag 0xC4A5, needs decoding info
    * Add 0x9C9B-F range of tags
    * Add a bunch of tag definitions from:
      http://owl.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
    * Add 'strict' variable and command line option

2008-01-18 - Gunter Ohrner
    * Add ``GPSDate`` tag

2007-12-12
    * Fix quick option on certain image types
    * Add note on tag naming in documentation

2007-11-30
    * Changed -s option to -t
    * Put changelog into separate file

2007-10-28
    * Merged changes from ReimarBauer
    * Added command line option for debug, stop 
      processing on tag.

2007-09-27
    * Add some Olympus Makernote tags.

2007-09-26 - Stephen H. Olson
    * Don't error out on invalid Olympus 'SpecialMode'.
    * Add a few more Olympus/Minolta tags.

2007-09-22 - Stephen H. Olson
    * Don't error on invalid string
    * Improved Nikon MakerNote support

2007-05-03 - Martin Stone
    * Fix for inverted detailed flag and Photoshop header

2007-03-24
    * Can now ignore MakerNotes Tags for faster processing.

2007-01-18
    * Fixed a couple errors and assuming maintenance of the library.

2006-08-04 Reimar Bauer
    * Added an optional parameter name to process_file and dump_IFD. Using this
      parameter the loop is breaked after that tag_name is processed.
    * some PEP8 changes


Original Notices
****************

Contains code from "exifdump.py" originally written by Thierry Bousch
<bousch@topo.math.u-psud.fr> and released into the public domain.

Updated and turned into general-purpose library by Gene Cash

Patch Contributors:
    * Simon J. Gerraty <sjg@crufty.net>
      s2n fix & orientation decode
    * John T. Riedl <riedl@cs.umn.edu>
      Added support for newer Nikon type 3 Makernote format for D70 and some
      other Nikon cameras.
    * Joerg Schaefer <schaeferj@gmx.net>
      Fixed subtle bug when faking an EXIF header, which affected maker notes
      using relative offsets, and a fix for Nikon D100.

2004-02-15 CEC
    * Finally fixed bit shift warning by converting Y to 0L.

2003-11-30 CEC
    * Fixed problem with canon_decode_tag() not creating an
      IFD_Tag() object.

2002-01-26 CEC
    * Added ability to extract TIFF thumbnails.
    * Added Nikon, Fujifilm, Casio MakerNotes.

2002-01-25 CEC
    * Discovered JPEG thumbnail in Olympus TIFF MakerNote.

2002-01-23 CEC
    * Trimmed nulls from end of string values.

2002-01-20 CEC Added MakerNote processing logic.
    * Added Olympus MakerNote.
    * Converted data structure to single-level dictionary, avoiding
      tag name collisions by prefixing with IFD name.  This makes
      it much easier to use.

2002-01-19 CEC Added ability to read TIFFs and JFIF-format JPEGs.
    * Added ability to extract JPEG formatted thumbnail.
    * Added ability to read GPS IFD (not tested).
    * Converted IFD data structure to dictionaries indexed by tag name.
    * Factored into library returning dictionary of IFDs plus thumbnail, if any.

2002-01-17 CEC Discovered code on web.
    * Commented everything.
    * Made small code improvements.
    * Reformatted for readability.

1999-08-21 TB
    * Last update by Thierry Bousch to his code.











