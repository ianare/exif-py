"""
Misc utilities.
"""

from fractions import Fraction
from typing import Optional, Tuple, Union


def ord_(dta) -> int:
    if isinstance(dta, str):
        return ord(dta)
    return dta


def make_string(seq) -> str:
    """
    Don't throw an exception when given an out of range character.
    """
    string = ""
    for char in seq:
        # Screen out non-printing characters
        try:
            if 32 <= char < 256:
                string += chr(char)
        except TypeError:
            pass

    # If no printing chars
    if not string:
        if isinstance(seq, list):
            string = "".join(map(str, seq))
            # Some UserComment lists only contain null bytes, nothing valuable to return
            if set(string) == {"0"}:
                return ""
        else:
            string = str(seq)

    # Clean undesirable characters on any end
    return string.strip(" \x00")


def make_string_uc(seq) -> str:
    """
    Special version to deal with the code in the first 8 bytes of a user comment.
    First 8 bytes gives coding system e.g. ASCII vs. JIS vs Unicode.
    """
    if not isinstance(seq, str):
        # Remove code from sequence only if it is valid
        if make_string(seq[:8]).upper() in ("ASCII", "UNICODE", "JIS", ""):
            seq = seq[8:]
    # Of course, this is only correct if ASCII, and the standard explicitly
    # allows JIS and Unicode.
    return make_string(seq)


def degrees_to_decimal(degrees: float, minutes: float, seconds: float) -> float:
    """
    Converts coordinates from a degrees minutes seconds format to a decimal degrees format.
    Reference: https://en.wikipedia.org/wiki/Geographic_coordinate_conversion
    """
    return degrees + minutes / 60 + seconds / 3600


def get_gps_coords(tags: dict) -> Union[Tuple[float, float], None]:
    """
    Extract tuple of latitude and longitude values in decimal degrees format from EXIF tags.
    Return None if no GPS coordinates are found.
    Handles regular and serialized Exif tags.
    """
    gps = {
        "lat_coord": "GPS GPSLatitude",
        "lat_ref": "GPS GPSLatitudeRef",
        "lng_coord": "GPS GPSLongitude",
        "lng_ref": "GPS GPSLongitudeRef",
    }

    # Verify if required keys are a subset of provided tags
    if not set(gps.values()) <= tags.keys():
        return None

    # If tags have not been converted to native Python types, do it
    if not isinstance(tags[gps["lat_coord"]], list):
        tags[gps["lat_coord"]] = [c.decimal() for c in tags[gps["lat_coord"]].values]
        tags[gps["lng_coord"]] = [c.decimal() for c in tags[gps["lng_coord"]].values]
        tags[gps["lat_ref"]] = tags[gps["lat_ref"]].values
        tags[gps["lng_ref"]] = tags[gps["lng_ref"]].values

    lat = degrees_to_decimal(*tags[gps["lat_coord"]])
    if tags[gps["lat_ref"]] == "S":
        lat *= -1

    lng = degrees_to_decimal(*tags[gps["lng_coord"]])
    if tags[gps["lng_ref"]] == "W":
        lng *= -1

    return lat, lng


class Ratio(Fraction):
    """
    Ratio object that eventually will be able to reduce itself to lowest
    common denominator for printing.
    """

    _numerator: Optional[int]
    _denominator: Optional[int]

    # We're immutable, so use __new__ not __init__
    def __new__(cls, numerator: int = 0, denominator: Optional[int] = None):
        try:
            self = super(Ratio, cls).__new__(cls, numerator, denominator)
        except ZeroDivisionError:
            self = super(Ratio, cls).__new__(cls)
            self._numerator = numerator
            self._denominator = denominator
        return self

    def __repr__(self) -> str:
        return str(self)

    @property
    def num(self):
        return self.numerator

    @property
    def den(self):
        return self.denominator

    def decimal(self) -> float:
        return float(self)
