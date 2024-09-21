"""
Enable conversion of Exif IfdTags to native Python types
"""

from exifread.tags import FIELD_TYPES

def convert_types(exif_tags: dict) -> dict:
    """
    Convert Exif IfdTags to built-in Python types (allowing exif serialization).

    If the printable value of the IfdTag is relevant (e.g. enum type), keep it.
    Otherwise, handle values according to their type.
    """

    output = {}

    for tag_name, ifd_tag in exif_tags.items():
        # JPEGThumbnail and TIFFThumbnail are the only values
        # in HDR Tags dict that do not have the IfdTag type.
        if isinstance(ifd_tag, bytes):
            output[tag_name] = ifd_tag
            continue

        code = FIELD_TYPES[ifd_tag.field_type][1]

        # Use the printable version if relevant
        if ifd_tag.prefer_printable:
            out = ifd_tag.printable

        # ASCII
        elif code == 'A':
            out = ifd_tag.values

            # Image DateTime, EXIF DateTimeOriginal, EXIF DateTimeDigitized are often
            # formatted in a way that cannot be parsed by python dateutil (%Y:%m:%d %H:%M:%S).
            if 'DateTime' in tag_name and len(out) == 19 and out.count(':') == 4:
                out = out.replace(':', '-', 2)

            # GPSDate
            elif tag_name == 'GPS GPSDate':
                # These are proper dates with the wrong delimiter (':' rather than '-').
                # Invalid values have been found in test images: '' and '2014:09:259'
                if len(out) == 10 and out.count(':') == 2:
                    out = out.replace(':', '-')

            # Other dates seen can be parsed properly

            # Strip occasional trailing whitespaces
            out = out.strip()

        # Undefined
        elif code == 'U':
            # These contain bytes represented as a list of integers
            out = bytes(ifd_tag.values)

            # Empty byte sequences or unicode values should be decoded as strings
            try:
                out = out.decode()
            except UnicodeDecodeError:
                pass

        # Short, Long, Signed Short, Signed Long,
        # Single-Precision Floating Point (32-bit), Double-Precision Floating Point (64-bit)
        elif code in ('S', 'L', 'SS', 'SL', 'F32', 'F64'):
            out = ifd_tag.values
            if not out:  # Empty lists, seen in floating point numbers
                out = ''
            elif len(out) == 1:
                out = out[0]

        # Ratio, Signed Ratio
        elif code in ('R', 'SR'):
            # Handle IfdTags where values are ratios (fractions.Fraction).
            # By default, the printable IfdTags is a string.
            # If there is only one ratio, it's the repr of that ratio (e.g. '1/10'), otherwise it's
            # a stringified list of repr of a Fraction objects (e.g. '[1/10, 3, 5/2]').
            # Values should be kept as float type, or integer if it's the case.
            # To convert back if desired: `Fraction(float_value).limit_denominator()`.
            out = []
            for ratio in ifd_tag.values:
                # Prevent division by 0. Sometimes, exif is full of 0s when a feature is not used.
                if ratio.denominator == 0:
                    ratio = ratio.numerator

                ratio = float(ratio)
                if ratio.is_integer():
                    ratio = int(ratio)

                out.append(ratio)

            if not out:  # Empty lists, seen in signed ratios
                out = ''
            elif len(out) == 1:
                out = out[0]

        # Proprietary
        elif code == 'X':
            out = ifd_tag.printable

        # Byte, Signed Byte
        elif code in ('B', 'SB'):
            out = ifd_tag.values

            if len(out) == 1:
                # Byte can be a single integer, such as GPSAltitudeRef (ifd_tag 0 or 1)
                out = out[0]

            elif not tag_name.startswith('GPS'):
                out = bytes(out)
                # Seen text strings with a null byte between each character
                # (e.g. b'p\x00i\x00a\x00n\x00o\x00')
                # and others with a lot of trailing null bytes.
                if out.endswith(b'\x00'):
                    out = out.replace(b'\x00', b'').strip()

                # Empty byte sequences or unicode values (e.g. XML Image ApplicationNotes)
                # should be decoded as strings.
                try:
                    out = out.decode()
                except UnicodeDecodeError:
                    pass

        else:
            # Fallback handling in case new field types are added before
            # updating the serialization function (e.g. to support bigtiff)
            out = ifd_tag.printable

        output[tag_name] = out

    return output
