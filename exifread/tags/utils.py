

def make_string(seq):
    """
    Don't throw an exception when given an out of range character.
    """
    string = ''
    for c in seq:
        # Screen out non-printing characters
        if 32 <= c and c < 256:
            string += chr(c)
    # If no printing chars
    if not string:
        return str(seq)
    return string


def make_string_uc(seq):
    """
    Special version to deal with the code in the first 8 bytes of a user comment.
    First 8 bytes gives coding system e.g. ASCII vs. JIS vs Unicode.
    """
    #code = seq[0:8]
    seq = seq[8:]
    # Of course, this is only correct if ASCII, and the standard explicitly
    # allows JIS and Unicode.
    return make_string( make_string(seq) )
