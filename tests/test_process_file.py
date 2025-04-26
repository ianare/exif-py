"""Basic tests."""

import pytest

import exifread


def test_corrupted_exception():
    file_path = "tests/resources/jpg/corrupted.jpg"
    with open(file_path, "rb") as fh:
        with pytest.raises(ValueError) as err:
            exifread.process_file(fh=fh, strict=True)
        assert "tag 0x089C" in str(err.value)


def test_corrupted_pass():
    file_path = "tests/resources/jpg/corrupted.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, strict=False)
    assert "EXIF Contrast" in tags
    assert len(tags) == 69


@pytest.mark.parametrize("details", (True, False))
def test_thumbnail_extract(details):
    file_path = "tests/resources/jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, extract_thumbnail=True, details=details)
    assert len(tags["JPEGThumbnail"]) == 1378


@pytest.mark.parametrize("details", (True, False))
def test_no_thumbnail_extract(details):
    file_path = "tests/resources/jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, extract_thumbnail=False, details=details)
    assert "JPEGThumbnail" not in tags


@pytest.mark.parametrize("strict", (True, False))
def test_no_exif(strict):
    file_path = "tests/resources/jpg/xmp/no_exif.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, details=True, strict=strict)
    assert not tags


@pytest.mark.parametrize("strict", (True, False))
def test_invalid_exif(strict):
    file_path = "tests/resources/jpg/invalid/image00971.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, details=True, strict=strict)
    assert not tags
