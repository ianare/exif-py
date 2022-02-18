# Find Exif data in an HEIC file.

# As of 2019, the latest standard seems to be "ISO/IEC 14496-12:2015"
# There are many different related standards. (quicktime, mov, mp4, etc...)
# See https://en.wikipedia.org/wiki/ISO_base_media_file_format for more details.

# We parse just enough of the ISO format to locate the Exif data in the file.
# Inside the 'meta' box are two directories we need:
#   1) the 'iinf' box contains 'infe' records, we look for the item_id for 'Exif'.
#   2) once we have the item_id, we find a matching entry in the 'iloc' box, which
#      gives us position and size information.

import struct
from typing import List, Dict, Callable, BinaryIO, Optional

from exifread.exif_log import get_logger

logger = get_logger()


class WrongBox(Exception):
    pass
class NoParser(Exception):
    pass
class BoxVersion(Exception):
    pass
class BadSize(Exception):
    pass


class Box:
    version = 0
    minor_version = 0
    item_count = 0
    size = 0
    after = 0
    pos = 0
    compat = []  # type: List
    base_offset = 0
    # this is full of boxes, but not in a predictable order.
    subs = {}  # type: Dict[str, Box]
    locs = {}  # type: Dict
    exif_infe = None  # type: Optional[Box]
    item_id = 0
    item_type = b''
    item_name = b''
    item_protection_index = 0
    major_brand = b''
    offset_size = 0
    length_size = 0
    base_offset_size = 0
    index_size = 0
    flags = 0

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "<box '%s'>" % self.name

    def set_sizes(self, offset: int, length: int, base_offset: int, index: int):
        self.offset_size = offset
        self.length_size = length
        self.base_offset_size = base_offset
        self.index_size = index

    def set_full(self, vflags: int):
        """
        ISO boxes come in 'old' and 'full' variants.
        The 'full' variant contains version and flags information.
        """
        self.version = vflags >> 24
        self.flags = vflags & 0x00ffffff


class HEICExifFinder:

    def __init__(self, file_handle: BinaryIO):
        self.file_handle = file_handle

    def get(self, nbytes: int) -> bytes:
        read = self.file_handle.read(nbytes)
        if not read:
            raise EOFError
        if len(read) != nbytes:
            msg = "get(nbytes={nbytes}) found {read} bytes at position {pos}".format(
                nbytes=nbytes,
                read=len(read),
                pos=self.file_handle.tell()
            )
            raise BadSize(msg)
        return read

    def get16(self) -> int:
        return struct.unpack('>H', self.get(2))[0]

    def get32(self) -> int:
        return struct.unpack('>L', self.get(4))[0]

    def get64(self) -> int:
        return struct.unpack('>Q', self.get(8))[0]

    def get_int4x2(self) -> tuple:
        num = struct.unpack('>B', self.get(1))[0]
        num0 = num >> 4
        num1 = num & 0xf
        return num0, num1

    def get_int(self, size: int) -> int:
        """some fields have variant-sized data."""
        if size == 2:
            return self.get16()
        if size == 4:
            return self.get32()
        if size == 8:
            return self.get64()
        if size == 0:
            return 0
        raise BadSize(size)

    def get_string(self) -> bytes:
        read = []
        while 1:
            char = self.get(1)
            if char == b'\x00':
                break
            read.append(char)
        return b''.join(read)

    def next_box(self) -> Box:
        pos = self.file_handle.tell()
        size = self.get32()
        kind = self.get(4).decode('ascii')
        box = Box(kind)
        if size == 0:
            # signifies 'to the end of the file', we shouldn't see this.
            raise NotImplementedError
        if size == 1:
            # 64-bit size follows type.
            size = self.get64()
            box.size = size - 16
            box.after = pos + size
        else:
            box.size = size - 8
            box.after = pos + size
        box.pos = self.file_handle.tell()
        return box

    def get_full(self, box: Box):
        box.set_full(self.get32())

    def skip(self, box: Box):
        self.file_handle.seek(box.after)

    def expect_parse(self, name: str) -> Box:
        while True:
            box = self.next_box()
            if box.name == name:
                return self.parse_box(box)
            self.skip(box)

    def get_parser(self, box: Box) -> Callable:
        defs = {
            'ftyp': self._parse_ftyp,
            'meta': self._parse_meta,
            'infe': self._parse_infe,
            'iinf': self._parse_iinf,
            'iloc': self._parse_iloc,
        }
        try:
            return defs[box.name]
        except (IndexError, KeyError) as err:
            raise NoParser(box.name) from err

    def parse_box(self, box: Box) -> Box:
        probe = self.get_parser(box)
        probe(box)
        # in case anything is left unread
        self.file_handle.seek(box.after)
        return box

    def _parse_ftyp(self, box: Box):
        box.major_brand = self.get(4)
        box.minor_version = self.get32()
        box.compat = []
        size = box.size - 8
        while size > 0:
            box.compat.append(self.get(4))
            size -= 4

    def _parse_meta(self, meta: Box):
        self.get_full(meta)
        while self.file_handle.tell() < meta.after:
            box = self.next_box()
            psub = self.get_parser(box)
            if psub is not None:
                psub(box)
                meta.subs[box.name] = box
            else:
                logger.debug('HEIC: skipping %r', box)
            # skip any unparsed data
            self.skip(box)

    def _parse_infe(self, box: Box):
        self.get_full(box)
        if box.version >= 2:
            if box.version == 2:
                box.item_id = self.get16()
            elif box.version == 3:
                box.item_id = self.get32()
            box.item_protection_index = self.get16()
            box.item_type = self.get(4)
            box.item_name = self.get_string()
            # ignore the rest

    def _parse_iinf(self, box: Box):
        self.get_full(box)
        count = self.get16()
        box.exif_infe = None
        for _ in range(count):
            infe = self.expect_parse('infe')
            if infe.item_type == b'Exif':
                logger.debug("HEIC: found Exif 'infe' box")
                box.exif_infe = infe
                break

    def _parse_iloc(self, box: Box):
        self.get_full(box)
        size0, size1 = self.get_int4x2()
        size2, size3 = self.get_int4x2()
        box.set_sizes(size0, size1, size2, size3)
        if box.version < 2:
            box.item_count = self.get16()
        elif box.version == 2:
            box.item_count = self.get32()
        else:
            raise BoxVersion(2, box.version)
        box.locs = {}
        logger.debug('HEIC: %d iloc items', box.item_count)
        for _ in range(box.item_count):
            if box.version < 2:
                item_id = self.get16()
            elif box.version == 2:
                item_id = self.get32()
            else:
                # notreached
                raise BoxVersion(2, box.version)
            if box.version in (1, 2):
                # ignore construction_method
                self.get16()
            # ignore data_reference_index
            self.get16()
            box.base_offset = self.get_int(box.base_offset_size)
            extent_count = self.get16()
            extents = []
            for _ in range(extent_count):
                if box.version in (1, 2) and box.index_size > 0:
                    self.get_int(box.index_size)
                extent_offset = self.get_int(box.offset_size)
                extent_length = self.get_int(box.length_size)
                extents.append((extent_offset, extent_length))
            box.locs[item_id] = extents

    def find_exif(self) -> tuple:
        ftyp = self.expect_parse('ftyp')
        assert ftyp.major_brand == b'heic'
        assert ftyp.minor_version == 0
        meta = self.expect_parse('meta')
        assert meta.subs['iinf'].exif_infe is not None
        item_id = meta.subs['iinf'].exif_infe.item_id
        extents = meta.subs['iloc'].locs[item_id]
        logger.debug('HEIC: found Exif location.')
        # we expect the Exif data to be in one piece.
        assert len(extents) == 1
        pos, _ = extents[0]
        # looks like there's a kind of pseudo-box here.
        self.file_handle.seek(pos)
        # the payload of "Exif" item may be start with either
        # b'\xFF\xE1\xSS\xSSExif\x00\x00' (with APP1 marker, e.g. Android Q)
        # or
        # b'Exif\x00\x00' (without APP1 marker, e.g. iOS)
        # according to "ISO/IEC 23008-12, 2017-12", both of them are legal
        exif_tiff_header_offset = self.get32()
        assert exif_tiff_header_offset >= 6
        assert self.get(exif_tiff_header_offset)[-6:] == b'Exif\x00\x00'
        offset = self.file_handle.tell()
        endian = self.file_handle.read(1)
        return offset, endian
