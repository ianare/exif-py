"""Basic tests."""

import logging
from pathlib import Path

import pytest

import exifread
from exifread import DEFAULT_STOP_TAG

RESOURCES_ROOT = Path(__file__).parent / "resources"


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


@pytest.mark.parametrize("builtin_types", (True, False))
@pytest.mark.parametrize(
    "stop_tag, tag_count", (("ColorSpace", 39), (DEFAULT_STOP_TAG, 51))
)
def test_stop_at_tag(builtin_types, stop_tag, tag_count):
    file_path = RESOURCES_ROOT / "jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(
            fh=fh, stop_tag=stop_tag, builtin_types=builtin_types
        )
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


@pytest.mark.parametrize("details", (True, False))
@pytest.mark.parametrize("truncate_tags", (True, False))
@pytest.mark.parametrize("stop_tag", ("WhiteBalance", DEFAULT_STOP_TAG))
def test_builtin_types(stop_tag, details, truncate_tags):
    """
    When ``builtin_types=True``, always convert to Python types.
    Test with various other options to make sure they don't interfere.
    The "WhiteBalance" tag is after al the tags tested so must not have an impact.
    """
    file_path = RESOURCES_ROOT / "jpg/Canon_DIGITAL_IXUS_400.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(
            fh=fh,
            builtin_types=True,
            stop_tag=stop_tag,
            details=details,
            truncate_tags=truncate_tags,
        )
    # Short mapped to string value
    assert tags["EXIF ColorSpace"] == "sRGB"
    # Short
    assert isinstance(tags["EXIF ExifImageLength"], int)
    assert tags["EXIF ExifImageLength"] == 75
    # Ratio
    assert isinstance(tags["EXIF ExposureTime"], float)
    assert tags["EXIF ExposureTime"] == 0.005
    # ASCII
    assert tags["Image Make"] == "Canon"
    # Unknown / Undefined
    assert tags["EXIF FlashPixVersion"] == "0100"


def test_xmp_no_tag():
    """Read XMP data not in an Exif tag."""

    file_path = RESOURCES_ROOT / "tiff/Arbitro.tiff"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(
            fh=fh,
            builtin_types=True,
        )
    assert len(tags["Image ApplicationNotes"]) == 323
