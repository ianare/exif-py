
from ...utils import make_string, Ratio


def ev_bias(seq) -> str:
    """
    First digit seems to be in steps of 1/6 EV.
    Does the third value mean the step size?  It is usually 6,
    but it is 12 for the ExposureDifference.
    Check for an error condition that could cause a crash.
    This only happens if something has gone really wrong in
    reading the Nikon MakerNote.
    http://tomtia.plala.jp/DigitalCamera/MakerNote/index.asp
    """
    if len(seq) < 4:
        return ''
    if seq == [252, 1, 6, 0]:
        return '-2/3 EV'
    if seq == [253, 1, 6, 0]:
        return '-1/2 EV'
    if seq == [254, 1, 6, 0]:
        return '-1/3 EV'
    if seq == [0, 1, 6, 0]:
        return '0 EV'
    if seq == [2, 1, 6, 0]:
        return '+1/3 EV'
    if seq == [3, 1, 6, 0]:
        return '+1/2 EV'
    if seq == [4, 1, 6, 0]:
        return '+2/3 EV'
    # Handle combinations not in the table.
    i = seq[0]
    # Causes headaches for the +/- logic, so special case it.
    if i == 0:
        return '0 EV'
    if i > 127:
        i = 256 - i
        ret_str = '-'
    else:
        ret_str = '+'
    step = seq[2]  # Assume third value means the step size
    whole = i / step
    i = i % step
    if whole != 0:
        ret_str = '%s%s ' % (ret_str, str(whole))
    if i == 0:
        ret_str += 'EV'
    else:
        ratio = Ratio(i, step)
        ret_str = ret_str + str(ratio) + ' EV'
    return ret_str


# Nikon E99x MakerNote Tags
#
# NOTE: Byte field values are actually integer representations in this module so keys should
# be integers.
TAGS_NEW = {
    0x0001: ('MakernoteVersion', make_string),  # Sometimes binary
    0x0002: ('ISOSetting', ),
    0x0003: ('ColorMode', ),
    0x0004: ('Quality', ),
    0x0005: ('Whitebalance', ),
    0x0006: ('ImageSharpening', ),
    0x0007: ('FocusMode', ),
    0x0008: ('FlashSetting', ),
    0x0009: ('AutoFlashMode', ),
    0x000A: ('LensMount', ),    # According to LibRAW
    0x000B: ('WhiteBalanceBias', ),
    0x000C: ('WhiteBalanceRBCoeff', ),
    0x000D: ('ProgramShift', ev_bias),
    # Nearly the same as the other EV vals, but step size is 1/12 EV (?)
    0x000E: ('ExposureDifference', ev_bias),
    0x000F: ('ISOSelection', ),
    0x0010: ('DataDump', ),
    0x0011: ('NikonPreview', ),
    0x0012: ('FlashCompensation', ev_bias),
    0x0013: ('ISOSpeedRequested', ),
    0x0014: ('ColorBalance', ),     # According to LibRAW
    0x0016: ('PhotoCornerCoordinates', ),
    0x0017: ('ExternalFlashExposureComp', ev_bias),
    0x0018: ('FlashBracketCompensationApplied', ev_bias),
    0x0019: ('AEBracketCompensationApplied', ),
    0x001A: ('ImageProcessing', ),
    0x001B: ('CropHiSpeed', [
        {
            0: 'Off',
            1: '1.3x',
            2: 'DX',
            3: '5:4',
            4: '3:2',
            6: '16:9',
            8: '2.7x',
            9: 'DX Movie',
            10: '1.3x Movie',
            11: 'FX Uncropper',
            12: 'DX Uncropped',
            15: '1.5x Movie',
            17: '1:1'
        },
        {},
        {},
        {},
        {},
        {},
        {},
    ]),
    0x001C: ('ExposureTuning', ),
    0x001D: ('SerialNumber', ),  # Conflict with 0x00A0 ?
    0x001E: ('ColorSpace', {
        1: 'sRGB',
        2: 'Adobe RGB'
    }),
    0x001F: ('VRInfo', ),
    0x0020: ('ImageAuthentication', {
        0: 'Off',
        1: 'On'
    }),
    0x0021: ('FaceDetect', ),
    0x0022: ('ActiveDLighting', {
        0: 'Off',
        1: 'Low',
        3: 'Normal',
        5: 'High',
        7: 'Extra High',
        8: 'Extra High 1',
        9: 'Extra High 2',
        10: 'Extra High 3',
        11: 'Extra High 4',
        65535: 'Auto'
    }),
    0x0023: ('PictureControl', ),
    0x0024: ('WorldTime', ),
    0x0025: ('ISOInfo', ),
    0x002A: ('VignetteControl', {
        0: 'Off',
        1: 'Low',
        3: 'Normal',
        5: 'High'
    }),
    0x002B: ('DistortInfo', ),
    0x002C: ('UnknownInfo', ),      # Using what ExifTool uses
    0x0032: ('UnknownInfo2', ),     # Using what ExifTool uses
    0x0034: ('ShutterMode', {
        0: 'Mechanical',
        16: 'Electronic',
        48: 'Electronic Front Curtain',
        64: 'Electronic (Movie)',
        80: 'Auto (Mechanical)',
        81: 'Auto (Electronic Front Curtain)',
    }),
    0x0035: ('HDRInfo', ),
    0x0037: ('MechanicalShutterCount', ),
    0x0039: ('LocationInfo', ),
    # 0x003A: unknown
    0x003B: ('MultiExposureWhiteBalance', ),
    # 0x003C: unknown
    0x003D: ('BlackLevel', ),
    # 0x003E: unknown
    # 0x003F: unknown
    # 0x0040: unknown
    # 0x0041: unknown
    # 0x0042: unknown
    # 0x0043: unknown
    # 0x0044: unknown
    0x0045: ('CropArea', ),     # (left, top, width, height) / left pixel (x,y), size (width,length)
    # 0x0046: unknown
    # 0x0047: unknown
    # 0x0048: unknown
    # 0x0049: unknown
    # 0x004A: unknown
    # 0x004B: unknown
    # 0x004C: unknown
    # 0x004D: unknown
    0x004E: ('NikonSettings', ),
    0x004F: ('ColorTemperatureAuto', ),
    0x0080: ('ImageAdjustment', ),
    0x0081: ('ToneCompensation', ),
    0x0082: ('AuxiliaryLens', ),
    # About the table below:
    # * All G lenses are also D lenses but not vice versa.
    # * G lens names do not include the D
    # * All G and D lenses are also AF
    # * G and D don't even refer to related feature or lens characteristics
    # * Nikon doesn't differentiate AF, AF-I, or AF-S lenses but does with AF-P
    # * AF-{I,S,P} are autofocus technology types
    # * But sometimes Nikon likes to write AF-D or AF-G too in documentation
    # * VR is an additional lens feature.
    0x0083: ('LensType', {  # FIXME: We should form the string instead of listing every possible combo
        0: 'AF',
        1: 'MF',
        2: 'AF D',
        6: 'AF G',
        8: 'VR',
        10: 'AF D VR',
        14: 'AF G VR',
        128: 'AF-P',
        142: 'AF-P G VR'
    }),
    0x0084: ('LensMinMaxFocalMaxAperture', ),
    0x0085: ('ManualFocusDistance', ),
    0x0086: ('DigitalZoomFactor', ),
    0x0087: ('FlashMode', {
        0: 'Did Not Fire',
        1: 'Fired, Manual',
        3: 'Not Ready',
        7: 'Fired, External',
        8: 'Fired, Commander Mode ',
        9: 'Fired, TTL Mode',
    }),
    0x0088: ('AFInfo', ),   # FIXME: This is a list where each position has a different meaning
    0x0089: ('ShootingMode', {  # FIXME: We should form the string instead of listing every possible combo
        0: 'Single frame',
        1: 'Continuous',
        2: 'Delay',
        8: 'b3 ???',
        10: 'b3 ???, Delay',
        16: 'Exposure Bracketing',
        17: 'Exposure Bracketing, Continuous',
        18: 'Exposure Bracketing, Delay',
        32: 'Auto ISO',
        33: 'Auto ISO, Continuous',
        34: 'Auto ISO, Delay',
        40: 'Auto ISO, b3 ???',
        48: 'Auto ISO, Exposure Bracketing',
        128: 'IR Control',
        256: 'b8 ???',
        272: 'b8 ???, Exposure Bracketing'
    }),
    0x008A: ('AutoBracketRelease', ),
    0x008B: ('LensFStops', ),
    0x008C: ('NEFCurve1', ),  # ExifTool calls this 'ContrastCurve'
    0x008D: ('ColorMode', ),
    0x008F: ('SceneMode', ),
    0x0090: ('LightingType', ),
    0x0091: ('ShotInfo', ),  # First 4 bytes are a version number in ASCII
    0x0092: ('HueAdjustment', ),
    # ExifTool calls this 'NEFCompression', should be 1-4
    0x0093: ('Compression', {
        1: 'Lossy (type 1)',
        2: 'Uncompressed',
        3: 'Lossless',
        4: 'Lossy (type 2)',
        5: 'Striped packed 12 bits',
        6: 'Uncompressed (reduced to 12 bit)',
        7: 'Unpacked 12 bits',
        8: 'Small',
        9: 'Packed 12 bits',
        10: 'Packed 14 bits',
    }),
    0x0094: ('Saturation', {
        -3: 'B&W',
        -2: '-2',
        -1: '-1',
        0: '0',
        1: '1',
        2: '2',
    }),
    0x0095: ('NoiseReduction', ),
    0x0096: ('NEFCurve2', ),  # ExifTool calls this 'LinearizationTable'
    0x0097: ('ColorBalance', ),  # First 4 bytes are a version number in ASCII
    0x0098: ('LensData', ),  # First 4 bytes are a version number in ASCII
    0x0099: ('RawImageCenter', ),
    0x009A: ('SensorPixelSize', ),
    0x009C: ('Scene Assist', ),
    0x009D: ('DateStampMode', {
        0: 'Off',
        1: 'Date & Time',
        2: 'Date',
        3: 'Date Counter'
    }),
    0x009E: ('RetouchHistory', {
        0: 'None',
        3: 'B & W',
        4: 'Sepia',
        5: 'Trim',
        6: 'Small Picture',
        7: 'D-Lighting',
        8: 'Red Eye',
        9: 'Cyanotype',
        10: 'Sky Light',
        11: 'Warm Tone',
        12: 'Color Custom',
        13: 'Image Overlay',
        14: 'Red Intensifier',
        15: 'Green Intensifier',
        16: 'Blue Intensifier',
        17: 'Cross Screen',
        18: 'Quick Retouch',
        19: 'NEF Processing',
        23: 'Distortion Control',
        25: 'Fisheye',
        26: 'Straighten',
        29: 'Perspective Control',
        30: 'Color Outline',
        31: 'Soft Filter',
        32: 'Resize',
        33: 'Miniature Effect',
        34: 'Skin Softening',
        35: 'Selected Frame',
        37: 'Color Sketch',
        38: 'Selective Color',
        39: 'Glamour',
        40: 'Drawing',
        44: 'Pop',
        45: 'Toy Camera Effect 1',
        46: 'Toy Camera Effect 2',
        47: 'Cross Process (red)',
        48: 'Cross Process (blue)',
        49: 'Cross Process (green)',
        50: 'Cross Process (yellow)',
        51: 'Super Vivid',
        52: 'High-contrast Monochrome',
        53: 'High Key',
        54: 'Low Key'
    }),
    0x00A0: ('SerialNumber', ),
    0x00A2: ('ImageDataSize', ),
    # 00A3: unknown - a single byte 0
    # 00A4: In NEF, looks like a 4 byte ASCII version number ('0200')
    0x00A5: ('ImageCount', ),
    0x00A6: ('DeletedImageCount', ),
    0x00A7: ('TotalShutterReleases', ),
    # First 4 bytes are a version number in ASCII, with version specific
    # info to follow.  Its hard to treat it as a string due to embedded nulls.
    0x00A8: ('FlashInfo', ),
    0x00A9: ('ImageOptimization', ),
    0x00AA: ('Saturation', ),
    0x00AB: ('DigitalVariProgram', ),
    0x00AC: ('ImageStabilization', ),
    0x00AD: ('AFResponse', ),
    0x00B0: ('MultiExposure', ),
    0x00B1: ('HighISONoiseReduction', {
        0: 'Off',
        1: 'Minimal',
        2: 'Low',
        3: 'Medium Low',
        4: 'Normal',
        5: 'Medium High',
        6: 'High',
    }),
    0x00B3: ('ToningEffect', ),
    0x00B6: ('PowerUpTime', ),
    0x00B7: ('AFInfo2', ),  # FIXME: This is a list where each position has a different meaning
    0x00B8: ('FileInfo', ),
    0x00B9: ('AFTune', ),
    0x00BB: ('RetouchInfo', ),
    # 0x00BC: unknown
    0x00BD: ('PictureControlData', ),
    # 0x00BF: unknown
    # 0x00C0: unknown
    0x00C3: ('BarometerInfo', ),
    0x0100: ('DigitalICE', ),
    0x0103: ('PreviewCompression', {
        1: 'Uncompressed',
        2: 'CCITT 1D',
        3: 'T4/Group 3 Fax',
        4: 'T6/Group 4 Fax',
        5: 'LZW',
        6: 'JPEG (old-style)',
        7: 'JPEG',
        8: 'Adobe Deflate',
        9: 'JBIG B&W',
        10: 'JBIG Color',
        32766: 'Next',
        32769: 'Epson ERF Compressed',
        32771: 'CCIRLEW',
        32773: 'PackBits',
        32809: 'Thunderscan',
        32895: 'IT8CTPAD',
        32896: 'IT8LW',
        32897: 'IT8MP',
        32898: 'IT8BL',
        32908: 'PixarFilm',
        32909: 'PixarLog',
        32946: 'Deflate',
        32947: 'DCS',
        34661: 'JBIG',
        34676: 'SGILog',
        34677: 'SGILog24',
        34712: 'JPEG 2000',
        34713: 'Nikon NEF Compressed',
        65000: 'Kodak DCR Compressed',
        65535: 'Pentax PEF Compressed',
    }),
    0x0201: ('PreviewImageStart', ),
    0x0202: ('PreviewImageLength', ),
    0x0213: ('PreviewYCbCrPositioning', {
        1: 'Centered',
        2: 'Co-sited',
    }),
    0x0E00: ('PrintIM', ),
    0x0E01: ('InCameraEditNote', ),
    0x0E09: ('NikonCaptureVersion', ),
    0x0E0E: ('NikonCaptureOffsets', ),
    0x0E10: ('NikonScan', ),
    0x0E13: ('NikonCaptureEditVersions', ),
    0x0E1D: ('NikonICCProfile', ),
    0x0E1E: ('NikonCaptureOutput', ),
    0x0E22: ('NEFBitDepth', ),
}

TAGS_OLD = {
    0x0003: ('Quality', {
        1: 'VGA Basic',
        2: 'VGA Normal',
        3: 'VGA Fine',
        4: 'SXGA Basic',
        5: 'SXGA Normal',
        6: 'SXGA Fine',
    }),
    0x0004: ('ColorMode', {
        1: 'Color',
        2: 'Monochrome',
    }),
    0x0005: ('ImageAdjustment', {
        0: 'Normal',
        1: 'Bright+',
        2: 'Bright-',
        3: 'Contrast+',
        4: 'Contrast-',
    }),
    0x0006: ('CCDSpeed', {
        0: 'ISO 80',
        2: 'ISO 160',
        4: 'ISO 320',
        5: 'ISO 100',
    }),
    0x0007: ('WhiteBalance', {
        0: 'Auto',
        1: 'Preset',
        2: 'Daylight',
        3: 'Incandescent',
        4: 'Fluorescent',
        5: 'Cloudy',
        6: 'Speed Light',
    }),
}
