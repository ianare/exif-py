"""Tests for TIFF headers in HEIC Exif items."""

from io import BytesIO

import pytest

from exifread.core.exceptions import InvalidExif
from exifread.core.heic import find_heic_tiff


@pytest.mark.parametrize("header", [b"II\x2a\x00", b"MM\x00\x2a"])
def test_tiff_header_byte_order(header):
    """Recognize the TIFF magic number in either byte order."""
    stream = BytesIO(b"prefix" + header + b"payload")
    stream.seek(6)

    assert find_heic_tiff(stream) == (6, header[:2])
    assert stream.tell() == 6
    assert stream.read(4) == header


@pytest.mark.parametrize(
    "header",
    [
        b"",
        b"I",
        b"II",
        b"II\x2a",
        b"MM",
        b"MM\x00",
        b"II\x00\x2a",
        b"MM\x2a\x00",
        b"bad!",
    ],
)
def test_invalid_tiff_header(header):
    """Reject truncated headers and magic numbers in the wrong byte order."""
    with pytest.raises(InvalidExif):
        find_heic_tiff(BytesIO(header))
