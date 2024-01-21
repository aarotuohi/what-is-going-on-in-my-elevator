# Import necessary libraries and modules
try:
    from roypypack import roypy  # package installation
except ImportError:
    import roypy  # local installation

import numpy as np
import matplotlib.pyplot as plt
import converters.data_to_image_converter
from analysers.sensor_data_processing import*
from yolo.object_detection import*
import threading

class MyDepthImageListener(roypy.IDepthImageListener):
    """
    Class for handling depth image data.
    """
    def __init__(self, q, rrf_file_name, format = "", save = False, save_dir = "", track = False):
        """
        Initialize the listener with necessary parameters and objects.
        """
        super(MyDepthImageListener, self).__init__()
        self.queue = q
        self.ImgCreator = converters.data_to_image_converter.ImgCreator(rrf_file_name)
        self.frame = 0
        self.done = False
        self.lock = threading.Lock()
        self.rrf_file_name = rrf_file_name
        self.save_dir = save_dir
        self.format = format
        self.save = save
        self.track = track
        self.detector = ObjectDetector()
        
    def onNewData(self, data):
        """
        Handle new data, convert depth data to numpy array and add to queue.
        """
        zvalues = [data.getDepth(i) for i in range(data.getNumPoints())]
        p = np.asarray(zvalues).reshape (-1, data.width)        
        self.queue.put(p)

    def paint (self, data):
        """
        Process and visualize the data. Save or display the result based on the configuration.
        """
        self.lock.acquire()
        data = data/1000  # Convert depth data to meters
        #check if depth data is in meters
        #print(np.max(data))

        # Process data based on the format
        if self.format == 'surfaceNormal':
            data = depth_to_surface_normal(data, self.cameraMatrix)
        elif self.format == 'colormapJET':
            data = depth_to_colormap(data)
        else:
            data = data.astype(np.uint8)
            cv2.normalize(data, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_8U)  
            data = cv2.cvtColor(data, cv2.COLOR_GRAY2RGB)

        # Save or display the result
        if self.save:
            if self.frame % 3 == 0:
                self.ImgCreator.addImgDepth(data, self.frame, self.rrf_file_name, self.save_dir)
        else:
            yoloResultImage = self.detector.detectObjects(data, self.track)
            resized = cv2.resize(yoloResultImage, (int(yoloResultImage.shape[1] * 250 / 100), int(yoloResultImage.shape[0] * 250 / 100)), interpolation = cv2.INTER_AREA)
            cv2.imshow("YOLO Objects on Image", resized)

        self.frame += 1
        self.lock.release()
        self.done = True

    def setLensParameters(self, lensParameters):
        """
        Set the camera matrix and distortion coefficients based on the lens parameters.
        """
        # Construct the camera matrix
        # (fx   0    cx)
        # (0    fy   cy)
        # (0    0    1 )
        self.cameraMatrix = np.array([[lensParameters['fx'], 0, lensParameters['cx']], [0, lensParameters['fy'], lensParameters['cy']], [0, 0, 1]], dtype=np.float32)
        
        # Construct the distortion coefficients
        # k1 k2 p1 p2 k3
        self.distortionCoefficients = np.array([lensParameters['k1'], lensParameters['k2'], lensParameters['p1'], lensParameters['p2'], lensParameters['k3']], dtype=np.float32).reshape(1, 5)