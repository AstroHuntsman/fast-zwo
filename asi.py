import ctypes
import enum
import warnings

import numpy as np

from astropy import units as u

class ASICamera:
    """ZWO ASI Camera class."""

    def __init__(self, library_path, camera_index=0):
        self._CDLL = ctypes.CDLL(library_path)

        n_cameras = self._CDLL.ASIGetNumOfConnectedCameras()
        if n_cameras < 1:
            msg = "No ASI cameras found!"
            warnings.warn(msg)
            raise RuntimeError(msg)

        self._camera_index = camera_index
        if n_cameras - self._camera_index < 1:
            mag = "Requested camera index {}, but only {} cameras found!".format(self._camera_index,
                                                                                 n_cameras)
            warnings.warn(msg)
            raise RuntimeError(msg)

        self._info = self.get_camera_property(self._camera_index)
        self._camera_ID = self.info['camera_ID']

        error_code = self._CDLL.ASIOpenCamera(self._camera_ID)
        if error_code != ErroCode.SUCCESS:
            msg = "Couldn't open camera: {}".format(ErrorCode(error_code).name)
            warnings.warn(msg)
            raise RuntimeError(msg)

        result = self._CDLL.ASIInitCamera(self._camera_ID)
        if error_code != ErroCode.SUCCESS:
            msg = "Couldn't init camera: {}".format(ErrorCode(error_code).name)
            warnings.warn(msg)
            raise RuntimeError(msg)

    def get_camera_property(self, camera_index):
        """ Get properties of the camera with given index """
        camera_info = CameraInfo()
        error_code = self._CDLL.ASIGetCameraProperty(ctypes.byref(camera_info), camera_index)
        if error_code != ErrorCode.SUCCESS:
            msg = "Error getting camera properties: {}".format(ErrorCode(error_code).name)
            warnings.warn(msg)
            raise RuntimeError(msg)

        pythonic_info = self._parse_info(camera_info)
        return pythonic_info

    def _call_function(self, function_name, camera_ID, *args):
        """ Utility function for calling the SDK functions that return ErrorCode """
        function = getattr(self._CDLL, function_name)
        error_code = function(ctypes.c_int(camera_ID), *args)
        if error_code != ErrorCode.SUCCESS:
            msg = "Error calling {}: {}".format(function_name, ErrorCode(error_code).name)
            warnings.warn(msg)
            raise RuntimeError(msg)

    def _parse_info(self, camera_info):
        """ Utility function to parse CameraInfo Structures into something more Pythonic """
        pythonic_info = {'name': camera_info.name.decode(),
                         'camera_ID': int(camera_info.camera_ID),
                         'max_height': camera_info.max_height * u.pixel,
                         'max_width': camera_info.max_width * u.pixel,
                         'is_color_camera': bool(camera_info.is_color_camera),
                         'bayer_pattern': BayerPattern(camera_info.bayer_pattern).name,
                         'supported_bins': self._parse_bins(camera_info.supported_bins),
                         'supported_video_format': self._parse_formats(
                             camera_info.supported_video_format),
                         'pixel_size': camera_info.pixel_size * u.um,
                         'has_mechanical_shutter': bool(camera_info.has_mechanical_shutter),
                         'has_ST4_port': bool(camera_info.has_ST4_port),
                         'has_cooler': bool(camera_info.has_cooler),
                         'is_USB3_host': bool(camera_info.is_USB3_host),
                         'is_USB3_camera': bool(camera_info.is_USB3_camera),
                         'e_per_adu': camera_info.e_per_adu * u.electron / u.adu,
                         'bit_depth': camera_info.bit_depth * u.bit,
                         'is_trigger_camera': bool(camera_info.is_trigger_camera)}
        return pythonic_info


ID_MAX = 128  # Maximum value for camera integer ID (camera_ID)


@enum.unique
class BayerPattern(enum.IntEnum):
    """ Bayer filter type """
    RG = 0
    BG = enum.auto()
    GR = enum.auto()
    GB = enum.auto()


@enum.unique
class ImgType(enum.IntEnum):
    """ Supported video format """
    RAW8 = 0
    RGB24 = enum.auto()
    RAW16 = enum.auto()
    Y8 = enum.auto()
    END = -1


@enum.unique
class GuideDirection(enum.IntEnum):
    """ Guider direction """
    NORTH = 0
    SOUTH = enum.auto()
    EAST = enum.auto()
    WEST = enum.auto()


@enum.unique
class FlipStatus(enum.IntEnum):
    """ Flip status """
    NONE = 0
    HORIZ = enum.auto()
    VERT = enum.auto()
    BOTH = enum.auto()


@enum.unique
class CameraMode(enum.IntEnum):
    """ Camera status """
    NORMAL = 0
    TRIG_SOFT_EDGE = enum.auto()
    TRIG_RISE_EDGE = enum.auto()
    TRIG_FALL_EDGE = enum.auto()
    TRIG_SOFT_LEVEL = enum.auto()
    TRIG_HIGH_LEVEL = enum.auto()
    TRIG_LOW_LEVEL = enum.auto()
    END = -1


@enum.unique
class TrigOutput(enum.IntEnum):
    """External trigger output."""

    PINA = 0  # Only Pin A output
    PINB = enum.auto()  # Only Pin B outoput
    NONE = -1


@enum.unique
class ErrorCode(enum.IntEnum):
    """ Error codes """
    SUCCESS = 0
    INVALID_INDEX = 1  # No camera connected or index value out of boundary
    INVALID_ID = 2
    INVALID_CONTROL_TYPE = 3
    CAMERA_CLOSED = 4  # Camera didn't open
    CAMERA_REMOVED = 5  # Failed to fine the camera, maybe it was removed
    INVALID_PATH = 6  # Cannot find the path of the file
    INVALID_FILEFORMAT = 7
    INVALID_SIZE = 8  # Wrong video format size
    INVALID_IMGTYPE = 9  # Unsupported image format
    OUTOF_BOUNDARY = 10  # The startpos is out of boundary
    TIMEOUT = 11
    INVALID_SEQUENCE = 12  # Stop capture first
    BUFFER_TOO_SMALL = 13
    VIDEO_MODE_ACTIVE = 14
    EXPOSURE_IN_PROGRESS = 15
    GENERAL_ERROR = 16  # General error, e.g. value is out of valid range
    INVALID_MODE = 17  # The current mode is wrong
    END = 18


class CameraInfo(ctypes.Structure):
    """ Camera info structure """
    _fields_ = [('name', ctypes.c_char * 64),
                ('camera_ID', ctypes.c_int),
                ('max_height', ctypes.c_long),
                ('max_width', ctypes.c_long),
                ('is_color_camera', ctypes.c_int),
                ('bayer_pattern', ctypes.c_int),
                ('supported_bins', ctypes.c_int * 16),  # e.g. (1,2,4,8,0,...) means 1x, 2x, 4x, 8x
                ('supported_video_format', ctypes.c_int * 8),  # ImgTypes, terminates with END
                ('pixel_size', ctypes.c_double),  # in microns
                ('has_mechanical_shutter', ctypes.c_int),
                ('has_ST4_port', ctypes.c_int),
                ('has_cooler', ctypes.c_int),
                ('is_USB3_host', ctypes.c_int),
                ('is_USB3_camera', ctypes.c_int),
                ('e_per_adu', ctypes.c_float),
                ('bit_depth', ctypes.c_int),
                ('is_trigger_camera', ctypes.c_int),
                ('unused', ctypes.c_char * 16)]
class ControlType(enum.IntEnum):
    """ Control types """
    GAIN = 0
    EXPOSURE = enum.auto()
    GAMMA = enum.auto()
    WB_R = enum.auto()
    WB_B = enum.auto()
    OFFSET = enum.auto()
    BANDWIDTHOVERLOAD = enum.auto()
    OVERCLOCK = enum.auto()
    TEMPERATURE = enum.auto()  # Returns temperature*10
    FLIP = enum.auto()
    AUTO_MAX_GAIN = enum.auto()
    AUTO_MAX_EXP = enum.auto()  # in microseconds
    AUTO_TARGET_BRIGHTNESS = enum.auto()
    HARDWARE_BIN = enum.auto()
    HIGH_SPEED_MODE = enum.auto()
    COOLER_POWER_PERC = enum.auto()
    TARGET_TEMP = enum.auto()  # NOT *10
    COOLER_ON = enum.auto()
    MONO_BIN = enum.auto()  # Leads to less grid at software bin mode for colour camera
    FAN_ON = enum.auto()
    PATTERN_ADJUST = enum.auto()
    ANTI_DEW_HEATER = enum.auto()

    BRIGHTNESS = OFFSET
    AUTO_MAX_BRIGHTNESS = AUTO_TARGET_BRIGHTNESS


class ControlCaps(ctypes.Structure):
    """ Structure for caps (limits) on allowable parameter values for each camera control """
    _fields_ = [('name', ctypes.c_char * 64),  # The name of the control, .e.g. Exposure, Gain
                ('description', ctypes.c_char * 128),  # Description of the command
                ('max_value', ctypes.c_long),
                ('min_value', ctypes.c_long),
                ('default_value', ctypes.c_long),
                ('is_auto_supported', ctypes.c_int),
                ('is_writable', ctypes.c_int),  # Some can be read only, e.g. temperature
                ('control_type', ctypes.c_int),  # ControlType used to get/set value
                ('unused', ctypes.c_char * 32)]


class ExposureStatus(enum.IntEnum):
    """ Exposure status codes """
    IDLE = 0
    WORKING = enum.auto()
    SUCCESS = enum.auto()
    FAILED = enum.auto()


class ID(ctypes.Structure):
    _fields_ = [('id', ctypes.c_ubyte * 8)]


class SupportedMode(ctypes.Structure):
    """ Array of supported CameraModes, terminated with CameraMode.END """
    _fields_ = [('modes', ctypes.c_int * 16)]
