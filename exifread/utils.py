"""
Misc utilities.
"""

from fractions import Fraction


def ord_(dta):
    if isinstance(dta, str):
        return ord(dta)
    return dta


def make_string(seq):
    """
    Don't throw an exception when given an out of range character.
    """
    string = ''
    for c in seq:
        # Screen out non-printing characters
        try:
            if 32 <= c and c < 256:
                string += chr(c)
        except TypeError:
            pass
        # If no printing chars
    if not string:
        return str(seq)
    return string


def make_string_uc(seq):
    """
    Special version to deal with the code in the first 8 bytes of a user comment.
    First 8 bytes gives coding system e.g. ASCII vs. JIS vs Unicode.
    """
    seq = seq[8:]
    # Of course, this is only correct if ASCII, and the standard explicitly
    # allows JIS and Unicode.
    return make_string(seq)


def s2n_motorola(string):
    """Extract multi-byte integer in Motorola format (little endian)."""
    x = 0
    for c in string:
        x = (x << 8) | ord_(c)
    return x


def s2n_intel(string):
    """Extract multi-byte integer in Intel format (big endian)."""
    x = 0
    y = 0
    for c in string:
        x = x | (ord_(c) << y)
        y += + 8
    return x

def get_gps_coords(tags):

    lng_ref_tag_name = "GPS GPSLongitudeRef"
    lng_tag_name = "GPS GPSLongitude"
    lat_ref_tag_name = "GPS GPSLatitudeRef"
    lat_tag_name = "GPS GPSLatitude"

    # Check if these tags are present
    gps_tags = [lng_ref_tag_name,lng_tag_name,lat_tag_name,lat_tag_name]
    for tag in gps_tags:
        if not tag in tags.keys():
            return None

    lng_ref_val = tags[lng_ref_tag_name].values
    lng_coord_val = [c.decimal() for c in tags[lng_tag_name].values]

    lat_ref_val = tags[lat_ref_tag_name].values
    lat_coord_val = [c.decimal() for c in tags[lat_tag_name].values]

    lng_coord = sum([c/60**i for i,c in enumerate(lng_coord_val)])
    lng_coord *= (-1)**(lng_ref_val=="W")

    lat_coord = sum([c/60**i for i,c in enumerate(lat_coord_val)])
    lat_coord *= (-1)**(lat_ref_val=="S")

    return (lat_coord, lng_coord)

class Ratio(Fraction):
    """
    Ratio object that eventually will be able to reduce itself to lowest
    common denominator for printing.
    """

    # We're immutable, so use __new__ not __init__
    def __new__(cls, numerator=0, denominator=None):
        try:
            self = super(Ratio, cls).__new__(cls, numerator, denominator)
        except ZeroDivisionError:
            self = super(Ratio, cls).__new__(cls)
            self._numerator = numerator
            self._denominator = denominator
            return self
    __new__.doc = Fraction.__new__.__doc__

    def __repr__(self):
        return str(self)

    @property
    def num(self):
        return self.numerator

    @property
    def den(self):
        return self.denominator

    def decimal(self):
        return float(self)
