import os
from listeners.streamer import stream
from listeners.ir_image_listener import MyIRImageListener
from listeners.depth_image_listener import MyDepthImageListener

def get_rrf_files(path):
    rrf_files = []

    if os.path.isdir(path):
        # If the path is a directory, get all .rrf files in the directory
        for filename in os.listdir(path):
            if filename.endswith(".rrf"):
                rrf_path = os.path.join(path, filename)
                rrf_files.append(rrf_path)
    elif os.path.isfile(path) and path.endswith(".rrf"):
        # If the path is a .rrf file, add it to the list
        rrf_files.append(path)
        if len(rrf_files) == 0:
            print("No .rrf files found in the given path")
    return rrf_files

def main():
    #ir = using sensor ir
    #depth = using sensor depth
    SENSOR = "depth"
    #--code = using sensor camera
    #--rrf = using .rrf file
    INPUT_TYPE = "--rrf"
    #path to .rrf file or folder where .rrf files exists
    RRF_FILE_PATH = r"D:\TIMo\OMAT\rff_renamed_31.10.2023\31.10.2023"
    #for ir: (initial: grayscale)
    #for depth:(initial: grayscale), surfaceNormal, colormapJET 
    FORMAT = "colormapJET"
    # True save images
    # False stream camera or .rrf files with object recognition using current yolo weights
    SAVE = False
    #path to save images
    SAVE_PATH = r"D:\TIMo\OMAT"
    # for mode 9 there is fps 5, 10, 15, 20, 30
    # for mode 5 there is fps 15, 30, 45, 60
    MODE = "MODE_9_5FPS"
    # True use centroid tracker to track and count objects
    # False only count bounding boxes in the frame
    TRACK = False
    rrf_files = get_rrf_files(RRF_FILE_PATH)
    rrf_files = rrf_files if rrf_files else [""]
    for rrf_file in rrf_files:
            if SENSOR == "ir":
                stream([INPUT_TYPE, rrf_file],FORMAT, SAVE, MyIRImageListener, MODE, SAVE_PATH, TRACK)
            else:
                stream([INPUT_TYPE, rrf_file],FORMAT, SAVE, MyDepthImageListener, MODE, SAVE_PATH, TRACK)
                


if __name__ == "__main__":
    main()