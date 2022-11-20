"""
Makernote (proprietary) tag definitions for DJI cameras

Based on https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/DJI.pm
"""

TAGS = {
    0x03: ('SpeedX', ),
    0x04: ('SpeedY', ),
    0x05: ('SpeedZ', ),
    0x06: ('Pitch', ),
    0x07: ('Yaw', ),
    0x08: ('Roll', ),
    0x09: ('CameraPitch', ),
    0x0a: ('CameraYaw', ),
    0x0b: ('CameraRoll', ),
}
