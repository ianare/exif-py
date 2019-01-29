# -*- Mode: Python -*-

# Find Exif data in an HEIC file.

# As of 2019, the latest standard seems to be "ISO/IEC 14496-12:2015"
# There are many different related standards. (quicktime, mov, mp4, etc...)
# See https://en.wikipedia.org/wiki/ISO_base_media_file_format for more details.

# We parse just enough of the iso format to locate the Exif data in the file.
# Inside the 'meta' box are two directories we need:
#   1) the 'iinf' box contains 'infe' records, we look for the item_ID for 'Exif'.
#   2) once we have the item_ID, we find a matching entry in the 'iloc' box, which
#      gives us position and size information.

import struct

from .exif_log import get_logger

logger = get_logger()

class WrongBox (Exception):
    pass
class NoParser (Exception):
    pass
class BoxVersion (Exception):
    pass
class BadSize (Exception):
    pass

class Box:
    def __init__ (self, name):
        self.name = name

    def __repr__ (self):
        return "<box '%s'>" % (self.name,)

class HEICExifFinder:

    def __init__ (self, file):
        self.file = file

    def get (self, nbytes):
        r = self.file.read (nbytes)
        if not r:
            raise EOFError
        else:
            return r

    def get16 (self):
        return struct.unpack ('>H', self.get (2))[0]

    def get32 (self):
        return struct.unpack ('>L', self.get (4))[0]

    def get64 (self):
        return struct.unpack ('>Q', self.get (8))[0]

    def get_int4x2 (self):
        n = struct.unpack ('>B', self.get(1))[0]
        n0 = n >> 4
        n1 = n & 0xf
        return n0, n1

    # some fields have variant-sized data.
    def get_int (self, size):
        if size == 2:
            return self.get16()
        elif size == 4:
            return self.get32()
        elif size == 8:
            return self.get64()
        elif size == 0:
            return 0
        else:
            raise BadSize (size)

    def get_string (self):
        r = []
        while 1:
            ch = self.get (1)
            if ch == b'\x00':
                break
            else:
                r.append (ch)
        return b''.join (r)

    def next_box (self, depth=0):
        pos = self.file.tell()
        size = self.get32()
        kind = self.get(4).decode('ascii')
        b = Box (kind)
        if size == 0:
            # signifies 'to the end of the file', we shouldn't see this.
            raise NotImplementedError
        elif size == 1:
            # 64-bit size follows type.
            size = self.get64()
            b.size = size - 16
            b.after = pos + size
        else:
            b.size = size - 8
            b.after = pos + size
        b.pos = self.file.tell()
        return b

    def get_full (self, box):
        # iso boxes come in 'old' and 'full' variants.  the 'full' variant
        #   contains version and flags information.
        vflags = self.get32()
        box.version = vflags >> 24
        box.flags = vflags & 0x00ffffff

    def skip (self, box):
        self.file.seek (box.after)

    def expect_parse (self, name):
        b = self.next_box()
        if b.name == name:
            return self.parse_box (b)
        else:
            raise WrongBox (name, b.name)

    def get_parser (self, box):
        method = 'parse_%s' % (box.name,)
        return getattr (self, method, None)

    def parse_box (self, b):
        probe = self.get_parser (b)
        if probe is None:
            raise NoParser (b.name)
        else:
            probe (b)
            # in case anything is left unread
            self.file.seek (b.after)
            return b

    def parse_ftyp (self, box):
        box.major_brand = self.get(4)
        box.minor_version = self.get32()
        box.compat = []
        size = box.size - 8
        while size > 0:
            box.compat.append (self.get (4))
            size -= 4

    def parse_meta (self, meta):
        self.get_full (meta)
        # this is full of boxes, but not in a predictable order.
        meta.subs = {}
        while self.file.tell() < meta.after:
            box = self.next_box()
            psub = self.get_parser (box)
            if psub is not None:
                psub (box)
                meta.subs[box.name] = box
            else:
                logger.debug("HEIC: skipping %r" % (box,))
            # skip any unparsed data
            self.skip (box)

    def parse_infe (self, box):
        self.get_full (box)
        if box.version >= 2:
            if box.version == 2:
                box.item_ID = self.get16()
            elif box.version == 3:
                box.item_ID = self.get32()
            box.item_protection_index = self.get16()
            box.item_type = self.get(4)
            box.item_name = self.get_string()
            # ignore the rest
        else:
            box.item_type = ''

    def parse_iinf (self, box):
        self.get_full (box)
        count = self.get16()
        box.exif_infe = None
        for _ in range (count):
            infe = self.expect_parse ('infe')
            if infe.item_type == b'Exif':
                logger.debug("HEIC: found Exif 'infe' box")
                box.exif_infe = infe
                break

    def parse_iloc (self, box):
        self.get_full (box)
        s0, s1 = self.get_int4x2()
        s2, s3 = self.get_int4x2()
        box.offset_size = s0
        box.length_size = s1
        box.base_offset_size = s2
        box.index_size = s3
        if box.version < 2:
            box.item_count = self.get16()
        elif box.version == 2:
            box.item_count = self.get32()
        else:
            raise BoxVersion (2, box.version)
        box.locs = {}
        logger.debug("HEIC: %d iloc items" % (box.item_count,))
        for i in range (box.item_count):
            if box.version < 2:
                item_ID = self.get16()
            elif box.version == 2:
                item_ID = self.get32()
            else:
                # notreached
                raise BoxVersion (2, box.version)
            if box.version in (1, 2):
                # ignore construction_method
                _ = self.get16()
            data_reference_index = self.get16()
            box.base_offset = self.get_int (box.base_offset_size)
            extent_count = self.get16()
            extents = []
            for _ in range (extent_count):
                if box.version in (1, 2) and box.index_size > 0:
                    extent_index = self.get_int (box.index_size)
                else:
                    extent_index = -1
                extent_offset = self.get_int (box.offset_size)
                extent_length = self.get_int (box.length_size)
                extents.append ((extent_offset, extent_length))
            box.locs[item_ID] = extents

    def find_exif (self):
        ftyp = self.expect_parse ('ftyp')
        assert ftyp.major_brand == b'heic'
        assert ftyp.minor_version == 0
        meta = self.expect_parse ('meta')
        item_ID = meta.subs['iinf'].exif_infe.item_ID
        extents = meta.subs['iloc'].locs[item_ID]
        logger.debug("HEIC: found Exif location.")
        # we expect the Exif data to be in one piece.
        assert len(extents) == 1
        pos, size = extents[0]
        # looks like there's a kind of pseudo-box here.
        self.file.seek (pos)
        size1 = self.get32()
        assert self.get(size1)[0:4] == b'Exif'
        offset = self.file.tell()
        endian = self.file.read(1)
        return offset, endian
