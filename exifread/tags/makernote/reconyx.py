from ...utils import make_string

# maker notes for Reconyx Hyperfire cameras (ref PH)
# ported from https://fossies.org/linux/Image-ExifTool/lib/Image/ExifTool/Reconyx.pm
TAGS_MAIN = {
    0x00: ('MakerNoteVersion', make_string),  # Sometimes binary
    0x01: ('FirmwareVersion', ),
    
}

# maker notes for Reconyx UltraFire cameras (ref PH)
# ported from https://fossies.org/linux/Image-ExifTool/lib/Image/ExifTool/Reconyx.pm
TAGS_TYPE_2 = {
    0x18: ('FirmwareVersion', ),
    0x1f: ('Micro1Version', ),
    0x26: ('BootLoaderVersion', ),
    0x2d: ('Micro2Version', ),
}

# maker notes for Reconyx HF2 PRO cameras (ref 3)
# ported from https://fossies.org/linux/Image-ExifTool/lib/Image/ExifTool/Reconyx.pm
TAGS_TYPE_3 = {
    0x10: ('FileNumber', ),
    0x12: ('DirectoryNumber', ),
}
