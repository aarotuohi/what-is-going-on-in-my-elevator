from tkinter import * 

try:
    from roypypack import roypy  # package installation
except ImportError:
    import roypy  # local installation 

class CameraStreamer:
    """
    This class is responsible for streaming from a hardware camera.
    """

    @staticmethod
    def open_hardware_camera():
        """
        This method opens the first connected hardware camera.

        Returns:
            cam: The opened camera object.

        Raises:
            RuntimeError: If no cameras are connected.
        """

        # Create a CameraManager object
        c = roypy.CameraManager("")

        # Get the list of connected cameras
        l = c.getConnectedCameraList()

        # Print the number of connected cameras
        print("Number of cameras connected: ", l.size())

        # If no cameras are connected, raise an error
        if l.size() == 0:
            raise RuntimeError("No cameras connected")

        # Create a camera object for the first camera in the list
        cam = c.createCamera(l[0])

        # Initialize the camera
        cam.initialize()

        # Return the camera object
        return cam