import struct
from typing import Any, List, Dict, Callable, BinaryIO, Optional
from exifread.exif_log import get_logger

class WrongBox(Exception):
    pass

class BoxVersion(Exception):
    pass

class BadSize(Exception):
    pass

class Box:
    def __init__(self, name: str):
        self.name = name
        self.version = 0
        self.minor_version = 0
        self.item_count = 0
        self.size = 0
        self.after = 0
        self.pos = 0
        self.compat = []
        self.base_offset = 0
        self.subs = {}
        self.locs = {}
        self.exif_infe = None
        self.item_id = 0
        self.item_type = b''
        self.item_name = b''
        self.item_protection_index = 0
        self.major_brand = b''
        self.offset_size = 0
        self.length_size = 0
        self.base_offset_size = 0
        self.index_size = 0
        self.flags = 0

class HEICExifFinder:
    def __init__(self, file_handle: BinaryIO):
        self.file_handle = file_handle

    def get(self, nbytes: int) -> bytes:
        read = self.file_handle.read(nbytes)
        if not read:
            raise EOFError
        if len(read) != nbytes:
            raise BadSize
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
        while True:
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
            raise NotImplementedError
        if size == 1:
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

    def get_parser(self, box: Box) -> Optional[Callable[[Box], Any]]:
        defs = {
            'ftyp': self._parse_ftyp,
            'meta': self._parse_meta,
            'infe': self._parse_infe,
            'iinf': self._parse_iinf,
            'iloc': self._parse_iloc,
        }
        return defs.get(box.name)

    def parse_box(self, box: Box) -> Box:
        probe = self.get_parser(box)
        if probe is not None:
            probe(box)
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

    def _parse_iinf(self, box: Box):
        self.get_full(box)
        count = self.get16()
        box.exif_infe = None
        for _ in range(count):
            infe = self.expect_parse('infe')
            if infe.item_type == b'Exif':
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
        box.locs = {}
        for _ in range(box.item_count):
            if box.version < 2:
                item_id = self.get16()
            elif box.version == 2:
                item_id = self.get32()
            if box.version in (1, 2):
                self.get16()
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
        meta = self.expect_parse('meta')
        assert ftyp.major_brand == b'heic'
        assert ftyp.minor_version == 0
        assert meta.subs['iinf'].exif_infe is not None
        item_id = meta.subs['iinf'].exif_infe.item_id
        extents = meta.subs['iloc'].locs[item_id]
        assert len(extents) == 1
        pos, _ = extents[0]
        self.file_handle.seek(pos)
        exif_tiff_header_offset = self.get32()
        assert exif_tiff_header_offset >= 6
        assert self.get(exif_tiff_header_offset)[-6:] == b'Exif\x00\x00'
        offset = self.file_handle.tell()
        endian = self.file_handle.read(1)
        return offset, endian
