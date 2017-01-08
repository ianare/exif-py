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


class Ratio(Fraction):
    @property
    def num(self):
        return self.numerator

    @property
    def den(self):
        return self.denominator

    def __repr__(self):
        return str(self)

