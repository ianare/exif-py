"""
Read Exif metadata from image files
Supported formats: TIFF, JPEG, PNG, Webp, HEIC
"""

from typing import Any, BinaryIO, Dict

from exifread.core.exceptions import ExifNotFound, InvalidExif
from exifread.core.exif_header import ExifHeader
from exifread.core.find_exif import determine_type, get_endian_str
from exifread.exif_log import get_logger
from exifread.serialize import convert_types
from exifread.tags import DEFAULT_STOP_TAG

__version__ = "3.3.1"

logger = get_logger()


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
        offset, endian_bytes, fake_exif = determine_type(fh)
    except ExifNotFound as err:
        logger.warning(err)
        return {}
    except InvalidExif as err:
        logger.debug(err)
        return {}

    endian_str, endian_type = get_endian_str(endian_bytes)
    # deal with the EXIF info we found
    logger.debug("Endian format is %s (%s)", endian_str, endian_type)

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
        hdr.dump_ifd(ifd=ifd, ifd_name=ifd_name, stop_tag=stop_tag)
        ctr += 1
    # EXIF IFD
    exif_off = hdr.tags.get("Image ExifOffset")
    if exif_off:
        logger.debug("Exif SubIFD at offset %s:", exif_off.values[0])
        hdr.dump_ifd(ifd=exif_off.values[0], ifd_name="EXIF", stop_tag=stop_tag)

    # deal with MakerNote contained in EXIF IFD
    # (Some apps use MakerNote tags but do not use a format for which we
    # have a description, do not process these).
    if details and "EXIF MakerNote" in hdr.tags and "Image Make" in hdr.tags:
        hdr.decode_maker_note()

    # extract thumbnails
    if thumb_ifd and extract_thumbnail:
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
