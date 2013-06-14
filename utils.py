
def make_string(seq):
    """Don't throw an exception when given an out of range character."""
    
    str = ''
    for c in seq:
        # Screen out non-printing characters
        if 32 <= c and c < 256:
            str += chr(c)
    # If no printing chars
    if not str:
        return seq
    return str

def make_string_uc(seq):
    """ Special version to deal with the code in the first 8 bytes of a user comment.
        First 8 bytes gives coding system e.g. ASCII vs. JIS vs Unicode
    """
    code = seq[0:8]
    seq = seq[8:]
    # Of course, this is only correct if ASCII, and the standard explicitly
    # allows JIS and Unicode.
    return make_string( make_string(seq) )

def nikon_ev_bias(seq):
    """ First digit seems to be in steps of 1/6 EV.
    Does the third value mean the step size?  It is usually 6,
    but it is 12 for the ExposureDifference.
    
    Check for an error condition that could cause a crash.
    This only happens if something has gone really wrong in
    reading the Nikon MakerNote.
    http://tomtia.plala.jp/DigitalCamera/MakerNote/index.asp
    """
    if len( seq ) < 4 : return ""
    #
    if seq == [252, 1, 6, 0]:
        return "-2/3 EV"
    if seq == [253, 1, 6, 0]:
        return "-1/2 EV"
    if seq == [254, 1, 6, 0]:
        return "-1/3 EV"
    if seq == [0, 1, 6, 0]:
        return "0 EV"
    if seq == [2, 1, 6, 0]:
        return "+1/3 EV"
    if seq == [3, 1, 6, 0]:
        return "+1/2 EV"
    if seq == [4, 1, 6, 0]:
        return "+2/3 EV"
    # Handle combinations not in the table.
    a = seq[0]
    # Causes headaches for the +/- logic, so special case it.
    if a == 0:
        return "0 EV"
    if a > 127:
        a = 256 - a
        ret_str = "-"
    else:
        ret_str = "+"
    b = seq[2]  # Assume third value means the step size
    whole = a / b
    a = a % b
    if whole != 0:
        ret_str = ret_str + str(whole) + " "
    if a == 0:
        ret_str = ret_str + "EV"
    else:
        r = Ratio(a, b)
        ret_str = ret_str + r.__repr__() + " EV"
    return ret_str

def olympus_special_mode(v):
    """decode Olympus SpecialMode tag in MakerNote"""
    a={
        0: 'Normal',
        1: 'Unknown',
        2: 'Fast',
        3: 'Panorama'}
    b={
        0: 'Non-panoramic',
        1: 'Left to right',
        2: 'Right to left',
        3: 'Bottom to top',
        4: 'Top to bottom'}
    if v[0] not in a or v[2] not in b:
        return v
    return '%s - sequence %d - %s' % (a[v[0]], v[1], b[v[2]])
