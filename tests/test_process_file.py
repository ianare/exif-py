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


@pytest.mark.parametrize(
    "extract_thumbnail, details",
    (
        (True, False),
        (True, True),
        (False, True),
    ),
)
def test_thumbnail_extraction(extract_thumbnail, details):
    file_path = "tests/resources/jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(
            fh=fh, extract_thumbnail=extract_thumbnail, details=details
        )
    assert len(tags["JPEGThumbnail"]) == 1378


def test_no_thumbnail_extraction():
    file_path = "tests/resources/jpg/Canon_40D.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, extract_thumbnail=False, details=False)
    assert "JPEGThumbnail" not in tags


@pytest.mark.parametrize("strict", (True, False))
def test_no_exif(strict):
    file_path = "tests/resources/jpg/xmp/no_exif.jpg"
    with open(file_path, "rb") as fh:
        tags = exifread.process_file(fh=fh, details=True, strict=strict)
    assert not tags
