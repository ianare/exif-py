"""WebP EXIF payload layouts."""

import struct
from io import BytesIO

import pytest

import exifread


def webp_with_orientation(endian, orientation, prefix):
    """Generate a RIFF metadata container without external image fixtures."""
    marker, order = (b"II", "<") if endian == "little" else (b"MM", ">")
    tiff = (
        marker
        + struct.pack(order + "HI", 42, 8)
        + struct.pack(order + "H", 1)
        + struct.pack(order + "HHI", 0x0112, 3, 1)
        + struct.pack(order + "H", orientation)
        + b"\x00\x00"
        + struct.pack(order + "I", 0)
    )
    payload = prefix + tiff
    vp8x = b"VP8X" + struct.pack("<I", 10) + b"\x08" + b"\x00" * 9
    body = b"WEBP" + vp8x + b"EXIF" + struct.pack("<I", len(payload)) + payload
    return b"RIFF" + struct.pack("<I", len(body)) + body


@pytest.mark.parametrize("orientation", range(1, 9))
@pytest.mark.parametrize("endian", ("little", "big"))
@pytest.mark.parametrize("prefix", (b"", b"Exif\x00\x00"))
def test_webp_orientation_with_optional_exif_prefix(orientation, endian, prefix):
    tags = exifread.process_file(
        BytesIO(webp_with_orientation(endian, orientation, prefix))
    )
    assert tags["Image Orientation"].values == [orientation]
