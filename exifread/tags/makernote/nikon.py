"""
Makernote (proprietary) tag definitions for Nikon.
"""
from typing import Dict, Tuple

from exifread.tags.str_utils import make_string
from exifread.utils import Ratio


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
        return ""
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
    i = seq[0]
    # Causes headaches for the +/- logic, so special case it.
    if i == 0:
        return "0 EV"
    if i > 127:
        i = 256 - i
        ret_str = "-"
    else:
        ret_str = "+"
    step = seq[2]  # Assume third value means the step size
    whole = i / step
    i = i % step
    if whole != 0:
        ret_str = "%s%s " % (ret_str, str(whole))
    if i == 0:
        ret_str += "EV"
    else:
        ratio = Ratio(i, step)
        ret_str = ret_str + str(ratio) + " EV"
    return ret_str


# Nikon E99x MakerNote Tags
TAGS_NEW: Dict[int, Tuple] = {
    0x0001: ("MakernoteVersion", make_string),  # Sometimes binary
    0x0002: ("ISOSetting",),
    0x0003: ("ColorMode",),
    0x0004: ("Quality",),
    0x0005: ("Whitebalance",),
    0x0006: ("ImageSharpening",),
    0x0007: ("FocusMode",),
    0x0008: ("FlashSetting",),
    0x0009: ("AutoFlashMode",),
    0x000B: ("WhiteBalanceBias",),
    0x000C: ("WhiteBalanceRBCoeff",),
    0x000D: ("ProgramShift", ev_bias),
    # Nearly the same as the other EV vals, but step size is 1/12 EV (?)
    0x000E: ("ExposureDifference", ev_bias),
    0x000F: ("ISOSelection",),
    0x0010: ("DataDump",),
    0x0011: ("NikonPreview",),
    0x0012: ("FlashCompensation", ev_bias),
    0x0013: ("ISOSpeedRequested",),
    0x0016: ("PhotoCornerCoordinates",),
    0x0017: ("ExternalFlashExposureComp", ev_bias),
    0x0018: ("FlashBracketCompensationApplied", ev_bias),
    0x0019: ("AEBracketCompensationApplied",),
    0x001A: ("ImageProcessing",),
    0x001B: (
        "CropHiSpeed",
        # need to investigate, returns incoherent results
        #          {
        #     0: "Off",
        #     1: "1.3x Crop",
        #     2: "DX Crop",
        #     3: "5:4 Crop",
        #     4: "3:2 Crop",
        #     6: "16:9 Crop",
        #     8: "2.7x Crop",
        #     9: "DX Movie Crop",
        #     10: "1.3x Movie Crop",
        #     11: "FX Uncropped",
        #     12: "DX Uncropped",
        #     13: "2.8x Movie Crop",
        #     14: "1.4x Movie Crop",
        #     15: "1.5x Movie Crop",
        #     17: "1:1 Crop",
        # }
    ),
    0x001C: ("ExposureTuning",),
    0x001D: ("SerialNumber",),  # Conflict with 0x00A0 ?
    0x001E: (
        "ColorSpace",
        {
            1: "sRGB",
            2: "Adobe RGB",
            4: "BT.2100",
        },
    ),
    0x001F: ("VRInfo",),
    0x0020: ("ImageAuthentication",),
    0x0021: ("FaceDetect",),
    0x0022: (
        "ActiveDLighting",
        {
            0: "Off",
            1: "Low",
            3: "Normal",
            5: "High",
            7: "Extra High",
            8: "Extra High 1",
            9: "Extra High 2",
            10: "Extra High 3",
            11: "Extra High 4",
            65535: "Auto",
        },
    ),
    0x0023: ("PictureControl",),
    0x0024: ("WorldTime",),
    0x0025: ("ISOInfo",),
    0x002A: ("VignetteControl",),
    0x002B: ("DistortInfo",),
    0x002C: ("UnknownInfo",),
    0x0034: (
        "ShutterMode",
        {
            0: "Mechanical",
            16: "Electronic",
            48: "Electronic Front Curtain",
            64: "Electronic (Movie)",
            80: "Auto (Mechanical)",
            81: "Auto (Electronic Front Curtain)",
            96: "Electronic (High Speed)",
        },
    ),
    0x0037: ("MechanicalShutterCount",),
    0x0039: ("LocationInfo",),
    0x003D: ("BlackLevel",),
    0x003E: ("ImageSizeRAW",),
    0x0080: ("ImageAdjustment",),
    0x0081: ("ToneCompensation",),
    0x0082: ("AuxiliaryLens",),
    0x0083: ("LensType",),
    0x0084: ("LensMinMaxFocalMaxAperture",),
    0x0085: ("ManualFocusDistance",),
    0x0086: ("DigitalZoomFactor",),
    0x0087: (
        "FlashMode",
        {
            0x00: "Did Not Fire",
            0x01: "Fired, Manual",
            0x03: "Not Ready",
            0x07: "Fired, External",
            0x08: "Fired, Commander Mode ",
            0x09: "Fired, TTL Mode",
            0x18: "LED Light",
        },
    ),
    0x0088: (
        "AFFocusPosition",
        {
            0x0000: "Center",
            0x0100: "Top",
            0x0200: "Bottom",
            0x0300: "Left",
            0x0400: "Right",
        },
    ),
    0x0089: (
        "BracketingMode",
        {
            0x00: "Single frame, no bracketing",
            0x01: "Continuous, no bracketing",
            0x02: "Timer, no bracketing",
            0x10: "Single frame, exposure bracketing",
            0x11: "Continuous, exposure bracketing",
            0x12: "Timer, exposure bracketing",
            0x40: "Single frame, white balance bracketing",
            0x41: "Continuous, white balance bracketing",
            0x42: "Timer, white balance bracketing",
        },
    ),
    0x008A: ("AutoBracketRelease",),
    0x008B: ("LensFStops",),
    0x008C: ("NEFCurve1",),  # ExifTool calls this 'ContrastCurve'
    0x008D: ("ColorMode",),
    0x008F: ("SceneMode",),
    0x0090: ("LightingType",),
    0x0091: ("ShotInfo",),  # First 4 bytes are a version number in ASCII
    0x0092: ("HueAdjustment",),
    0x0093: (
        "NEFCompression",
        {
            1: "Lossy (type 1)",
            2: "Uncompressed",
            3: "Lossless",
            4: "Lossy (type 2)",
            5: "Striped packed 12 bits",
            6: "Uncompressed (reduced to 12 bit)",
            7: "Unpacked 12 bits",
            8: "Small",
            9: "Packed 12 bits",
            10: "Packed 14 bits",
            13: "High Efficiency",
            14: "High Efficiency*",
        },
    ),
    0x0094: (
        "Saturation",
        {
            -3: "B&W",
            -2: "-2",
            -1: "-1",
            0: "0",
            1: "1",
            2: "2",
        },
    ),
    0x0095: ("NoiseReduction",),
    0x0096: ("NEFCurve2",),  # ExifTool calls this 'LinearizationTable'
    0x0097: ("ColorBalance",),  # First 4 bytes are a version number in ASCII
    0x0098: ("LensData",),  # First 4 bytes are a version number in ASCII
    0x0099: ("RawImageCenter",),
    0x009A: ("SensorPixelSize",),
    0x009C: ("Scene Assist",),
    0x009E: ("RetouchHistory",),
    0x00A0: ("SerialNumber",),
    0x00A2: ("ImageDataSize",),
    # 00A3: unknown - a single byte 0
    # 00A4: In NEF, looks like a 4 byte ASCII version number ('0200')
    0x00A5: ("ImageCount",),
    0x00A6: ("DeletedImageCount",),
    0x00A7: ("TotalShutterReleases",),
    # First 4 bytes are a version number in ASCII, with version specific
    # info to follow.  It's hard to treat it as a string due to embedded nulls.
    0x00A8: ("FlashInfo",),
    0x00A9: ("ImageOptimization",),
    0x00AA: ("Saturation",),
    0x00AB: ("DigitalVariProgram",),
    0x00AC: ("ImageStabilization",),
    0x00AD: ("AFResponse",),
    0x00B0: ("MultiExposure",),
    0x00B1: ("HighISONoiseReduction",),
    0x00B6: ("PowerUpTime",),
    0x00B7: ("AFInfo2",),
    0x00B8: ("FileInfo",),
    0x00B9: ("AFTune",),
    0x00BB: ("RetouchInfo",),
    0x00BD: ("PictureControlData",),
    0x00BF: ("SilentPhotography", {0: "Off", 1: "On"}),
    0x0100: ("DigitalICE",),
    0x0201: ("PreviewImageStart",),
    0x0202: ("PreviewImageLength",),
    0x0213: (
        "PreviewYCbCrPositioning",
        {
            1: "Centered",
            2: "Co-sited",
        },
    ),
    0x0E09: ("NikonCaptureVersion",),
    0x0E0E: ("NikonCaptureOffsets",),
    0x0E10: ("NikonScan",),
    0x0E22: ("NEFBitDepth",),
}

TAGS_OLD: Dict[int, Tuple] = {
    0x0003: (
        "Quality",
        {
            1: "VGA Basic",
            2: "VGA Normal",
            3: "VGA Fine",
            4: "SXGA Basic",
            5: "SXGA Normal",
            6: "SXGA Fine",
        },
    ),
    0x0004: (
        "ColorMode",
        {
            1: "Color",
            2: "Monochrome",
        },
    ),
    0x0005: (
        "ImageAdjustment",
        {
            0: "Normal",
            1: "Bright+",
            2: "Bright-",
            3: "Contrast+",
            4: "Contrast-",
        },
    ),
    0x0006: (
        "CCDSpeed",
        {
            0: "ISO 80",
            2: "ISO 160",
            4: "ISO 320",
            5: "ISO 100",
        },
    ),
    0x0007: (
        "WhiteBalance",
        {
            0: "Auto",
            1: "Preset",
            2: "Daylight",
            3: "Incandescent",
            4: "Fluorescent",
            5: "Cloudy",
            6: "Speed Light",
        },
    ),
}
