"""
Tag definitions
"""

from typing import List

DEFAULT_STOP_TAG = "UNDEF"


# To ignore when quick processing
IGNORE_TAGS: List[int] = [
    0x02BC,  # XPM
    0x927C,  # MakerNote Tags
    0x9286,  # user comment
]
