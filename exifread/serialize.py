"""
Enable conversion of Exif IfdTags to native Python types
"""

from .tags import FIELD_TYPES

def convert_hdr_tags(hdr_tags: dict) -> dict:
    """
    Convert Exif IfdTags to native Python types (allowing exif serialization).

    If the printable value is relevant (i.e. enum type), keep it.
    Otherwise, handle values according on their type.
    """

    output = {}

    for k, v in hdr_tags.items():
        # JPEGThumbnail and TIFFThumbnail are the only values
        # in HDR Tags dict that do not have the IfdTag type.
        if isinstance(v, bytes):
            output[k] = v
            continue

        code = FIELD_TYPES[v.field_type][1]

        # Use the printable version if relevant
        if v.prefer_printable:
            out = v.printable

        # ASCII
        elif code == 'A':
            out = v.values

            # Image DateTime, EXIF DateTimeOriginal, EXIF DateTimeDigitized are often
            # formatted in a way that cannot be parsed by python dateutil (%Y:%m:%d %H:%M:%S).
            if 'DateTime' in k and len(out) == 19 and out.count(':') == 4:
                out = out.replace(':', '-', 2)

            # GPSDate
            elif k == 'GPS GPSDate':
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
            out = bytes(v.values)

            # Empty byte sequences or unicode values should be decoded as strings
            try:
                out = out.decode()
            except UnicodeDecodeError:
                pass

        # Short, Long, Signed Short, Signed Long, Single-Precision Floating Point (32-bit), Double-Precision Floating Point (64-bit)
        elif code in ('S', 'L', 'SS', 'SL', 'F32', 'F64'):
            out = v.values
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
            out = []
            for r in v.values:
                # Prevent division by 0. Sometimes, exif is full of 0s when a feature is not used.
                if r.denominator == 0:
                    r = r.numerator

                r = float(r)
                if r.is_integer():
                    r = int(r)

                out.append(r)

            if not out:  # Empty lists, seen in signed ratios
                out = ''
            elif len(out) == 1:
                out = out[0]

        # Proprietary
        elif code == 'X':
            out = v.printable

        # Byte, Signed Byte
        elif code in ('B', 'SB'):
            out = v.values

            if len(out) == 1:
                # Byte can be a single integer, such as GPSAltitudeRef (value 0 or 1)
                out = out[0]

            elif not k.startswith('GPS'):
                out = bytes(out)
                # Seen text strings with a null byte between each character
                # (i.e. b'p\x00i\x00a\x00n\x00o\x00')
                # and others with a lot of trailing null bytes.
                if out.endswith(b'\x00'):
                    out = out.replace(b'\x00', b'').strip()

                # Empty byte sequences or unicode values (i.e. XML Image ApplicationNotes)
                # should be decoded as strings.
                try:
                    out = out.decode()
                except UnicodeDecodeError:
                    pass

        output[k] = out

    return output

