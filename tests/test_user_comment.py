"""Read encoding-marked UserComment values through the public API."""

import struct
from io import BytesIO

import pytest

import exifread


def _tiff_comment(payload, byte_order):
    """Construct a TIFF with an Exif IFD containing one undefined UserComment."""
    endian = "<" if byte_order == b"II" else ">"

    def pack(fmt, *args):
        return struct.pack(endian + fmt, *args)

    return (
        byte_order
        + pack("HI", 42, 8)
        + pack("H", 1)
        + pack("HHII", 0x8769, 4, 1, 26)
        + pack("I", 0)
        + pack("H", 1)
        + pack("HHII", 0x9286, 7, len(payload), 44)
        + pack("I", 0)
        + payload
    )


@pytest.mark.parametrize("byte_order", (b"II", b"MM"))
@pytest.mark.parametrize(
    "encoding,bom", (("utf-16-le", b"\xff\xfe"), ("utf-16-be", b"\xfe\xff"))
)
def test_unicode_user_comment(byte_order, encoding, bom):
    comment = "Café — 東京 🌅"
    payload = b"UNICODE\x00" + bom + comment.encode(encoding)
    tags = exifread.process_file(BytesIO(_tiff_comment(payload, byte_order)))
    assert str(tags["EXIF UserComment"]) == comment


@pytest.mark.parametrize(
    "payload,expected",
    (
        (b"ASCII\x00\x00\x00plain comment\x00", "plain comment"),
        (b"UNICODE\x00" + "legacy".encode("utf-16-le"), "legacy"),
        (b"UNICODE\x00\xff\xfeA", "ÿþA"),
        (b"UNICODE\x00\xff\xfe", ""),
        (b"UNKNOWN!plain", "UNKNOWN!plain"),
        (b"ASCII\x00\x00\x00  padded comment  \x00", "padded comment"),
        (b"UNICODE\x00\xff\xfe" + "  東京  \x00".encode("utf-16-le"), "東京"),
    ),
)
def test_user_comment_legacy_and_incomplete(payload, expected):
    tags = exifread.process_file(BytesIO(_tiff_comment(payload, b"II")))
    assert str(tags["EXIF UserComment"]) == expected
