"""
Read Exif metadata from image files
Supported formats: TIFF, JPEG, PNG, Webp, HEIC
"""

import struct
from typing import Any, BinaryIO, Dict, Tuple

from exifread.classes import ExifHeader
from exifread.exceptions import ExifNotFound, InvalidExif
from exifread.exif_log import get_logger
from exifread.heic import HEICExifFinder
from exifread.jpeg import find_jpeg_exif
from exifread.serialize import convert_types
from exifread.tags import DEFAULT_STOP_TAG
from exifread.utils import make_string, ord_

__version__ = "3.1.0"

logger = get_logger()


ENDIAN_TYPES: Dict[str, str] = {
    "I": "Intel",
    "M": "Motorola",
    "\x01": "Adobe Ducky",
    "b": "XMP/Adobe unknown",
}


def _find_tiff_exif(fh: BinaryIO) -> Tuple[int, bytes]:
    logger.debug("TIFF format recognized in data[0:2]")
    fh.seek(0)
    endian = fh.read(1)
    fh.read(1)
    offset = 0
    return offset, endian


def _find_heic_tiff(fh: BinaryIO) -> Tuple[int, bytes]:
    """
    Look for TIFF header in HEIC files.

    In some HEIC files, the Exif offset is 0,
    and yet there is a plain TIFF header near end of the file.
    """

    data = fh.read(4)
    if data[0:2] in [b"II", b"MM"] and data[2] == 42 and data[3] == 0:
        offset = fh.tell() - 4
        fh.seek(offset)
        endian = data[0:2]
        offset = fh.tell()
        logger.debug("Found TIFF header in Exif, offset = %0xH", offset)
    else:
        raise InvalidExif(
            "Exif pointer to zeros, but found "
            + str(data)
            + " instead of a TIFF header."
        )

    return offset, endian


def _find_webp_exif(fh: BinaryIO) -> Tuple[int, bytes]:
    logger.debug("WebP format recognized in data[0:4], data[8:12]")
    # file specification: https://developers.google.com/speed/webp/docs/riff_container
    data = fh.read(5)
    if data[0:4] == b"VP8X" and data[4] & 8:
        # https://developers.google.com/speed/webp/docs/riff_container#extended_file_format
        fh.seek(13, 1)
        while True:
            data = fh.read(8)  # Chunk FourCC (32 bits) and Chunk Size (32 bits)
            if len(data) != 8:
                raise InvalidExif("Invalid webp file chunk header.")
            if data[0:4] == b"EXIF":
                fh.seek(6, 1)
                offset = fh.tell()
                endian = fh.read(1)
                return offset, endian
            size = struct.unpack("<L", data[4:8])[0]
            fh.seek(size, 1)
    raise ExifNotFound("Webp file does not have exif data.")


def _find_png_exif(fh: BinaryIO, data: bytes) -> Tuple[int, bytes]:
    logger.debug("PNG format recognized in data[0:8]=%s", data[:8].hex())
    fh.seek(8)

    while True:
        data = fh.read(8)
        chunk = data[4:8]
        logger.debug("PNG found chunk %s", chunk.decode("ascii"))

        if chunk in (b"", b"IEND"):
            break
        if chunk == b"eXIf":
            offset = fh.tell()
            return offset, fh.read(1)

        chunk_size = int.from_bytes(data[:4], "big")
        fh.seek(fh.tell() + chunk_size + 4)

    raise ExifNotFound("PNG file does not have exif data.")


def _get_xmp(fh: BinaryIO) -> bytes:
    xmp_bytes = b""
    logger.debug("XMP not in Exif, searching file for XMP info...")
    xml_started = False
    xml_finished = False
    for line in fh:
        open_tag = line.find(b"<x:xmpmeta")
        close_tag = line.find(b"</x:xmpmeta>")
        if open_tag != -1:
            xml_started = True
            line = line[open_tag:]
            logger.debug("XMP found opening tag at line position %s", open_tag)
        if close_tag != -1:
            logger.debug("XMP found closing tag at line position %s", close_tag)
            line_offset = 0
            if open_tag != -1:
                line_offset = open_tag
            line = line[: (close_tag - line_offset) + 12]
            xml_finished = True
        if xml_started:
            xmp_bytes += line
        if xml_finished:
            break
    logger.debug("XMP Finished searching for info")
    return xmp_bytes


def _determine_type(fh: BinaryIO) -> Tuple[int, bytes, int]:
    # by default do not fake an EXIF beginning
    fake_exif = 0

    data = fh.read(12)
    if data[0:2] in [b"II", b"MM"]:
        # it's a TIFF file
        offset, endian = _find_tiff_exif(fh)
    elif data[4:12] == b"ftypheic":
        fh.seek(0)
        heic = HEICExifFinder(fh)
        offset, endian = heic.find_exif()
        if offset == 0:
            offset, endian = _find_heic_tiff(fh)
            # It's a HEIC file with a TIFF header
    elif data[0:4] == b"RIFF" and data[8:12] == b"WEBP":
        offset, endian = _find_webp_exif(fh)
    elif data[0:2] == b"\xFF\xD8":
        # it's a JPEG file
        offset, endian, fake_exif = find_jpeg_exif(fh, data, fake_exif)
    elif data[0:8] == b"\x89PNG\r\n\x1a\n":
        offset, endian = _find_png_exif(fh, data)
    else:
        raise ExifNotFound("File format not recognized.")
    return offset, endian, fake_exif


def process_file(
    fh: BinaryIO,
    stop_tag=DEFAULT_STOP_TAG,
    details=True,
    strict=False,
    debug=False,
    truncate_tags=True,
    auto_seek=True,
    extract_thumbnail=True,
    builtin_types=False,
) -> Dict[str, Any]:
    """
    Process an image file (expects an open file object).

    This is the function that has to deal with all the arbitrary nasty bits
    of the EXIF standard.
    """

    if auto_seek:
        fh.seek(0)

    try:
        offset, endian_bytes, fake_exif = _determine_type(fh)
    except ExifNotFound as err:
        logger.warning(err)
        return {}
    except InvalidExif as err:
        logger.debug(err)
        return {}

    endian_str = chr(ord_(endian_bytes[0]))
    # deal with the EXIF info we found
    logger.debug(
        "Endian format is %s (%s)", endian_str, ENDIAN_TYPES.get(endian_str, "Unknown")
    )

    hdr = ExifHeader(
        fh, endian_str, offset, fake_exif, strict, debug, details, truncate_tags
    )
    ifd_list = hdr.list_ifd()
    thumb_ifd = 0
    ctr = 0
    for ifd in ifd_list:
        if ctr == 0:
            ifd_name = "Image"
        elif ctr == 1:
            ifd_name = "Thumbnail"
            thumb_ifd = ifd
        else:
            ifd_name = "IFD %d" % ctr
        logger.debug("IFD %d (%s) at offset %s:", ctr, ifd_name, ifd)
        hdr.dump_ifd(ifd, ifd_name, stop_tag=stop_tag)
        ctr += 1
    # EXIF IFD
    exif_off = hdr.tags.get("Image ExifOffset")
    if exif_off:
        logger.debug("Exif SubIFD at offset %s:", exif_off.values[0])
        hdr.dump_ifd(exif_off.values[0], "EXIF", stop_tag=stop_tag)

    # deal with MakerNote contained in EXIF IFD
    # (Some apps use MakerNote tags but do not use a format for which we
    # have a description, do not process these).
    if details and "EXIF MakerNote" in hdr.tags and "Image Make" in hdr.tags:
        hdr.decode_maker_note()

    # extract thumbnails
    if details or (thumb_ifd and extract_thumbnail):
        hdr.extract_tiff_thumbnail(thumb_ifd)
        hdr.extract_jpeg_thumbnail()

    # parse XMP tags (experimental)
    if debug and details:
        # Easy we already have them
        xmp_tag = hdr.tags.get("Image ApplicationNotes")
        if xmp_tag:
            logger.debug("XMP present in Exif")
            xmp_bytes = bytes(xmp_tag.values)
        # We need to look in the entire file for the XML
        else:
            xmp_bytes = _get_xmp(fh)
        if xmp_bytes:
            hdr.parse_xmp(xmp_bytes)

    if builtin_types:
        return convert_types(hdr.tags)

    return hdr.tags
