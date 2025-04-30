"""Basic tests."""

import logging
from pathlib import Path

import pytest

import exifread
from exifread import DEFAULT_STOP_TAG

RESOURCES_ROOT = Path("tests/resources/")


def test_corrupted_exception():
    file_path = RESOURCES_ROOT / "jpg/corrupted.jpg"
    with open(file_path, "rb") as fh:
        with pytest.raises(ValueError) as err:
            exifread.process_file(fh=fh, strict=True)
        assert "tag 0x089C" in str(err.value)


def test_corrupted_pass():
    file_path = RESOURCES_ROOT / "jpg/corrupted.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, strict=False)
    assert "EXIF Contrast" in tags
    assert len(tags) == 69


@pytest.mark.parametrize(
    "stop_tag, tag_count", (("ColorSpace", 39), (DEFAULT_STOP_TAG, 51))
)
def test_stop_at_tag(stop_tag, tag_count):
    file_path = RESOURCES_ROOT / "jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, stop_tag=stop_tag)
    assert len(tags) == tag_count


@pytest.mark.parametrize("extract_thumbnail", (True, False))
def test_makernote_extract(extract_thumbnail):
    file_path = RESOURCES_ROOT / "jpg/Canon_DIGITAL_IXUS_400.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(
            fh=fh, extract_thumbnail=extract_thumbnail, details=True
        )
    assert "MakerNote AESetting" in tags


@pytest.mark.parametrize("extract_thumbnail", (True, False))
def test_no_makernote_extract(extract_thumbnail):
    file_path = RESOURCES_ROOT / "jpg/Canon_DIGITAL_IXUS_400.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(
            fh=fh, extract_thumbnail=extract_thumbnail, details=False
        )
    assert "MakerNote AESetting" not in tags


@pytest.mark.parametrize("details", (True, False))
def test_thumbnail_extract(details):
    file_path = RESOURCES_ROOT / "jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, extract_thumbnail=True, details=details)
    assert len(tags["JPEGThumbnail"]) == 1378


@pytest.mark.parametrize("details", (True, False))
def test_no_thumbnail_extract(details):
    file_path = RESOURCES_ROOT / "jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, extract_thumbnail=False, details=details)
    assert "JPEGThumbnail" not in tags


@pytest.mark.parametrize("strict", (True, False))
def test_no_exif(strict):
    file_path = RESOURCES_ROOT / "jpg/xmp/no_exif.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, details=True, strict=strict)
    assert not tags


@pytest.mark.parametrize("strict", (True, False))
def test_invalid_exif(strict):
    file_path = RESOURCES_ROOT / "jpg/invalid/image00971.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, details=True, strict=strict)
    assert not tags


@pytest.mark.parametrize(
    "file_path, message",
    (
        ("jpg/tests/30-type_error.jpg", "corrupted IFD: EXIF"),
        ("jpg/tests/35-empty.jpg", "corrupted field RecordingMode"),
        ("jpg/tests/45-gps_ifd.jpg", "No values found for GPS SubIFD"),
    ),
)
def test_warning_messages(caplog, file_path, message):
    """
    We already capture this in the dump file.
    Need to make sure it's the logger capturing this rather than a print() statement or equivalent.
    """
    caplog.set_level(logging.WARNING)
    with open(RESOURCES_ROOT / file_path, "rb") as fh:
        exifread.process_file(fh=fh, details=True)
    assert message in caplog.text


def test_stop_tag_with_thumbnail_extract():
    """
    Stop at `Orientation` tag and extract thumbnail.
    Fails since the `Orientation` tag comes before the `JPEGInterchangeFormatLength` tag.
    Should not raise an Exception.
    """
    file_path = RESOURCES_ROOT / "jpg/tests/Xiaomi_Mi_9T_KeyError.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, details=False, stop_tag="Orientation")
    assert tags
