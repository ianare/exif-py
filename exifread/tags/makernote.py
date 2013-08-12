
from .utils import make_string, make_string_uc
from exifread.classes import Ratio

def nikon_ev_bias(seq):
    """
    First digit seems to be in steps of 1/6 EV.
    Does the third value mean the step size?  It is usually 6,
    but it is 12 for the ExposureDifference.
    Check for an error condition that could cause a crash.
    This only happens if something has gone really wrong in
    reading the Nikon MakerNote.
    http://tomtia.plala.jp/DigitalCamera/MakerNote/index.asp
    """
    if len( seq ) < 4 :
        return ''
    if seq == [252, 1, 6, 0]:
        return "-2/3 EV"
    if seq == [253, 1, 6, 0]:
        return "-1/2 EV"
    if seq == [254, 1, 6, 0]:
        return "-1/3 EV"
    if seq == [0, 1, 6, 0]:
        return "0 EV"
    if seq == [2, 1, 6, 0]:
        return "+1/3 EV"
    if seq == [3, 1, 6, 0]:
        return "+1/2 EV"
    if seq == [4, 1, 6, 0]:
        return "+2/3 EV"
    # Handle combinations not in the table.
    a = seq[0]
    # Causes headaches for the +/- logic, so special case it.
    if a == 0:
        return "0 EV"
    if a > 127:
        a = 256 - a
        ret_str = "-"
    else:
        ret_str = "+"
    b = seq[2]  # Assume third value means the step size
    whole = a / b
    a = a % b
    if whole != 0:
        ret_str = ret_str + str(whole) + " "
    if a == 0:
        ret_str = ret_str + "EV"
    else:
        r = Ratio(a, b)
        ret_str = ret_str + r.__repr__() + " EV"
    return ret_str

# Nikon E99x MakerNote Tags
NIKON_NEW = {
    0x0001: ('MakernoteVersion', make_string),  # Sometimes binary
    0x0002: ('ISOSetting', make_string),
    0x0003: ('ColorMode', ),
    0x0004: ('Quality', ),
    0x0005: ('Whitebalance', ),
    0x0006: ('ImageSharpening', ),
    0x0007: ('FocusMode', ),
    0x0008: ('FlashSetting', ),
    0x0009: ('AutoFlashMode', ),
    0x000B: ('WhiteBalanceBias', ),
    0x000C: ('WhiteBalanceRBCoeff', ),
    0x000D: ('ProgramShift', nikon_ev_bias),
    # Nearly the same as the other EV vals, but step size is 1/12 EV (?)
    0x000E: ('ExposureDifference', nikon_ev_bias),
    0x000F: ('ISOSelection', ),
    0x0010: ('DataDump', ),
    0x0011: ('NikonPreview', ),
    0x0012: ('FlashCompensation', nikon_ev_bias),
    0x0013: ('ISOSpeedRequested', ),
    0x0016: ('PhotoCornerCoordinates', ),
    # 0x0017: Unknown, but most likely an EV value
    0x0018: ('FlashBracketCompensationApplied', nikon_ev_bias),
    0x0019: ('AEBracketCompensationApplied', ),
    0x001A: ('ImageProcessing', ),
    0x001B: ('CropHiSpeed', ),
    0x001D: ('SerialNumber', ), # Conflict with 0x00A0 ?
    0x001E: ('ColorSpace', ),
    0x001F: ('VRInfo', ),
    0x0020: ('ImageAuthentication', ),
    0x0022: ('ActiveDLighting', ),
    0x0023: ('PictureControl', ),
    0x0024: ('WorldTime', ),
    0x0025: ('ISOInfo', ),
    0x0080: ('ImageAdjustment', ),
    0x0081: ('ToneCompensation', ),
    0x0082: ('AuxiliaryLens', ),
    0x0083: ('LensType', ),
    0x0084: ('LensMinMaxFocalMaxAperture', ),
    0x0085: ('ManualFocusDistance', ),
    0x0086: ('DigitalZoomFactor', ),
    0x0087: ('FlashMode',
             {0x00: 'Did Not Fire',
              0x01: 'Fired, Manual',
              0x07: 'Fired, External',
              0x08: 'Fired, Commander Mode ',
              0x09: 'Fired, TTL Mode'}),
    0x0088: ('AFFocusPosition',
             {0x0000: 'Center',
              0x0100: 'Top',
              0x0200: 'Bottom',
              0x0300: 'Left',
              0x0400: 'Right'}),
    0x0089: ('BracketingMode',
             {0x00: 'Single frame, no bracketing',
              0x01: 'Continuous, no bracketing',
              0x02: 'Timer, no bracketing',
              0x10: 'Single frame, exposure bracketing',
              0x11: 'Continuous, exposure bracketing',
              0x12: 'Timer, exposure bracketing',
              0x40: 'Single frame, white balance bracketing',
              0x41: 'Continuous, white balance bracketing',
              0x42: 'Timer, white balance bracketing'}),
    0x008A: ('AutoBracketRelease', ),
    0x008B: ('LensFStops', ),
    0x008C: ('NEFCurve1', ),  # ExifTool calls this 'ContrastCurve'
    0x008D: ('ColorMode', ),
    0x008F: ('SceneMode', ),
    0x0090: ('LightingType', ),
    0x0091: ('ShotInfo', ), # First 4 bytes are a version number in ASCII
    0x0092: ('HueAdjustment', ),
    # ExifTool calls this 'NEFCompression', should be 1-4
    0x0093: ('Compression', ),
    0x0094: ('Saturation',
             {-3: 'B&W',
              -2: '-2',
              -1: '-1',
              0: '0',
              1: '1',
              2: '2'}),
    0x0095: ('NoiseReduction', ),
    0x0096: ('NEFCurve2', ),  # ExifTool calls this 'LinearizationTable'
    0x0097: ('ColorBalance', ), # First 4 bytes are a version number in ASCII
    0x0098: ('LensData', ), # First 4 bytes are a version number in ASCII
    0x0099: ('RawImageCenter', ),
    0x009A: ('SensorPixelSize', ),
    0x009C: ('Scene Assist', ),
    0x009E: ('RetouchHistory', ),
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
    0x00AD: ('Responsive AF', ),  # 'AFResponse'
    0x00B0: ('MultiExposure', ),
    0x00B1: ('HighISONoiseReduction', ),
    0x00B7: ('AFInfo', ),
    0x00B8: ('FileInfo', ),
    # 00B9: unknown
    0x0100: ('DigitalICE', ),
    0x0103: ('PreviewCompression',
             {1: 'Uncompressed',
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
              65535: 'Pentax PEF Compressed',}),
    0x0201: ('PreviewImageStart', ),
    0x0202: ('PreviewImageLength', ),
    0x0213: ('PreviewYCbCrPositioning',
             {1: 'Centered',
              2: 'Co-sited'}),
    0x0E09: ('NikonCaptureVersion', ),
    0x0E0E: ('NikonCaptureOffsets', ),
    0x0E10: ('NikonScan', ),
    0x0E22: ('NEFBitDepth', ),
}

NIKON_OLD = {
    0x0003: ('Quality',
             {1: 'VGA Basic',
              2: 'VGA Normal',
              3: 'VGA Fine',
              4: 'SXGA Basic',
              5: 'SXGA Normal',
              6: 'SXGA Fine'}),
    0x0004: ('ColorMode',
             {1: 'Color',
              2: 'Monochrome'}),
    0x0005: ('ImageAdjustment',
             {0: 'Normal',
              1: 'Bright+',
              2: 'Bright-',
              3: 'Contrast+',
              4: 'Contrast-'}),
    0x0006: ('CCDSpeed',
             {0: 'ISO 80',
              2: 'ISO 160',
              4: 'ISO 320',
              5: 'ISO 100'}),
    0x0007: ('WhiteBalance',
             {0: 'Auto',
              1: 'Preset',
              2: 'Daylight',
              3: 'Incandescent',
              4: 'Fluorescent',
              5: 'Cloudy',
              6: 'Speed Light'}),
}

def olympus_special_mode(v):
    """decode Olympus SpecialMode tag in MakerNote"""
    mode1 = {
        0: 'Normal',
        1: 'Unknown',
        2: 'Fast',
        3: 'Panorama'}
    mode2 = {
        0: 'Non-panoramic',
        1: 'Left to right',
        2: 'Right to left',
        3: 'Bottom to top',
        4: 'Top to bottom'}
    if v[0] not in mode1 or v[2] not in mode2:
        return v
    return '%s - sequence %d - %s' % (mode1[v[0]], v[1], mode2[v[2]])

OLYMPUS = {
    # ah HAH! those sneeeeeaky bastids! this is how they get past the fact
    # that a JPEG thumbnail is not allowed in an uncompressed TIFF file
    0x0100: ('JPEGThumbnail', ),
    0x0200: ('SpecialMode', olympus_special_mode),
    0x0201: ('JPEGQual',
             {1: 'SQ',
              2: 'HQ',
              3: 'SHQ'}),
    0x0202: ('Macro',
             {0: 'Normal',
             1: 'Macro',
             2: 'SuperMacro'}),
    0x0203: ('BWMode',
             {0: 'Off',
             1: 'On'}),
    0x0204: ('DigitalZoom', ),
    0x0205: ('FocalPlaneDiagonal', ),
    0x0206: ('LensDistortionParams', ),
    0x0207: ('SoftwareRelease', ),
    0x0208: ('PictureInfo', ),
    0x0209: ('CameraID', make_string), # print as string
    0x0F00: ('DataDump', ),
    0x0300: ('PreCaptureFrames', ),
    0x0404: ('SerialNumber', ),
    0x1000: ('ShutterSpeedValue', ),
    0x1001: ('ISOValue', ),
    0x1002: ('ApertureValue', ),
    0x1003: ('BrightnessValue', ),
    0x1004: ('FlashMode', ),
    0x1004: ('FlashMode',
       {2: 'On',
        3: 'Off'}),
    0x1005: ('FlashDevice',
       {0: 'None',
        1: 'Internal',
        4: 'External',
        5: 'Internal + External'}),
    0x1006: ('ExposureCompensation', ),
    0x1007: ('SensorTemperature', ),
    0x1008: ('LensTemperature', ),
    0x100b: ('FocusMode',
       {0: 'Auto',
        1: 'Manual'}),
    0x1017: ('RedBalance', ),
    0x1018: ('BlueBalance', ),
    0x101a: ('SerialNumber', ),
    0x1023: ('FlashExposureComp', ),
    0x1026: ('ExternalFlashBounce',
       {0: 'No',
        1: 'Yes'}),
    0x1027: ('ExternalFlashZoom', ),
    0x1028: ('ExternalFlashMode', ),
    0x1029: ('Contrast  int16u',
       {0: 'High',
        1: 'Normal',
        2: 'Low'}),
    0x102a: ('SharpnessFactor', ),
    0x102b: ('ColorControl', ),
    0x102c: ('ValidBits', ),
    0x102d: ('CoringFilter', ),
    0x102e: ('OlympusImageWidth', ),
    0x102f: ('OlympusImageHeight', ),
    0x1034: ('CompressionRatio', ),
    0x1035: ('PreviewImageValid',
       {0: 'No',
        1: 'Yes'}),
    0x1036: ('PreviewImageStart', ),
    0x1037: ('PreviewImageLength', ),
    0x1039: ('CCDScanMode',
       {0: 'Interlaced',
        1: 'Progressive'}),
    0x103a: ('NoiseReduction',
       {0: 'Off',
        1: 'On'}),
    0x103b: ('InfinityLensStep', ),
    0x103c: ('NearLensStep', ),

    # TODO - these need extra definitions
    # http://search.cpan.org/src/EXIFTOOL/Image-ExifTool-6.90/html/TagNames/Olympus.html
    0x2010: ('Equipment', ),
    0x2020: ('CameraSettings', ),
    0x2030: ('RawDevelopment', ),
    0x2040: ('ImageProcessing', ),
    0x2050: ('FocusInfo', ),
    0x3000: ('RawInfo ', ),
}

# 0x2020 CameraSettings
OLYMPUS_TAG_0x2020 = {
    0x0100: ('PreviewImageValid',
             {0: 'No',
              1: 'Yes'}),
    0x0101: ('PreviewImageStart', ),
    0x0102: ('PreviewImageLength', ),
    0x0200: ('ExposureMode',
             {1: 'Manual',
              2: 'Program',
              3: 'Aperture-priority AE',
              4: 'Shutter speed priority AE',
              5: 'Program-shift'}),
    0x0201: ('AELock',
             {0: 'Off',
              1: 'On'}),
    0x0202: ('MeteringMode',
             {2: 'Center Weighted',
              3: 'Spot',
              5: 'ESP',
              261: 'Pattern+AF',
              515: 'Spot+Highlight control',
              1027: 'Spot+Shadow control'}),
    0x0300: ('MacroMode',
             {0: 'Off',
              1: 'On'}),
    0x0301: ('FocusMode',
             {0: 'Single AF',
              1: 'Sequential shooting AF',
              2: 'Continuous AF',
              3: 'Multi AF',
              10: 'MF'}),
    0x0302: ('FocusProcess',
             {0: 'AF Not Used',
              1: 'AF Used'}),
    0x0303: ('AFSearch',
             {0: 'Not Ready',
              1: 'Ready'}),
    0x0304: ('AFAreas', ),
    0x0401: ('FlashExposureCompensation', ),
    0x0500: ('WhiteBalance2',
             {0: 'Auto',
             16: '7500K (Fine Weather with Shade)',
             17: '6000K (Cloudy)',
             18: '5300K (Fine Weather)',
             20: '3000K (Tungsten light)',
             21: '3600K (Tungsten light-like)',
             33: '6600K (Daylight fluorescent)',
             34: '4500K (Neutral white fluorescent)',
             35: '4000K (Cool white fluorescent)',
             48: '3600K (Tungsten light-like)',
             256: 'Custom WB 1',
             257: 'Custom WB 2',
             258: 'Custom WB 3',
             259: 'Custom WB 4',
             512: 'Custom WB 5400K',
             513: 'Custom WB 2900K',
             514: 'Custom WB 8000K', }),
    0x0501: ('WhiteBalanceTemperature', ),
    0x0502: ('WhiteBalanceBracket', ),
    0x0503: ('CustomSaturation', ), # (3 numbers: 1. CS Value, 2. Min, 3. Max)
    0x0504: ('ModifiedSaturation',
             {0: 'Off',
              1: 'CM1 (Red Enhance)',
              2: 'CM2 (Green Enhance)',
              3: 'CM3 (Blue Enhance)',
              4: 'CM4 (Skin Tones)'}),
    0x0505: ('ContrastSetting', ), # (3 numbers: 1. Contrast, 2. Min, 3. Max)
    0x0506: ('SharpnessSetting', ), # (3 numbers: 1. Sharpness, 2. Min, 3. Max)
    0x0507: ('ColorSpace',
             {0: 'sRGB',
              1: 'Adobe RGB',
              2: 'Pro Photo RGB'}),
    0x0509: ('SceneMode',
             {0: 'Standard',
              6: 'Auto',
              7: 'Sport',
              8: 'Portrait',
              9: 'Landscape+Portrait',
             10: 'Landscape',
             11: 'Night scene',
             13: 'Panorama',
             16: 'Landscape+Portrait',
             17: 'Night+Portrait',
             19: 'Fireworks',
             20: 'Sunset',
             22: 'Macro',
             25: 'Documents',
             26: 'Museum',
             28: 'Beach&Snow',
             30: 'Candle',
             35: 'Underwater Wide1',
             36: 'Underwater Macro',
             39: 'High Key',
             40: 'Digital Image Stabilization',
             44: 'Underwater Wide2',
             45: 'Low Key',
             46: 'Children',
             48: 'Nature Macro'}),
    0x050a: ('NoiseReduction',
             {0: 'Off',
              1: 'Noise Reduction',
              2: 'Noise Filter',
              3: 'Noise Reduction + Noise Filter',
              4: 'Noise Filter (ISO Boost)',
              5: 'Noise Reduction + Noise Filter (ISO Boost)'}),
    0x050b: ('DistortionCorrection',
             {0: 'Off',
              1: 'On'}),
    0x050c: ('ShadingCompensation',
             {0: 'Off',
              1: 'On'}),
    0x050d: ('CompressionFactor', ),
    0x050f: ('Gradation',
             {'-1 -1 1': 'Low Key',
              '0 -1 1': 'Normal',
              '1 -1 1': 'High Key'}),
    0x0520: ('PictureMode',
             {1: 'Vivid',
              2: 'Natural',
              3: 'Muted',
              256: 'Monotone',
              512: 'Sepia'}),
    0x0521: ('PictureModeSaturation', ),
    0x0522: ('PictureModeHue?', ),
    0x0523: ('PictureModeContrast', ),
    0x0524: ('PictureModeSharpness', ),
    0x0525: ('PictureModeBWFilter',
             {0: 'n/a',
              1: 'Neutral',
              2: 'Yellow',
              3: 'Orange',
              4: 'Red',
              5: 'Green'}),
    0x0526: ('PictureModeTone',
             {0: 'n/a',
              1: 'Neutral',
              2: 'Sepia',
              3: 'Blue',
              4: 'Purple',
              5: 'Green'}),
    0x0600: ('Sequence', ), # 2 or 3 numbers: 1. Mode, 2. Shot number, 3. Mode bits
    0x0601: ('PanoramaMode', ), # (2 numbers: 1. Mode, 2. Shot number)
    0x0603: ('ImageQuality2',
             {1: 'SQ',
              2: 'HQ',
              3: 'SHQ',
              4: 'RAW'}),
    0x0901: ('ManometerReading', ),
}

CASIO = {
    0x0001: ('RecordingMode',
             {1: 'Single Shutter',
              2: 'Panorama',
              3: 'Night Scene',
              4: 'Portrait',
              5: 'Landscape'}),
    0x0002: ('Quality',
             {1: 'Economy',
              2: 'Normal',
              3: 'Fine'}),
    0x0003: ('FocusingMode',
             {2: 'Macro',
              3: 'Auto Focus',
              4: 'Manual Focus',
              5: 'Infinity'}),
    0x0004: ('FlashMode',
             {1: 'Auto',
              2: 'On',
              3: 'Off',
              4: 'Red Eye Reduction'}),
    0x0005: ('FlashIntensity',
             {11: 'Weak',
              13: 'Normal',
              15: 'Strong'}),
    0x0006: ('Object Distance', ),
    0x0007: ('WhiteBalance',
             {1: 'Auto',
              2: 'Tungsten',
              3: 'Daylight',
              4: 'Fluorescent',
              5: 'Shade',
              129: 'Manual'}),
    0x000B: ('Sharpness',
             {0: 'Normal',
              1: 'Soft',
              2: 'Hard'}),
    0x000C: ('Contrast',
             {0: 'Normal',
              1: 'Low',
              2: 'High'}),
    0x000D: ('Saturation',
             {0: 'Normal',
              1: 'Low',
              2: 'High'}),
    0x0014: ('CCDSpeed',
             {64: 'Normal',
              80: 'Normal',
              100: 'High',
              125: '+1.0',
              244: '+3.0',
              250: '+2.0'}),
}

FUJIFILM = {
    0x0000: ('NoteVersion', make_string),
    0x1000: ('Quality', ),
    0x1001: ('Sharpness',
             {1: 'Soft',
              2: 'Soft',
              3: 'Normal',
              4: 'Hard',
              5: 'Hard'}),
    0x1002: ('WhiteBalance',
             {0: 'Auto',
              256: 'Daylight',
              512: 'Cloudy',
              768: 'DaylightColor-Fluorescent',
              769: 'DaywhiteColor-Fluorescent',
              770: 'White-Fluorescent',
              1024: 'Incandescent',
              3840: 'Custom'}),
    0x1003: ('Color',
             {0: 'Normal',
              256: 'High',
              512: 'Low'}),
    0x1004: ('Tone',
             {0: 'Normal',
              256: 'High',
              512: 'Low'}),
    0x1010: ('FlashMode',
             {0: 'Auto',
              1: 'On',
              2: 'Off',
              3: 'Red Eye Reduction'}),
    0x1011: ('FlashStrength', ),
    0x1020: ('Macro',
             {0: 'Off',
              1: 'On'}),
    0x1021: ('FocusMode',
             {0: 'Auto',
              1: 'Manual'}),
    0x1030: ('SlowSync',
             {0: 'Off',
              1: 'On'}),
    0x1031: ('PictureMode',
             {0: 'Auto',
              1: 'Portrait',
              2: 'Landscape',
              4: 'Sports',
              5: 'Night',
              6: 'Program AE',
              256: 'Aperture Priority AE',
              512: 'Shutter Priority AE',
              768: 'Manual Exposure'}),
    0x1100: ('MotorOrBracket',
             {0: 'Off',
              1: 'On'}),
    0x1300: ('BlurWarning',
             {0: 'Off',
              1: 'On'}),
    0x1301: ('FocusWarning',
             {0: 'Off',
              1: 'On'}),
    0x1302: ('AEWarning',
             {0: 'Off',
              1: 'On'}),
}

CANON = {
    0x0006: ('ImageType', ),
    0x0007: ('FirmwareVersion', ),
    0x0008: ('ImageNumber', ),
    0x0009: ('OwnerName', ),
    0x0015: ('SerialNumberFormat', {
        0x90000000: 'Format 1',
        0xA0000000: 'Format 2'
    }),
    0x001A: ('SuperMacro', {
        0: 'Off',
        1: 'On (1)',
        2: 'On (2)'
    }),
    0x0009: ('OwnerName', ),
    0x0009: ('OwnerName', ),
    0x0009: ('OwnerName', ),
    0x0009: ('OwnerName', ),

    0x0095: ('LensModel', ),
    0x0096: ('InternalSerialNumber ', ),
    0x0097: ('DustRemovalData ', ),
    0x0098: ('CropInfo ', ),
    0x009A: ('AspectInfo', ),
    0x00b4: ('ColorSpace', {
        1: 'sRGB',
        2: 'Adobe RGB'
    }),
}

# this is in element offset, name, optional value dictionary format
CANON_CAMERA_SETTINGS = {
    1: ('Macromode', {
        1: 'Macro',
        2: 'Normal'
    }),
    2: ('SelfTimer', ),
    3: ('Quality', {
        1: 'Economy',
        2: 'Normal',
        3: 'Fine',
        5: 'Superfine'
    }),
    4: ('FlashMode', {
        0: 'Flash Not Fired',
        1: 'Auto',
        2: 'On',
        3: 'Red-Eye Reduction',
        4: 'Slow Synchro',
        5: 'Auto + Red-Eye Reduction',
        6: 'On + Red-Eye Reduction',
        16: 'external flash'
    }),
    5: ('ContinuousDriveMode', {
        0: 'Single Or Timer',
        1: 'Continuous',
        2: 'Movie',
    }),
    7: ('FocusMode', {
        0: 'One-Shot',
        1: 'AI Servo',
        2: 'AI Focus',
        3: 'MF',
        4: 'Single',
        5: 'Continuous',
        6: 'MF'
    }),
    9: ('RecordMode', {
        1: 'JPEG',
        2: 'CRW+THM',
        3: 'AVI+THM',
        4: 'TIF',
        5: 'TIF+JPEG',
        6: 'CR2',
        7: 'CR2+JPEG',
        9: 'Video'
    }),
    10: ('ImageSize', {
        0: 'Large',
        1: 'Medium',
        2: 'Small'
    }),
    11: ('EasyShootingMode', {
        0: 'Full Auto',
        1: 'Manual',
        2: 'Landscape',
        3: 'Fast Shutter',
        4: 'Slow Shutter',
        5: 'Night',
        6: 'B&W',
        7: 'Sepia',
        8: 'Portrait',
        9: 'Sports',
        10: 'Macro/Close-Up',
        11: 'Pan Focus'
    }),
    12: ('DigitalZoom', {
        0: 'None',
        1: '2x',
        2: '4x',
        3: 'Other'
    }),
    13: ('Contrast', {
        0xFFFF: 'Low',
        0: 'Normal',
        1: 'High'
    }),
    14: ('Saturation', {
        0xFFFF: 'Low',
        0: 'Normal',
        1: 'High'
    }),
    15: ('Sharpness', {
        0xFFFF: 'Low',
        0: 'Normal',
        1: 'High'
    }),
    16: ('ISO', {
        0: 'See ISOSpeedRatings Tag',
        15: 'Auto',
        16: '50',
        17: '100',
        18: '200',
        19: '400'
    }),
    17: ('MeteringMode', {
        0: 'Default',
        1: 'Spot',
        2: 'Average',
        3: 'Evaluative',
        4: 'Partial',
        5: 'Center-weighted'
    }),
    18: ('FocusType', {
        0: 'Manual',
        1: 'Auto',
        3: 'Close-Up (Macro)',
        8: 'Locked (Pan Mode)'
    }),
    19: ('AFPointSelected', {
        0x3000: 'None (MF)',
        0x3001: 'Auto-Selected',
        0x3002: 'Right',
        0x3003: 'Center',
        0x3004: 'Left'
    }),
    20: ('ExposureMode', {
        0: 'Easy Shooting',
        1: 'Program',
        2: 'Tv-priority',
        3: 'Av-priority',
        4: 'Manual',
        5: 'A-DEP'
    }),
    22: ('LensType', ),
    23: ('LongFocalLengthOfLensInFocalUnits', ),
    24: ('ShortFocalLengthOfLensInFocalUnits', ),
    25: ('FocalUnitsPerMM', ),
    28: ('FlashActivity', {
        0: 'Did Not Fire',
        1: 'Fired'
    }),
    29: ('FlashDetails', {
        0: 'Manual',
        1: 'TTL',
        2: 'A-TTL',
        3: 'E-TTL',
        4: 'FP Sync Enabled',
        7: '2nd("Rear")-Curtain Sync Used',
        11: 'FP Sync Used',
        13: 'Internal Flash',
        14: 'External E-TTL'
    }),
    32: ('FocusMode', {
        0: 'Single',
        1: 'Continuous',
        8: 'Manual'
    }),
    41: ('ManualFlashOutput', {
        0x0: 'n/a',
        0x500: 'Full',
        0x502: 'Medium',
        0x504: 'Low',
        0x7FFF: 'n/a'
    }),
}

CANON_FOCAL_LENGTH = {
    1: ('FocalType', {
        1: 'Fixed',
        2: 'Zoom',
    }),
    2: ('FocalLength', ),
}

CANON_SHOT_INFO = {
    7: ('WhiteBalance', {
        0: 'Auto',
        1: 'Sunny',
        2: 'Cloudy',
        3: 'Tungsten',
        4: 'Fluorescent',
        5: 'Flash',
        6: 'Custom'
    }),
    8: ('SlowShutter', {
        -1: 'n/a',
        0: 'Off',
        1: 'Night Scene',
        2: 'On',
        3: 'None'
    }),
    9: ('SequenceNumber', ),
    14: ('AFPointUsed', ),
    15: ('FlashBias', {
        0xFFC0: '-2 EV',
        0xFFCC: '-1.67 EV',
        0xFFD0: '-1.50 EV',
        0xFFD4: '-1.33 EV',
        0xFFE0: '-1 EV',
        0xFFEC: '-0.67 EV',
        0xFFF0: '-0.50 EV',
        0xFFF4: '-0.33 EV',
        0x0000: '0 EV',
        0x000C: '0.33 EV',
        0x0010: '0.50 EV',
        0x0014: '0.67 EV',
        0x0020: '1 EV',
        0x002C: '1.33 EV',
        0x0030: '1.50 EV',
        0x0034: '1.67 EV',
        0x0040: '2 EV'
    }),
    19: ('SubjectDistance', ),
}

CANON_AF_INFO_2 = {
     2: ('AFAreaMode', {
        0: 'Off (Manual Focus)',
        2: 'Single-point AF',
        4: 'Multi-point AF or AI AF',
        5: 'Face Detect AF',
        6: 'Face + Tracking',
        7: 'Zone AF',
        8: 'AF Point Expansion',
        9: 'Spot AF',
        11: 'Flexizone Multi',
        13: 'Flexizone Single',
    }),
    3: ('NumAFPoints', ),
    4: ('ValidAFPoints', ),
    5: ('CanonImageWidth', ),
}
