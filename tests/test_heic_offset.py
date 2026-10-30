"""Tests for HEIC TIFF header offset validation and bounded reading (issue #249)."""

import io
import struct

import pytest

import exifread
from exifread.core.exceptions import InvalidExif
from exifread.core.heic import HEICExifFinder


class GuardedBytesIO(io.BytesIO):
    """BytesIO that records read sizes and fails before any huge allocation."""

    def __init__(self, initial_bytes=b"", max_read_size=64 * 1024):
        super().__init__(initial_bytes)
        self.max_read_size = max_read_size
        self.read_requests = []

    def read(self, size=-1):
        self.read_requests.append(size)
        if size is not None and size > self.max_read_size:
            raise AssertionError(
                f"GuardedBytesIO: read request {size} exceeded safety limit {self.max_read_size}"
            )
        return super().read(size)


def make_box(box_type: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", 8 + len(payload)) + box_type + payload


def make_full_box(box_type: bytes, version: int, flags: int, payload: bytes) -> bytes:
    vflags = (version << 24) | (flags & 0x00FFFFFF)
    return (
        struct.pack(">I", 12 + len(payload))
        + box_type
        + struct.pack(">I", vflags)
        + payload
    )


def make_simple_tiff(make_name=b"TestCamera\x00") -> bytes:
    header = b"II\x2a\x00\x08\x00\x00\x00"
    make_offset = 26
    ifd0 = (
        struct.pack("<H", 1)
        + struct.pack("<HHI", 0x010F, 2, len(make_name))
        + struct.pack("<I", make_offset)
        + struct.pack("<I", 0)
    )
    return header + ifd0 + make_name


def build_test_heic(
    exif_offset_val: int,
    prefix_data: bytes = b"Exif\x00\x00",
    tiff_data: bytes = make_simple_tiff(),
) -> bytes:
    ftyp = make_box(b"ftyp", b"heic" + struct.pack(">I", 0) + b"heic")
    infe_payload = struct.pack(">HH", 1, 0) + b"Exif" + b"\x00"
    infe = make_full_box(b"infe", 2, 0, infe_payload)
    iinf_payload = struct.pack(">H", 1) + infe
    iinf = make_full_box(b"iinf", 0, 0, iinf_payload)

    iloc_payload = (
        struct.pack(">BBHHH", 0x44, 0x00, 1, 1, 0)
        + struct.pack(">H", 1)
        + struct.pack(">II", 0xDEADBEEF, 0xCAFEBABE)
    )
    iloc = make_full_box(b"iloc", 0, 0, iloc_payload)

    meta_payload = iinf + iloc
    meta = make_full_box(b"meta", 0, 0, meta_payload)

    header = ftyp + meta
    payload_offset = len(header)

    exif_payload = struct.pack(">I", exif_offset_val) + prefix_data + tiff_data
    payload_len = len(exif_payload)

    full = bytearray(header + exif_payload)
    off_idx = full.find(struct.pack(">I", 0xDEADBEEF))
    len_idx = full.find(struct.pack(">I", 0xCAFEBABE))
    full[off_idx : off_idx + 4] = struct.pack(">I", payload_offset)
    full[len_idx : len_idx + 4] = struct.pack(">I", payload_len)
    return bytes(full)


def test_normal_6byte_prefix_control():
    raw = build_test_heic(6, prefix_data=b"Exif\x00\x00")
    fh = GuardedBytesIO(raw)
    finder = HEICExifFinder(fh)
    offset, endian = finder.find_exif()
    assert offset > 0
    assert endian == b"I"

    fh.seek(0)
    tags = exifread.process_file(fh)
    assert str(tags.get("Image Make")) == "TestCamera"


def test_app1_prefixed_control():
    raw = build_test_heic(10, prefix_data=b"\xff\xe1\x00\x08Exif\x00\x00")
    fh = GuardedBytesIO(raw)
    finder = HEICExifFinder(fh)
    offset, endian = finder.find_exif()
    assert offset > 0
    assert endian == b"I"

    fh.seek(0)
    tags = exifread.process_file(fh)
    assert str(tags.get("Image Make")) == "TestCamera"


def test_valid_padded_payload_control():
    padding = b"\x00" * 512
    raw = build_test_heic(512 + 6, prefix_data=padding + b"Exif\x00\x00")
    fh = GuardedBytesIO(raw)
    finder = HEICExifFinder(fh)
    offset, endian = finder.find_exif()
    assert offset > 0
    assert endian == b"I"

    fh.seek(0)
    tags = exifread.process_file(fh)
    assert str(tags.get("Image Make")) == "TestCamera"


def test_nokia_zero_offset_control():
    raw = build_test_heic(0, prefix_data=b"", tiff_data=make_simple_tiff())
    fh = GuardedBytesIO(raw)
    finder = HEICExifFinder(fh)
    offset, endian = finder.find_exif()
    assert offset == 0
    assert endian == b"?"

    fh.seek(0)
    tags = exifread.process_file(fh)
    assert str(tags.get("Image Make")) == "TestCamera"


def test_huge_32bit_offset_safely_rejected():
    raw = build_test_heic(0x7FFFFFFF)
    fh = GuardedBytesIO(raw, max_read_size=64 * 1024)
    finder = HEICExifFinder(fh)
    with pytest.raises(InvalidExif):
        finder.find_exif()

    # Verify no huge read request was passed to the file handle
    assert all(req <= 64 for req in fh.read_requests if req is not None)

    fh.seek(0)
    tags = exifread.process_file(fh)
    assert tags == {}


def test_too_small_offset_raises_invalid_exif():
    raw = build_test_heic(5)
    fh = GuardedBytesIO(raw)
    finder = HEICExifFinder(fh)
    with pytest.raises(InvalidExif) as exc_info:
        finder.find_exif()
    assert "too small" in str(exc_info.value).lower()

    fh.seek(0)
    assert exifread.process_file(fh) == {}


def test_bad_marker_raises_invalid_exif():
    raw = build_test_heic(6, prefix_data=b"BadMrk")
    fh = GuardedBytesIO(raw)
    finder = HEICExifFinder(fh)
    with pytest.raises(InvalidExif) as exc_info:
        finder.find_exif()
    assert "not found" in str(exc_info.value).lower()

    fh.seek(0)
    assert exifread.process_file(fh) == {}


def test_truncated_marker_raises_invalid_exif():
    # Only 2 bytes of marker present before EOF
    raw = build_test_heic(6, prefix_data=b"Ex", tiff_data=b"")
    fh = GuardedBytesIO(raw)
    finder = HEICExifFinder(fh)
    with pytest.raises(InvalidExif) as exc_info:
        finder.find_exif()
    assert "not found" in str(exc_info.value).lower()

    fh.seek(0)
    assert exifread.process_file(fh) == {}
