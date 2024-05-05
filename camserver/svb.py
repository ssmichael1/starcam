# %%
from svb_sdk import *
from threading import Thread
import datetime as dt
import types

def bits_per_pixel(t: SVB_IMG_TYPE):
    """Return number of bits per pixel for given image type
    
    Args:
        t (SVB_IMG_TYPE): Image type

    Returns:
        int: Number of bits per pixel
    """
    match t:
        case SVB_IMG_TYPE.SVB_IMG_RAW8:
            return 8
        case SVB_IMG_TYPE.SVB_IMG_RAW10:
            return 10
        case SVB_IMG_TYPE.SVB_IMG_RAW12:
            return 12
        case SVB_IMG_TYPE.SVB_IMG_RAW14:
            return 14
        case SVB_IMG_TYPE.SVB_IMG_RAW16:
            return 16
        case SVB_IMG_TYPE.SVB_IMG_Y8:
            return 8
        case SVB_IMG_TYPE.SVB_IMG_Y10:
            return 10
        case SVB_IMG_TYPE.SVB_IMG_Y12:
            return 12
        case SVB_IMG_TYPE.SVB_IMG_Y14:
            return 14
        case SVB_IMG_TYPE.SVB_IMG_Y16:
            return 16
        case SVB_IMG_TYPE.SVB_IMG_RGB24:
            return 24
        case SVB_IMG_TYPE.SVB_IMG_RGB32:
            return 32
        case _:
            raise Exception("Invalid image type") 

def bytes_per_pixel(t: SVB_IMG_TYPE):
    """Return number of bytes per pixel for given image type
    
    Args:
        t (SVB_IMG_TYPE): Image type

    Returns:
        int: Number of bytes per pixel
    """
    return (bits_per_pixel(t) + 7) // 8


def svb_get_connected_cameras():
    """Return a list of all connected SVB cameras, with details
    
    Args:
        None

    Returns:
        list: A list of dictionaries, each containing details about an available camera.

    """
    cameras = []
    for idx in range(SVBGetNumOfConnectedCameras()):
        cameras.append(SVBGetCameraInfo(idx))
    return cameras

class SVBonyCamera:
    """
    A class to represent and interface with a SVBony camera
    
    """

    def __init__(self, cidx: int):
        """Constructor

        Args:
            cidx (int): Index into list returned by svb_get_connected_cameras() indicating camera to connect to.

        Returns:
            None        
        """

        self.info = SVBGetCameraInfo(cidx)
        self.id = self.info['CameraID']
        self.camera = SVBOpenCamera(self.id)
        self.camera_properties = SVBGetCameraProperty(self.id)
        self.pixel_pitch_um = SVBGetSensorPixelSize(self.id)
        self.controls = []
        for idx in range(SVBGetNumOfControls(self.id)):
            self.controls.append(SVBGetControlCaps(self.id, idx))
        self.capture_thread = None
        self.running = False
        self.frame_rate_est = None
        self.callbacks = []
        SVBSetOutputImageType(self.id, SVB_IMG_TYPE.SVB_IMG_Y8)

    @property
    def output_image_type(self) -> SVB_IMG_TYPE:
        """Get the output image type
        
        Returns:
            SVB_IMG_TYPE: Image type        
        """
        return SVBGetOutputImageType(self.id)
    
    @output_image_type.setter
    def output_image_type(self, value: SVB_IMG_TYPE):
        """Set the output image type
        
        Args:
            value (SVB_IMG_TYPE): Image type        
        """
        SVBSetOutputImageType(self.id, value)

    @property
    def control_list(self):
        """Get a list of all controls available on the camera"""
        return self.controls
    
    @property
    def exposure(self) -> int:
        """get the exposure time in µs"""
        pexp, _auto = SVBGetControlValue(self.id, SVB_CONTROL_TYPE.SVB_EXPOSURE)
        return pexp

    @property
    def dropped_frames(self) -> int:
        """get the number of dropped frames"""
        return SVBGetDroppedFrames(self.id)

    @property
    def image_type(self) -> SVB_IMG_TYPE:
        """Get the image type"""
        return SVBGetOutputImageType(self.id)

    def add_callback(self, callback: types.FunctionType) -> None:
        """Add a callback to be called when a new frame is available
        
        Args:
            callback (types.FunctionType): A function to be called when a new frame is available.
                The function should take two arguments.  The first is a numpy array containing the image data. 
                The second is a datetime object containing the time the frame was captured.
        
        Returns:
            None                
        """
        
        self.callbacks.append(callback)

    def roi(self) -> tuple[int, int, int, int, int]:
        """get the region of interest
        
        Returns:
            tuple: (width, height, x, y, binning)
        """
        roi = SVBGetROIFormat(self.id)
        width = roi['width']
        height = roi['height']
        x = roi['startX']
        y = roi['startY']
        binning = roi['bin']
        return width, height, x, y, binning


    @property
    def max_cols(self) -> int:
        """get the maximum width"""
        return self.camera_properties['MaxWidth']
    
    @property
    def max_rows(self) -> int:
        """get the maximum height"""
        return self.camera_properties['MaxHeight']

    def sensor_format(self) -> int:
        """get the sensor format
        
        Returns:
            tuple: (width, height)
        """
        return (self.max_cols, self.max_rows)

    @exposure.setter
    def exposure(self, value):
        """Set exposure time in µs"""
        SVBSetControlValue(self.id, SVB_CONTROL_TYPE.SVB_EXPOSURE, value, False)

    @property
    def frame_speed_mode(self)->int:
        """get the frame speed mode
        
        Returns:
            int: Frame speed mode.  0 = Low Speed, 1 = Normal, 2 = High Speed
        
        """
        mode, _auto = SVBGetControlValue(self.id, SVB_CONTROL_TYPE.SVB_FRAME_SPEED_MODE)
        return mode

    @frame_speed_mode.setter
    def frame_speed_mode(self, value):
        """Set frame speed mode
        
        Args:
            value (int): Frame speed mode.  0 = Low Speed, 1 = Normal, 2 = High Speed
        
        """
        SVBSetControlValue(self.id, SVB_CONTROL_TYPE.SVB_FRAME_SPEED_MODE, value, False)


    @property
    def gain(self):
        """get the digital gain"""
        gain, _auto = SVBGetControlValue(self.id, SVB_CONTROL_TYPE.SVB_GAIN)
        return gain
    
    @gain.setter
    def gain(self, value):
        """Set frame rate in Hz"""
        SVBSetControlValue(self.id, SVB_CONTROL_TYPE.SVB_GAIN, value, False)

    @property
    def frame_rate(self) -> int|None:
        """get the frame rate"""
        return self.frame_rate_est

    def capture(self):
        """Thread to capture images"""
        
        width, height, _x, _y, _b = self.roi()
        imgtype = self.image_type
        bpp = bytes_per_pixel(imgtype)
        exposure_ms = self.exposure // 1000
        wait_duration = 2 * max(exposure_ms, 1000)
        self.running = True

        dt_last = dt.datetime.now()
        while self.running == True:
            img = SVBGetVideoData(self.id, width, height, bpp, waitMS=wait_duration)
            #img = img // 16
            dt_now = dt.datetime.now()
            self.frame_rate_est = 1/(dt_now-dt_last).total_seconds()
            dt_last = dt_now
            # Do something with the image
            for callback in self.callbacks:
                callback(img, dt_now)
            

    def start_capture(self):
        """Start video capture"""
        SVBStartVideoCapture(self.id)
        self.capture_thread = Thread(target=self.capture, args=())
        self.capture_thread.start()

    def stop_capture(self):
        """Stop video capture"""
        self.running = False
        exposure_ms = self.exposure // 1000
        wait_duration = 2 * max(exposure_ms, 1000)
        self.capture_thread.join(wait_duration)
        self.capture_thread = None
        print(f'Dropped frames: {self.dropped_frames}')
        SVBStopVideoCapture(self.id)
        self.frame_rate_est = None

    def __str__(self):
        """String representation of the camera

        Args:
            None

        Returns:
            str: A string representation of the camera.        
        """
        return \
            f"SVBony Camera {self.info['FriendlyName']}" + \
            f"\n\tSerial Number: {self.info['CameraSN']}" + \
            f"\n\tCamera ID: {self.info['CameraID']}" + \
            f"\n\tRows: {self.camera_properties['MaxHeight']}" + \
            f"\n\tColumns: {self.camera_properties['MaxWidth']}" + \
            f"\n\tPixel Pitch: {self.pixel_pitch_um:.2f} µm" + \
            f"\n\tColor: {self.camera_properties['IsColorCam']}" + \
            f"\n\tPort Type: {self.info['PortType']}" + \
            f""

    def __del__(self):
        """Destructor

        Args:
            None

        Returns:
            None        
        """
        #SVBCloseCamera(self.id)


if __name__=="__main__":
    import pprint
    import signal 
    import json
    import base64

    def callback(frame, timestamp):
        print(f'Frame received at {timestamp} with shape {frame.shape}')
        bytes = frame.tobytes()
        b64 = base64.b64encode(bytes).decode('utf-8')
        js = json.dumps({
            'timestamp': timestamp.isoformat(),
            'frame': b64,
            'shape': frame.shape,
        })

    print(svb_get_connected_cameras())
    camera = SVBonyCamera(0)
    print(camera)
    pprint.pp(camera.control_list)
    print(f'Exposure: {camera.exposure}')
    camera.exposure = 1000
    print(f'Exposure: {camera.exposure}')
    camera.gain = 10
    camera.frame_speed_mode = 0
    print(f'Gain: {camera.gain}')
    print(f'frame Speed Mode: {camera.frame_speed_mode}')
    camera.add_callback(callback)
    camera.start_capture()
    signal.signal(signal.SIGINT, lambda sig, frame: camera.stop_capture())
    print('Press Ctrl+C to stop capture')
    signal.pause()

# %%
