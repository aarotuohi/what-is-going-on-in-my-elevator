# Import necessary libraries
import queue
import sys
import argparse

# Import modules from the listeners package
from listeners.camera_opener import *
from listeners.camera_stream import *
from listeners.process_event_queue import *
from listeners.ir_image_listener import *
from listeners.depth_image_listener import *

# Try to import the roypy package. If it's not installed, import the local version.
try:
    from roypypack import roypy  # package installation
except ImportError:
    import roypy  # local installation

def setup_camera(args):
    """
    Set up the camera based on the provided arguments.
    """
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser (usage = __doc__)
    # Add camera opener options to the parser
    add_camera_opener_options (parser)
    # Parse the arguments
    options = parser.parse_args(args)
    # Create a CameraOpener object with the parsed options
    opener = CameraOpener (options)
    try:
        # Try to open the camera
        cam = opener.open_camera()
    except:
        # If the camera can't be opened, print an error message and exit the program
        print("could not open Camera Interface")
        sys.exit(1)
    # Return the camera object
    return cam

def start_capture(cam, listener):
    """
    Start capturing images with the camera.
    """
    # Register the listener with the camera
    if isinstance(listener, MyIRImageListener):
        cam.registerIRImageListener(listener)
    elif isinstance(listener, MyDepthImageListener):
        cam.registerDepthImageListener(listener)
    # Start capturing images
    cam.startCapture()
    # Get the lens parameters
    lensP = cam.getLensParameters()
    # Set the lens parameters in the listener
    listener.setLensParameters(lensP)

def stream(args, format, save, listener_class, mode = "MODE_9_5FPS", save_dir = "", track = False):
    """
    Stream images from the camera.
    """
    # Set up the camera
    cam = setup_camera(args)
    try:
        # Try to replay a recording
        replay = cam.asReplay()
        replay.loop(False)
        print ("Using a recording")
        print ("Framecount : ", replay.frameCount())
        print ("File version : ", replay.getFileVersion())
    except SystemError:
        # If a recording can't be replayed, use a live camera
        print ("Using a live camera")
        cam.setUseCase(mode)
    # Create a queue for events
    q = queue.Queue()
    # Get the name of the recording without the extension
    rrf_name_without_extension = os.path.splitext(args[1])[0]
    rrf_name_without_extension = os.path.basename(rrf_name_without_extension)
    # Create a listener
    listener = listener_class(q, rrf_name_without_extension, format, save, save_dir, track)
    # Start capturing images
    start_capture(cam, listener)
    # Process the event queue
    process_event_queue (q, listener)
    # Stop capturing images
    cam.stopCapture()
    print("Done")