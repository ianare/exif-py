exif-py
=======

Python library to extract EXIF data from tiff and jpeg files.

Originally written by Gene Cash / Thierry Bousch.

##Usage

###Command line
Get all tags
~~~
$ ./EXIF.py image.jpg
~~~

Show command line options
~~~
$ ./EXIF.py
~~~

###Within python script
~~~
[python]
import EXIF

# Open image file for reading (binary mode)
f = open(path_name, 'rb')

# Get all tags
tags = EXIF.process_file(f)

# Get tags, but not MakerNote
tags = EXIF.process_file(f, details=False)

# Stop processing the file after reaching a tag (faster processing)
tag = "DateTimeOriginal"
tags = EXIF.process_file(f, details=False, stop_tag=tag)

# Return an error on invalid tags
tags = EXIF.process_file(f, strict=True)
~~~