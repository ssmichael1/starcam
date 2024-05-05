"""
Python wrapping for C api for SVBony cameras

This module provides a python wrapping for the C API for SVBony cameras.  The C API is provided
by the manufacturer and is used to control the camera.  This module provides a pythonic interface

the C API is available at:
https://www.svbony.com/support-software-driver/


Note: SVBony libraries must be in same directory as this file or a separate
directory specified by the environment variable "SVBONY_LIBDIR"

Author: Steven Michael (ssmichael@gmail.com)

License: MIT
"""

import ctypes
import pathlib
import numpy as np
from os import getenv
from enum import Enum


# Get the base directory
__libdir = getenv("SVBONY_LIBDIR", str(pathlib.Path(__file__).parent))


__cusb = ctypes.CDLL(__libdir + "/libusb-1.0.0.dylib")
__clib = ctypes.CDLL(__libdir + "/libSVBCameraSDK.dylib")
__clib.SVBGetSDKVersion.restype = ctypes.c_char_p
__clib.SVBGetVideoData.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), 
                                 ctypes.c_long, ctypes.c_int]

class SVB_ERROR_CODE(Enum):
    SVB_SUCCESS = 0
    SVB_ERROR_INVALID_INDEX = 1
    SVB_ERROR_INVALID_ID = 2
    SVB_ERROR_INVALID_CONTROL_TYPE = 3
    SVB_ERROR_CAMERA_CLOSED = 4 
    SVB_ERROR_CAMERA_REMOVED = 5
    SVB_ERROR_INVALID_PATH = 6
    SVB_ERROR_INVALID_FILEFORMAT = 7
    SVB_ERROR_INVALID_SIZE = 8
    SVB_ERROR_INVALID_IMGTYPE = 9 
    SVB_ERROR_OUTOF_BOUNDARY = 10
    SVB_ERROR_TIMEOUT = 11
    SVB_ERROR_INVALID_SEQUENCE = 12
    SVB_ERROR_BUFFER_TOO_SMALL = 13
    SVB_ERROR_VIDEO_MODE_ACTIVE = 14
    SVB_ERROR_EXPOSURE_IN_PROGRESS = 15
    SVB_ERROR_GENERAL_ERROR = 16
    SVB_ERROR_INVALID_MODE = 17
    SVB_ERROR_INVALID_DIRECTION = 18
    SVB_ERROR_UNKNOW_SENSOR_TYPE = 19
    SVB_ERROR_END = 20

class SVB_BOOL(Enum):
    SVB_FALSE = 0
    SVB_TRUE = 1

class SVB_BAYER_PATTERN(Enum):
    SVB_BAYER_RG=0
    SVB_BAYER_BG=1
    SVB_BAYER_GR=2
    SVB_BAYER_GB=3

class SVB_GUIDE_DIRECTION(Enum):
    SVB_GUIDE_NORTH=0
    SVB_GUIDE_SOUTH=1
    SVB_GUIDE_EAST=2
    SVB_GUIDE_WEST=3

class SVB_FLIP_STATUS(Enum):
    SVB_FLIP_NONE=0
    SVB_FLIP_HORIZ=1
    SVB_FLIP_VERT=2

class SVB_CAMERA_MODE(Enum):
    SVB_MODE_NORMAL=0
    SVB_MODE_TRIG_SOFT=1
    SVB_MODE_TRIG_RISE_EDGE=2
    SVB_MODE_TRIG_FALL_EDGE=3
    SVB_MODE_TRIG_DOUBLE_EDGE=4
    SVB_MODE_TRIG_HIGH_LEVEL=5
    SVB_MODE_TRIG_LOW_LEVEL=6
    SVB_MODE_END=-1

class SVB_TRIG_OUTPUT(Enum):
    SVB_TRIG_OUTPUT_PINA=0
    SVB_TRIG_OUTPUT_PINB=1
    SVB_TRIG_OUTPUT_NONE=-1

class SVB_IMG_TYPE(Enum):
    SVB_IMG_RAW8=0
    SVB_IMG_RAW10=1
    SVB_IMG_RAW12=2
    SVB_IMG_RAW14=3
    SVB_IMG_RAW16=4
    SVB_IMG_Y8=5
    SVB_IMG_Y10=6
    SVB_IMG_Y12=7
    SVB_IMG_Y14=8
    SVB_IMG_Y16=9
    SVB_IMG_RGB24=10
    SVB_IMG_RGB32=11
    SVB_IMG_END=-1

class SVB_CONTROL_TYPE(Enum):
    SVB_GAIN=0
    SVB_EXPOSURE=1
    SVB_GAMMA=2
    SVB_GAMMA_CONTRAST=3
    SVB_WB_R=4
    SVB_WB_G=5
    SVB_WB_B=6
    SVB_FLIP=7
    SVB_FRAME_SPEED_MODE=8
    SVB_CONTRAST=9
    SVB_SHARPNESS=10
    SVB_SATURATION=11
    SVB_AUTO_TARGET_BRIGHTNESS=12
    SVB_BLACK_LEVEL=13
    SVB_COOLER_ENABLE=14
    SVB_TARGET_TEMPERATURE=15
    SVB_CURRENT_TEMPERATURE=16
    SVB_COOLER_POWER=17
    SVB_BAD_PIXEL_CORRECTION_ENABLE=18
    SVB_BAD_PIXEL_CORRECTION_THRESHOLD=19

class __SVBControlCaps(ctypes.Structure):
    _fields_ = [("Name", ctypes.c_char * 64),
               ("Description", ctypes.c_char * 128),
               ("MaxValue", ctypes.c_long),
               ("MinValue", ctypes.c_long),
               ("DefaultValue", ctypes.c_long),
               ("IsAutoSupported", ctypes.c_int),
               ("IsWritable", ctypes.c_int),
               ("ControlType", ctypes.c_int),
               ("Unused", ctypes.c_char*32)]

class __SVBCameraInfo(ctypes.Structure):
    _fields_ = [("FriendlyName", ctypes.c_char * 32),
                ("CameraSN", ctypes.c_char * 32),
                ("PortType", ctypes.c_char * 32),
                ("DeviceID", ctypes.c_uint32),
                ("CameraID", ctypes.c_int32)]

class __SVBCameraProperty(ctypes.Structure):
    _fields_ = [("MaxHeight", ctypes.c_long),
                ("MaxWidth", ctypes.c_long),
                ("IsColorCam", ctypes.c_int),
                ("BayerPattern", ctypes.c_int),
                ("SupportedBins", ctypes.c_int * 16),
                ("SupportedVideoFormat", ctypes.c_int * 8),
                ("MaxBitDepth", ctypes.c_int),
                ("IsTriggerCam", ctypes.c_int)]


class __SVB_ID(ctypes.Structure):
    _fields_ = [("id", ctypes.c_char * 64)]

class __SVB_SUPPORTED_MODE(ctypes.Structure):
    _fields_ = [("mode", ctypes.c_char * 16)]

def SVBGetNumOfConnectedCameras():
    """Get number of connected cameras
    
    Get number of connected SVBony cameras
    """
    return __clib.SVBGetNumOfConnectedCameras()

def SVBGetCameraInfo(index):
    
    """Get camera information
    
    Get information of the connected camera, by index.  Can be done without opening the camera

    Args:
        index (int): Index of the camera

    Returns:
        dict: Dictionary of camera information with the following fields:
            - FriendlyName (str): Friendly name of the camera
            - CameraSN (str): Camera serial number
            - PortType (str): Port type (USB, etc)
            - DeviceID (int): Device ID
            - CameraID (int): Camera ID to be used when opening & in other functions

    Raises:
        Exception: If error occurs
    
    """

    info = __SVBCameraInfo()
    errcode = __clib.SVBGetCameraInfo(ctypes.byref(info), index)

    if errcode != 0:
        raise Exception(f"Error code: {SVB_ERROR_CODE(errcode).name}")
    return {
        "FriendlyName": info.FriendlyName.decode("utf-8"),
        "CameraSN": info.CameraSN.decode("utf-8"),
        "PortType": info.PortType.decode("utf-8"),
        "DeviceID": info.DeviceID,
        "CameraID": info.CameraID
    }

def SVBOpenCamera(id):
    """Open a camera
    
    Open a camera.  All APIs except SVBGetCameraInfo require camera to be open first

    Args:
        id (int): Camera ID, returned in SVBGetCameraInfo function

    Returns:
        None

    Raises:
        Exception: If error occurs
    """

    errcode = __clib.SVBOpenCamera(id)
    if errcode != 0:
        raise Exception(f"Error code: {SVB_ERROR_CODE(errcode).name}")
    
def SVBCloseCamera(id) -> None:
    """Close a camera
    
    Close a camera and free resources

    Args:
        id (int): Camera ID

    Returns:
        None

    Raises:
        Exception: If error occurs

    """
    errcode = __clib.SVBCloseCamera(id)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBGetNumOfControls(id: int) -> int:
    """Get number of camera controls

    Get number of camera controls.  Camera needs to be opened first.

    Args:
        id (int): Camera ID

    Returns:
        int: Number of controls

    Raises:
        Exception: If error occurs
    """
    nctrl = ctypes.c_int(0)
    errcode = __clib.SVBGetNumOfControls(id, ctypes.byref(nctrl))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return nctrl.value

def SVBGetCameraProperty(id: int) -> dict:
    """Get properties of given camera
    
    Get properties of given camera.  Camera must be opened first.

    Args:
        id (int): Camera ID

    Returns:
        dict: Dictionary of camera properties with the following fields:
        - MaxHeight (int): Maximum height of the camera in pixels
        - MaxWidth (int): Maximum width of the camera in pixels
        - IsColorCam (bool): True if color camera
        - BayerPattern (SVB_BAYER_PATTERN): Bayer pattern details
        - SupportedBins (list[int]): List of supported binning factors
        - SupportedVideoFormat (list[SBG_IMG_TYPE]): List of supported video formats
        - MaxBitDepth (int): Maximum bit depth
        - IsTriggerCam (bool): True if triggered camera

    Raises:
        Exception: If error occurs

    """
    prop = __SVBCameraProperty()
    errcode = __clib.SVBGetCameraProperty(id, ctypes.byref(prop))

    if errcode != 0:
        raise Exception(f"Error code: {SVB_ERROR_CODE(errcode).name}")
    
    rawformats = [SVB_IMG_TYPE(prop.SupportedVideoFormat[i]) for i in range(8)]
    formats = []
    for f in rawformats:
        if f != SVB_IMG_TYPE.SVB_IMG_END:
            formats.append(f)
        else:
            break
    
    rawbins = [prop.SupportedBins[i] for i in range(16)]
    bins = []
    for b in rawbins:
        if b != 0:
            bins.append(b)
        else:
            break
    

    return {
        "MaxHeight": prop.MaxHeight,
        "MaxWidth": prop.MaxWidth,
        "IsColorCam": True if prop.IsColorCam == 1 else False,
        "BayerPattern": SVB_BAYER_PATTERN(prop.BayerPattern),
        "SupportedBins": bins,
        "SupportedVideoFormat": formats,
        "MaxBitDepth": prop.MaxBitDepth,
        "IsTriggerCam": prop.IsTriggerCam
    }

def SVBGetControlCaps(id: int, ctrl_idx: int) -> list:
    """Get control capabilities description at given index

    Get control capabilities description at given index.  Camera must be opened first.
    Index must be less than the number of control properties returned by SVBGetNumOfControls

    Args:
        id (int): Camera ID
        ctrl_idx (int): Control index

    Returns:
        dict: Dictionary of control capabilities with the following fields:
        - Name (str): Name of the control
        - Description (str): Description of the control
        - MaxValue (int): Maximum value
        - MinValue (int): Minimum value
        - DefaultValue (int): Default value
        - IsAutoSupported (bool): True if auto is supported
        - IsWritable (bool): True if writable
        - ControlType (SVB_CONTROL_TYPE): Control type Enum

    Raises:
        Exception: If error occurs
    
    """
    caps = __SVBControlCaps()
    errcode = __clib.SVBGetControlCaps(id, ctrl_idx, ctypes.byref(caps))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

    return {
        "Name": caps.Name.decode("utf-8"),
        "Description": caps.Description.decode("utf-8"),
        "MaxValue": caps.MaxValue,
        "MinValue": caps.MinValue,
        "DefaultValue": caps.DefaultValue,
        "IsAutoSupported": True if caps.IsAutoSupported == 1 else False,
        "IsWritable": True if caps.IsWritable == 1 else False,
        "ControlType": SVB_CONTROL_TYPE(caps.ControlType)
    }

def SVBGetControlValue(id: int, ctrl: SVB_CONTROL_TYPE) -> tuple[int, bool]:
    """Get controls property value and auto value
    
    Note:
        - The value of the temperature is in unites of 10ths of a degree Celsius

    Args:
        id (int): Camera ID
        ctrl (SVB_CONTROL_TYPE): Control type

    Returns:
        tuple: Tuple of value and auto value.  Value is the control value, auto is True if auto mode is enabled

    Raises:
        Exception: If error occurs
    """
    value = ctypes.c_long(0)
    auto = ctypes.c_int(0)
    errcode = __clib.SVBGetControlValue(id, ctrl.value, ctypes.byref(value), ctypes.byref(auto))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return (value.value, True if auto == 1 else False)

def SVBSetControlValue(id: int, ctrl: SVB_CONTROL_TYPE, value: int, auto: bool) -> None:
    """Set control value
    
    Set the control value and control auto.  Camera must be opened first.

    Note: For FRAME_SPEED_MODE:
        - 0 = Low Speed
        - 1 = Normal
        - 2 = High Speed

    Args:
        id (int): Camera ID
        ctrl (SVB_CONTROL_TYPE): Control type
        value (int): Control value
        auto (bool): True if auto mode is enabled

    Returns:
        None

    Raises:
        Exception: If error occurs

    """
    errcode = __clib.SVBSetControlValue(id, ctrl.value, value, 1 if auto else 0)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBGetOutputImageType(id: int) -> SVB_IMG_TYPE:
    """Get output image type

    Get the current output image type, or format.

    Args:
        id (int): Camera ID
    
    Returns:
        SVB_IMG_TYPE: Image type

    Raises:
        Exception: If error occurs

    """
    imgtype = ctypes.c_int(0)
    errcode = __clib.SVBGetOutputImageType(id, ctypes.byref(imgtype))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return SVB_IMG_TYPE(imgtype.value)

def SVBSetOutputImageType(id: int, imgtype: SVB_IMG_TYPE) -> None:
    """Set output image type
    
    Set the outout image type, or format.  Value must be type supported by the 
    SVBGetCameraProperty function

    Args:
        id (int): Camera ID
        imgtype (SVB_IMG_TYPE): Image type

    Returns:
        None

    Raises:
        Exception: If error occurs

    """
    errcode = __clib.SVBSetOutputImageType(id, imgtype.value)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))



def SVBSetROIFormat(id: int, iStartX: int, iStartY: int, iWidth: int, iHeight: int, iBin: int) -> None:
    """Set camera ROI

    Set the camera region of interest (ROI) before capture
    You must stop capture befor calling
    Width and height is value after binning

    Args:
        id (int): Camera ID
        iStartX (int): X coordinate of the top-left corner of the ROI
        iStartY (int): Y coordinate of the top-left corner of the ROI
        iWidth (int): Width of the ROI
        iHeight (int): Height of the ROI
        iBin (int): Binning factor

    Returns:
        None

    Raises:
        Exception: If error occurs

    """
    errcode = __clib.SVBSetROIFormat(id, iStartX, iStartY, iWidth, iHeight, iBin)
    if errcode != 0:
        raise Exception(f"Error code: {SVB_ERROR_CODE(errcode).name}")



def SVBSetROIFormatEx(id: int, iStartX: int, iStartY: int,
                      iWdith: int, iHeight: int, iBin: int, iMode: int) -> None:
    """Set camera ROI with mode
    
    Set the camera region of interest (ROI) before capture
    You must stop capture before calling
    Width and height is value after binning

    Args:
        id (int): Camera ID
        iStartX (int): X coordinate of the top-left corner of the ROI
        iStartY (int): Y coordinate of the top-left corner of the ROI
        iWidth (int): Width of the ROI
        iHeight (int): Height of the ROI
        iBin (int): Binning method.  1 or 2.
        iMode (int): Binning Mode.  0 = average, 1 = sum

    Returns:
        None

    Raises:
        Exception: If error occurs

    """

    errcode = __clib.SVBSetROIFormatEx(id, iStartX, iStartY, iWdith, iHeight, iBin, iMode)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))


def SVBGetROIFormat(id: int) -> dict:
    """Get the current ROI format

    Get the current ROI format

    Args:
        id (int): Camera ID

    Returns:
        dict: Dictionary of ROI format with the following fields:
        - startX (int): X coordinate of the top-left corner of the ROI
        - startY (int): Y coordinate of the top-left corner of the ROI
        - width (int): Width of the ROI
        - height (int): Height of the ROI
        - bin (int): Binning factor

    Raises:
        Exception: If error occurs

    """
    iStartX = ctypes.c_int(0)
    iStartY = ctypes.c_int(0)
    iWidth = ctypes.c_int(0)
    iHeight = ctypes.c_int(0)
    iBin = ctypes.c_int(0)
    errcode = __clib.SVBGetROIFormat(id, ctypes.byref(iStartX),
                                   ctypes.byref(iStartY), ctypes.byref(iWidth),
                                   ctypes.byref(iHeight), ctypes.byref(iBin))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return {"startX": iStartX.value, 
            "startY": iStartY.value,
            "width": iWidth.value,
            "height": iHeight.value,
            "bin": iBin.value}

def SVBGetROIFormatEx(id: int) -> dict:
    """Get the current ROI format with mode
    
    Get the current ROI format with mode
    
    Args:
        id (int): Camera ID
        
    Returns:
        dict: Dictionary of ROI format with the following fields:
        - startX (int): X coordinate of the top-left corner of the ROI
        - startY (int): Y coordinate of the top-left corner of the ROI
        - width (int): Width of the ROI
        - height (int): Height of the ROI
        - bin (int): Binning factor
        - mode (int): Binning mode
    
    Raises:
        Exception: If error occurs
    """
    iStartX = ctypes.c_int(0)
    iStartY = ctypes.c_int(0)
    iWidth = ctypes.c_int(0)
    iHeight = ctypes.c_int(0)
    iBin = ctypes.c_int(0)
    iMode = ctypes.c_int(0)
    errcode = __clib.SVBGetROIFormatEx(id, ctypes.byref(iStartX),
                                     ctypes.byref(iStartY), ctypes.byref(iWidth),
                                     ctypes.byref(iHeight), ctypes.byref(iBin),
                                     ctypes.byref(iMode))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return {"startX": iStartX.value, 
            "startY": iStartY.value,
            "width": iWidth.value,
            "height": iHeight.value,
            "bin": iBin.value,
            "mode": iMode.value}

def SVBGetDroppedFrames(id: int) -> int:
    """Get dropped frames
    
    Dropped frames happen when USB bandwidth is not enough to transfer all frames or harddisk write
    speed is slow

    It will reset to 0 after stop capture

    Args:
        id (int): Camera ID

    Returns:
        int: Number of dropped frames

    Raises:
        Exception: If error occurs
    """
    iDroppedFrames = ctypes.c_int(0)
    errcode = __clib.SVBGetDroppedFrames(id, ctypes.byref(iDroppedFrames))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return iDroppedFrames.value

def SVBStartVideoCapture(id: int) -> None:
    """Start video capture
    
    Start video capture

    Args:
        id (int): Camera ID

    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBStartVideoCapture(id)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBStopVideoCapture(id: int) -> None:
    """Stop video capture
    
    Stop video capture

    Args:
        id (int): Camera ID

    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBStopVideoCapture(id)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBGetVideoData(id: int, width: int, height: int, bytes_per_pixel: int, waitMS: int=-1) -> np.ndarray:
    """Capture a video frame to memory
    
    Capture a video frame to memory.  The camera on-board buffer is small so this needs
    to be called as fast as possible, otherwise frames will be discarded.

    Need to make sure buffer size is big enough to hold a single image, otherwise this API will crash

    Args:
        id (int): Camera ID
        width (int): Width of the image in pixels
        height (int): Height of the image in pixels
        bytes_per_pixel (int): Bytes per pixel
        waitMS (int): Timeout in milliseconds.  -1 means wait forever

    Returns:
        frame: numpy array with frame data

    Raises:
        Exception: If error occurs
    
    """

    #imgtype = ctypes.POINTER(ctypes.c_ubyte)
    nbytes = bytes_per_pixel * width * height
    imgtype = ctypes.c_ubyte * nbytes
    raw = bytearray(nbytes)
    buf = imgtype.from_buffer(raw)
    imgsize = ctypes.c_long(nbytes)
    cwaitms = ctypes.c_int(waitMS)

    errcode = (
        __clib.SVBGetVideoData(id, 
                             ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)),
                             imgsize, cwaitms)
    )
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    if bytes_per_pixel == 1:
        return np.frombuffer(buf, dtype=np.uint8).reshape((height, width))
    elif bytes_per_pixel == 2:
        return np.frombuffer(buf, dtype=np.uint16).reshape((height, width))
    elif bytes_per_pixel == 3:
        return np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 3))
    elif bytes_per_pixel == 4:
        return np.frombuffer(buf, dtype=np.uint32).reshape((height, width))
    else:
        raise Exception("Invalid bytes per pixel")

def SVBWhiteBalanceOnce(id: int) -> None:
    """White balance once
    
    White balance once.  This will adjust the white balance once.  
    Args:
        id (int): Camera ID

    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBWhiteBalanceOnce(id)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBGetCameraFirmwareVersion(id: int) -> str:
    """Get camera firmware version
    
    Get camera firmware version

    Args:
        id (int): Camera ID

    Returns:
        str: Firmware version

    Raises:
        Exception: If error occurs
    """
    fwversion = ctypes.c_char_p(b" " * 256)
    errcode = __clib.SVBGetCameraFirmwareVersion(id, fwversion)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return fwversion.value.decode("utf-8")

def SVBGetSDKVersion() -> str:
    """Get SDK version
    
    Get SDK version

    Returns:
        str: SDK version

    """
    sdkversion = __clib.SVBGetSDKVersion()
    return sdkversion.decode("utf-8")

def SVBGetCameraMode(id: int) -> SVB_CAMERA_MODE:
    """Get Camera Trigger Mode
    
    Get camera trigger mode.  Only needs to call when IsTriggerCam is True
    
    Args:
        id (int): Camera ID
    
    Returns:
        SVB_CAMERA_MODE: Camera mode

    Raises:
        Exception: If error occurs
    """
    mode = ctypes.c_int(0)
    errcode = __clib.SVBGetCameraMode(id, ctypes.byref(mode))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return SVB_CAMERA_MODE(mode.value)

def SVBSetCameraMode(id: int, mode: SVB_CAMERA_MODE) -> None:
    """Set Camera Trigger Mode
    
    Set camera trigger mode.  Only needs to call when IsTriggerCam is True

    Args:
        id (int): Camera ID
        mode (SVB_CAMERA_MODE): Camera mode

    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBSetCameraMode(id, mode.value)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    
def SVBSetTriggerOutputIOConf(id: int, pin: SVB_TRIG_OUTPUT,
                               active_high: bool, delay: int, duration: int) -> None:
    """Configure output pin of trigger port
    
    Configure the output pin (A or B) of trigger port.  If duration <=0, this output
    pin will be closed.

    Args:
        id (int): Camera ID
        pin (SVB_TRIG_OUTPUT): Trigger output pin
        active_high (bool): True if active high
        delay (int): Delay in microseconds
        duration (int): Duration in microseconds

    Returns:
        None
    
    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBSetTriggerOutputIOConf(id, pin.value, 1 if active_high else 0, delay, duration)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBGetTriggerOutputIOConf(id: int, pin) -> tuple[bool, int, int]:
    """Get trigger output IO configuration

    Get trigger output IO configuration for the input pin

    Args:
        id (int): Camera ID
        pin (SVB_TRIG_OUTPUT): Trigger output pin

    Returns:
        tuple: Tuple of active high, delay, duration
    """
    active_high = ctypes.c_int(0)
    delay = ctypes.c_long(0)
    duration = ctypes.c_long(0)
    errcode = __clib.SVBGetTriggerOutputIOConf(id, pin.value, ctypes.byref(active_high),
                                            ctypes.byref(delay), ctypes.byref(duration))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return (True if active_high == 1 else False, delay.value, duration.value)


def SVBPulseGuide(id: int, direction: SVB_GUIDE_DIRECTION, duration: int) -> None:
    """Pulse guide
    
    Pulse guide.  This will send a pulse guide command to the camera.  The camera must be in pulse guide mode

    Args:
        id (int): Camera ID
        direction (SVB_GUIDE_DIRECTION): Guide direction
        duration (int): Duration of the pulse guide in milliseconds

    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBPulseGuide(id, direction.value, duration)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBSetAutoSaveParam(id: int, enable: bool) -> None:
    """Set auto save parameter
    
    Set auto save parameter.  If true, then save the paramter file automatically

    Args:
        id (int): Camera ID
        enable (bool): Set auto save of parameter file

    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBSetAutoSaveParam(id, 1 if enable else 0)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))



def SVBGetCameraSupportMode(id: int) -> str:
    """Get the camera supported mode.

    Get the camera supported mode.  Only need to call when "IsTriggerCam" in
    the CameraInfo is set to True.

    Args:
        id (int): Camera ID

    Returns:
        mode (str): Supported mode

    Raises:
        Exception: If error occurs
    """
    mode = __SVB_SUPPORTED_MODE()
    errcode = __clib.SVBGetCameraSupportMode(id, ctypes.byref(mode))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return mode.mode.decode("utf-8")

def SVBSendSoftTrigger(id: int) -> None:
    """Send software trigger
    
    Send software trigger.  Only needs to call when IsTriggerCam is True

    Args:
        id (int): Camera ID

    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBSendSoftTrigger(id)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))

def SVBGetSerialNumber(id: int) -> str:
    """Get camera serial number
    
    Get camera serial number

    Args:
        id (int): Camera ID

    Returns:
        str: Camera serial number

    Raises:
        Exception: If error occurs
    """
    sn = __SVB_ID()
    errcode = __clib.SVBGetSerialNumber(id, ctypes.byref(sn))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return sn.id.decode("utf-8")

def SVBGetSensorPixelSize(id: int) -> float:
    """Get sensor pixel size
    
    Get sensor pixel size in microns

    Args:
        id (int): Camera ID

    Returns:
        float: Sensor pixel size in microns

    Raises:
        Exception: If error occurs
    """
    pixel_size = ctypes.c_float(0)
    errcode = __clib.SVBGetSensorPixelSize(id, ctypes.byref(pixel_size))
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return pixel_size.value

def SVBIsCameraNeedToUpgrade(id: int) -> tuple[bool, str]:
    """Check if camera needs to be upgraded

    Check if camera needs to be upgraded.  I have no idea how camera will know this, but it is 
    part of the provided API.

    Args:
        id (int): Camera ID

    Returns:
        tuple: Tuple of need_upgrade and upgrade version

    Raises:
        Exception: If error occurs
    """
    need_upgrade = ctypes.c_int(0)
    upgrade_version = ctypes.c_char_p(b" " * 256)
    errcode = __clib.SVBIsCameraNeedToUpgrade(id, ctypes.byref(need_upgrade), upgrade_version)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))
    return (True if need_upgrade == 1 else False, upgrade_version.value.decode("utf-8"))


def SVBRestoreDefaultParam(id: int) -> None:
    """Restore default parameters
    
    Restore default parameters

    Args:
        id (int): Camera ID
    
    Returns:
        None

    Raises:
        Exception: If error occurs
    """
    errcode = __clib.SVBRestoreDefaultParam(id)
    if errcode != 0:
        raise Exception(SVB_ERROR_CODE(errcode))


if __name__=="__main__":
    import pprint

    print("This is the main program")    
    print(f"SDK Version: {SVBGetSDKVersion()}")
    print(f"Number of connected cameras: {SVBGetNumOfConnectedCameras()}")
    info = SVBGetCameraInfo(0)
    pprint.pprint(info)
    id = info['CameraID']
    SVBOpenCamera(id)
    pprint.pp(SVBGetCameraProperty(id))
    nctrl = SVBGetNumOfControls(id)
    print(f'Image Type = {SVBGetOutputImageType(id)}')
    SVBSetOutputImageType(id, SVB_IMG_TYPE.SVB_IMG_Y16)
    print(f'Image Type = {SVBGetOutputImageType(id)}')
    print(f'Pixel Size = {SVBGetSensorPixelSize(id):.2f} µm')
    print(f'Supported Mode = {SVBGetCameraSupportMode(id)}')
    print(f'Upgrade Needed: {SVBIsCameraNeedToUpgrade(id)}')
    for idx in range(nctrl):
        print(f"Control {idx}")
        pprint.pp(SVBGetControlCaps(id, idx))
    try:
        print(f'mode = {SVBGetCameraMode(id)}')
        pprint.pp(SVBGetROIFormat(id))
        SVBStartVideoCapture(id)
        arr = SVBGetVideoData(id, 1920, 1080, 2, 500)
        SVBStopVideoCapture(id)
        
        print(f'min = {arr.min()} : max = {arr.max()} : mean = {arr.mean()} : std = {arr.std()}')    
        idx = np.argwhere(arr % 1 > 1e-6).flatten()
        print(arr.shape)
    except Exception as e:
        print(e)
    SVBCloseCamera(id)

# %%
