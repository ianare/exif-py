from ...utils import make_string

# maker notes for Reconyx Hyperfire cameras (ref PH)
# ported from https://fossies.org/linux/Image-ExifTool/lib/Image/ExifTool/Reconyx.pm
TAGS_HYPERFIRE = {
    0x00: ('MakerNoteVersion', make_string),  # Sometimes binary
    0x01: ('FirmwareVersion', ),
    0x04: ('FirmwareDate', ),
    0x06: ('TriggerMode', ),
    0x07: ('Sequence', ),
    0x09: ('EventNumber', ),
    0x0b: ('DateTimeOriginal', ),
    0x12: ('MoonPhase', {
            0: 'New',
            1: 'New Crescent',
            2: 'First Quarter',
            3: 'Waxing Gibbous',
            4: 'Full',
            5: 'Waning Gibbous',
            6: 'Last Quarter',
            7: 'Old Crescent'
    }),
    0x13: ('AmbientTemperatureFahrenheit', ),
    0x14: ('AmbientTemperature', ),
    0x15: ('SerialNumber', ),
    0x24: ('Contrast', ),
    0x25: ('Brightness', ),
    0x26: ('Sharpness', ),
    0x27: ('Saturation', ),
    0x28: ('InfraredIlluminator', ),
    0x29: ('MotionSensitivity', ),
    0x2a: ('BatteryVoltage', ),
    0x2b: ('UserLabel', )
}

# maker notes for Reconyx UltraFire cameras (ref PH)
# ported from https://fossies.org/linux/Image-ExifTool/lib/Image/ExifTool/Reconyx.pm
TAGS_ULTRAFIRE = {
    0x18: ('FirmwareVersion', ),
    0x1f: ('Micro1Version', ),
    0x26: ('BootLoaderVersion', ),
    0x2d: ('Micro2Version', ),
    0x34: ('TriggerMode', ),
    0x35: ('Sequence', ),
    0x37: ('EventNumber', ),
    0x3b: ('DateTimeOriginal', ),
    0x42: ('DayOfWeek', ),
    0x43: ('MoonPhase', {
            0: 'New',
            1: 'New Crescent',
            2: 'First Quarter',
            3: 'Waxing Gibbous',
            4: 'Full',
            5: 'Waning Gibbous',
            6: 'Last Quarter',
            7: 'Old Crescent'
    }),
    0x44: ('AmbientTemperatureFahrenheit', ),
    0x46: ('AmbientTemperature', ),
    0x48: ('Illumination', ),
    0x49: ('BatteryVoltage', ),
    0x4b: ('SerialNumber', ),
    0x5a: ('UserLabel', )
}

# maker notes for Reconyx HF2 PRO cameras (ref 3)
# ported from https://fossies.org/linux/Image-ExifTool/lib/Image/ExifTool/Reconyx.pm
TAGS_HF2PRO = {
    0x10: ('FileNumber', ),
    0x12: ('DirectoryNumber', ),
    0x2a: ('FirmwareVersion', ),
    0x30: ('FirmwareDate', ),
    0x34: ('TriggerMode', ),
    0x36: ('Sequence', ),
    0x3a: ('EventNumber', ),
    0x3e: ('DateTimeOriginal', ),
    0x4a: ('DayOfWeek', ),
    0x4c: ('MoonPhase', {
            0: 'New',
            1: 'New Crescent',
            2: 'First Quarter',
            3: 'Waxing Gibbous',
            4: 'Full',
            5: 'Waning Gibbous',
            6: 'Last Quarter',
            7: 'Old Crescent'
    }),
    0x4e: ('AmbientTemperatureFahrenheit', ),
    0x50: ('AmbientTemperature', ),
    0x52: ('Contrast', ),
    0x54: ('Brightness', ),
    0x56: ('Sharpness', ),
    0x58: ('Saturation', ),
    0x5a: ('Flash', ),
    0x5c: ('AmbientInfrared', ),
    0x5e: ('AmbientLight', ),
    0x60: ('MotionSensitivity', ),
    0x62: ('BatteryVoltage', ),
    0x64: ('BatteryVoltageAvg', ),
    0x66: ('BatteryType', ),
    0x68: ('UserLabel', ),
    0x7e: ('SerialNumber', ),
}
