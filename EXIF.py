#!/usr/bin/env python3
#
#AliElTop
# Library to extract Exif information from digital camera image files.
# https://github.com/ianare/exif-py
#
#
# Copyright (c) 2002-2007 Gene Cash
# Copyright (c) 2007-2023 Ianaré Sévi and contributors
#
# See LICENSE.txt file for licensing information
# See ChangeLog.rst file for all contributors and changes
#

"""
Runs Exif tag extraction in command line.
"""

import sys
import argparse
import timeit
from exifread.tags import FIELD_TYPES
from exifread import process_file, exif_log, __version__

logger = exif_log.get_logger()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='EXIF.py',
        description='Extract EXIF information from digital image files.'
    )
    parser.add_argument(
        'files', metavar='FILE', type=str, nargs='+',
        help='files to process',
    )
    parser.add_argument(
        '-v', '--version', action='version',
        version='EXIF.py Version %s on Python%s' % (__version__, sys.version_info[0]),
        help='Display version information and exit'
    )
    parser.add_argument(
        '-q', '--quick', action='store_false', dest='detailed',
        help='Do not process MakerNotes and do not extract thumbnails',
    )
    parser.add_argument(
        '-t', '--tag', type=str, dest='stop_tag',
        help='Stop processing when this tag is retrieved.',
    )
    parser.add_argument(
        '-s', '--strict', action='store_true', dest='strict',
        help='Run in strict mode (stop on errors).',
    )
    parser.add_argument(
        '-d', '--debug', action='store_true', dest='debug',
        help='Run in debug mode (display extra info).',
    )
    parser.add_argument(
        '-c', '--color', action='store_true', dest='color',
        help='Output in color (only works with debug on POSIX).',
    )
    args = parser.parse_args()
    return args


def main(args: argparse.Namespace) -> None:
    """Extract tags based on options (args)."""

    exif_log.setup_logger(args.debug, args.color)

    for filename in args.files:
        escaped_fn = filename.encode(sys.getfilesystemencoding(), 'surrogateescape').decode()

        file_start = timeit.default_timer()
        try:
            with open(escaped_fn, 'rb') as img_file:
                logger.info('Opening: %s', escaped_fn)

                tag_start = timeit.default_timer()

                data = process_file(
                    img_file,
                    stop_tag=args.stop_tag,
                    details=args.detailed,
                    strict=args.strict,
                    debug=args.debug,
                    extract_thumbnail=args.detailed
                )

                tag_stop = timeit.default_timer()

                if not data:
                    logger.warning('No EXIF information found')
                    logger.info('')
                    continue

                if 'JPEGThumbnail' in data:
                    logger.info('File has JPEG thumbnail')
                    del data['JPEGThumbnail']
                if 'TIFFThumbnail' in data:
                    logger.info('File has TIFF thumbnail')
                    del data['TIFFThumbnail']

                tag_keys = list(data.keys())
                tag_keys.sort()

                for i in tag_keys:
                    try:
                        field_type_info = FIELD_TYPES.get(data[i].field_type, ('Unknown', 'Unknown', 'Unknown'))
                        logger.info('%s (%s): %s', i, field_type_info[2], data[i].printable)
                    except Exception as e:
                        logger.error("%s : %s", i, str(e))

                file_stop = timeit.default_timer()

                logger.debug("Tags processed in %s seconds", tag_stop - tag_start)
                logger.debug("File processed in %s seconds", file_stop - file_start)
                logger.info('')

        except FileNotFoundError:
            logger.error("'%s' not found", escaped_fn)
        except Exception as e:
            logger.error("An error occurred while processing '%s': %s", escaped_fn, str(e))


if __name__ == '__main__':
    main(get_args())
