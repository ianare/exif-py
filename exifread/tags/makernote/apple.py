"""
Makernote (proprietary) tag definitions for Apple iOS

Based on version 1.01 of ExifTool -> Image/ExifTool/Apple.pm
http://owl.phy.queensu.ca/~phil/exiftool/
"""
from typing import Dict, Tuple

TAGS: Dict[int, Tuple] = {
    0x000A: (
        "HDRImageType",
        {
            3: "HDR Image",
            4: "Original Image",
        },
    ),
}
