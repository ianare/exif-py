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
    
}

# maker notes for Reconyx HF2 PRO cameras (ref 3)
# ported from https://fossies.org/linux/Image-ExifTool/lib/Image/ExifTool/Reconyx.pm
TAGS_TYPE_3 = {
    
}
