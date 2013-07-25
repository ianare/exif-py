# -*- coding: utf-8 -*-

from classes import *
from tags import *

def process_file(f, stop_tag=DEFAULT_STOP_TAG, detailed=True, strict=False, debug=False):
    """
    Process an image file (expects an open file object).

    This is the function that has to deal with all the arbitrary nasty bits
    of the EXIF standard.
    """

    # by default do not fake an EXIF beginning
    fake_exif = 0

    # determine whether it's a JPEG or TIFF
    data = f.read(12)
    if data[0:4] in ['II*\x00', 'MM\x00*']:
        # it's a TIFF file
        f.seek(0)
        endian = f.read(1)
        f.read(1)
        offset = 0
    elif data[0:2] == '\xFF\xD8':
        # it's a JPEG file
        if debug: print("JPEG format recognized data[0:2] == '0xFFD8'.")
        base = 2
        while data[2] == '\xFF' and data[6:10] in ('JFIF', 'JFXX', 'OLYM', 'Phot'):
            if debug: print("data[2] == 0xxFF data[3]==%x and data[6:10] = %s"%(ord(data[3]),
                        data[6:10]))
            length = ord(data[4])*256+ord(data[5])
            if debug: print("Length offset is", length)
            f.read(length-8)
            # fake an EXIF beginning of file
            # I don't think this is used. --gd
            data = '\xFF\x00' + f.read(10)
            fake_exif = 1
            if base > 2:
                if debug: print("added to base ")
                base = base + length + 4 -2
            else:
                if debug: print("added to zero ")
                base = length + 4
            if debug: print("Set segment base to", base)

        # Big ugly patch to deal with APP2 (or other) data coming before APP1
        f.seek(0)
        # in theory, this could be insufficient since 64K is the maximum size--gd
        data = f.read(base + 4000)
        # base = 2
        while 1:
            if debug: print("Segment base 0x%X" % base)
            if data[base:base+2] == '\xFF\xE1':
                # APP1
                if debug: print("APP1 at base", hex(base))
                if debug: print("Length", hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code", data[base+4:base+8])
                if data[base+4:base+8] == "Exif":
                    if debug: print("Decrement base by", 2,
                                    "to get to pre-segment header (for compatibility with later code)")
                    base = base-2
                    break
                increment = ord(data[base+2])*256+ord(data[base+3])+2
                if debug: print("Increment base by", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xE0':
                # APP0
                if debug: print("APP0 at base", hex(base))
                if debug: print("Length", hex(ord(data[base+2])),
                                hex(ord(data[base+3])))
                if debug: print("Code", data[base+4:base+8])
                increment = ord(data[base+2])*256+ord(data[base+3])+2
                if debug: print("Increment base by", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xE2':
                # APP2
                if debug: print("APP2 at base", hex(base))
                if debug: print("Length", hex(ord(data[base+2])),
                                hex(ord(data[base+3])))
                if debug: print("Code", data[base+4:base+8])
                increment = ord(data[base+2])*256+ord(data[base+3])+2
                if debug: print("Increment base by", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xEE':
                # APP14
                if debug: print("APP14 Adobe segment at base", hex(base))
                if debug: print("Length", hex(ord(data[base+2])),
                                hex(ord(data[base+3])))
                if debug: print("Code", data[base+4:base+8])
                increment = ord(data[base+2])*256+ord(data[base+3])+2
                if debug: print("Increment base by", increment)
                base = base + increment
                print("There is useful EXIF-like data here, but we have no parser for it.")
            elif data[base:base+2] == '\xFF\xDB':
                if debug: print("JPEG image data at base", hex(base),
                                "No more segments are expected.")
                # sys.exit(0)
                break
            elif data[base:base+2] == '\xFF\xD8':
                # APP12
                if debug: print("FFD8 segment at base", hex(base))
                if debug: print("Got", hex(ord(data[base])),
                                hex(ord(data[base+1])), "and",
                                data[4+base:10+base], "instead.")
                if debug: print("Length", hex(ord(data[base+2])),
                                hex(ord(data[base+3])))
                if debug: print("Code", data[base+4:base+8])
                increment = ord(data[base+2])*256+ord(data[base+3])+2
                if debug: print("Increment base by", increment)
                base = base + increment
            elif data[base:base+2] == '\xFF\xEC':
                # APP12
                if debug: print("APP12 XMP (Ducky) or Pictureinfo segment at base", hex(base))
                if debug: print("Got", hex(ord(data[base])), hex(ord(data[base+1])),
                                "and", data[4+base:10+base], "instead.")
                if debug: print("Length", hex(ord(data[base+2])), hex(ord(data[base+3])))
                if debug: print("Code", data[base+4:base+8])
                increment = ord(data[base+2])*256+ord(data[base+3])+2
                if debug: print("Increment base by", increment)
                base = base + increment
                print("There is useful EXIF-like data here (quality, comment, copyright),",
                      "but we have no parser for it.")
            else:
                try:
                    increment = ord(data[base+2])*256+ord(data[base+3])+2
                    if debug: print("Got", hex(ord(data[base])), hex(ord(data[base+1])),
                                    "and", data[4+base:10+base], "instead.")
                except:
                    if debug: print("Unexpected/unhandled segment type or file content.")
                    return {}
                else:
                    if debug: print("Increment base by", increment)
                    base = base + increment
        f.seek(base + 12)
        if data[2+base] == '\xFF' and data[6+base:10+base] == 'Exif':
            # detected EXIF header
            offset = f.tell()
            endian = f.read(1)
            #HACK TEST:  endian = 'M'
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Ducky':
            # detected Ducky header.
            if debug: print("EXIF-like header (normally 0xFF and code):",
                            hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        elif data[2+base] == '\xFF' and data[6+base:10+base+1] == 'Adobe':
            # detected APP14 (Adobe)
            if debug: print("EXIF-like header (normally 0xFF and code):",
                            hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            offset = f.tell()
            endian = f.read(1)
        else:
            # no EXIF information
            if debug: print("No EXIF header expected data[2+base]==0xFF and data[6+base:10+base]===Exif (or Duck)")
            if debug: print(" but got", hex(ord(data[2+base])) , "and", data[6+base:10+base+1])
            return {}
    else:
        # file format not recognized
        if debug: print("file format not recognized")
        return {}

    # deal with the EXIF info we found
    if debug:
        print("Endian format is ", endian)
        print({'I': 'Intel', 'M': 'Motorola', '\x01':'Adobe Ducky', 'd':'XMP/Adobe unknown' }[endian], 'format')

    hdr = ExifHeader(f, endian, offset, fake_exif, strict, debug)
    ifd_list = hdr.list_IFDs()
    ctr = 0
    for i in ifd_list:
        if ctr == 0:
            IFD_name = 'Image'
        elif ctr == 1:
            IFD_name = 'Thumbnail'
            thumb_ifd = i
        else:
            IFD_name = 'IFD %d' % ctr
        if debug:
            print(' IFD %d (%s) at offset %d:' % (ctr, IFD_name, i))
        hdr.dump_IFD(i, IFD_name, stop_tag=stop_tag)
        # EXIF IFD
        exif_off = hdr.tags.get(IFD_name+' ExifOffset')
        if exif_off:
            if debug:
                print(' EXIF SubIFD at offset %d:' % exif_off.values[0])
            hdr.dump_IFD(exif_off.values[0], 'EXIF', stop_tag=stop_tag)
            # Interoperability IFD contained in EXIF IFD
            intr_off = hdr.tags.get('EXIF SubIFD InteroperabilityOffset')
            if intr_off:
                if debug:
                    print(' EXIF Interoperability SubSubIFD at offset %d:' \
                          % intr_off.values[0])
                hdr.dump_IFD(intr_off.values[0], 'EXIF Interoperability',
                             dict=INTR_TAGS, stop_tag=stop_tag)
        # GPS IFD
        gps_off = hdr.tags.get(IFD_name+' GPSInfo')
        if gps_off:
            if debug:
                print(' GPS SubIFD at offset %d:' % gps_off.values[0])
            hdr.dump_IFD(gps_off.values[0], 'GPS', dict=GPS_TAGS, stop_tag=stop_tag)
        ctr += 1

    # extract uncompressed TIFF thumbnail
    thumb = hdr.tags.get('Thumbnail Compression')
    if thumb and thumb.printable == 'Uncompressed TIFF':
        hdr.extract_TIFF_thumbnail(thumb_ifd)

    # JPEG thumbnail (thankfully the JPEG data is stored as a unit)
    thumb_off = hdr.tags.get('Thumbnail JPEGInterchangeFormat')
    if thumb_off:
        f.seek(offset+thumb_off.values[0])
        size = hdr.tags['Thumbnail JPEGInterchangeFormatLength'].values[0]
        hdr.tags['JPEGThumbnail'] = f.read(size)

    # deal with MakerNote contained in EXIF IFD
    # (Some apps use MakerNote tags but do not use a format for which we
    # have a description, do not process these).
    if 'EXIF MakerNote' in hdr.tags and 'Image Make' in hdr.tags and detailed:
        hdr.decode_maker_note()

    # Sometimes in a TIFF file, a JPEG thumbnail is hidden in the MakerNote
    # since it's not allowed in a uncompressed TIFF IFD
    if 'JPEGThumbnail' not in hdr.tags:
        thumb_off = hdr.tags.get('MakerNote JPEGThumbnail')
        if thumb_off:
            f.seek(offset+thumb_off.values[0])
            hdr.tags['JPEGThumbnail'] = file.read(thumb_off.field_length)

    return hdr.tags
