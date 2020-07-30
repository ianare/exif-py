"""
Tag definitions
"""

from .exif import EXIF_TAGS
from .makernote import apple, canon, casio, fujifilm, nikon, olympus

DEFAULT_STOP_TAG = 'UNDEF'

# field type descriptions as (length, abbreviation, full name) tuples
FIELD_TYPES = (
    (0, 'X', 'Proprietary'),  # no such type
    (1, 'B', 'Byte'),
    (1, 'A', 'ASCII'),
    (2, 'S', 'Short'),
    (4, 'L', 'Long'),
    (8, 'R', 'Ratio'),
    (1, 'SB', 'Signed Byte'),
    (1, 'U', 'Undefined'),
    (2, 'SS', 'Signed Short'),
    (4, 'SL', 'Signed Long'),
    (8, 'SR', 'Signed Ratio'),
    (4, 'F32', 'Single-Precision Floating Point (32-bit)'),
    (8, 'F64', 'Double-Precision Floating Point (64-bit)'),
    (4, 'L', 'IFD'),
)

# To ignore when quick processing
IGNORE_TAGS = (
    0x9286,  # user comment
    0x927C,  # MakerNote Tags
    0x02BC,  # XPM
)
