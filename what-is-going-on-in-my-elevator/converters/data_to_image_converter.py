import os
import cv2

class ImgCreator():

    
    def __init__(self, dirName):
        self.frameGrayIndex = 0
        self.frameDepthIndex = 0
        self.dirGray = f"{dirName}_Ir/"
        self.dirDepth = f"{dirName}_Depth/"

    def addImgDepth(self, img, frame, rrf_file_name, BASE_DIR):
        self.dirGray, self.dirDepth = make_base_folder(BASE_DIR, rrf_file_name)
        if not os.path.exists(self.dirDepth):
            current_dir = os.getcwd()
            new_dir_path = os.path.join(current_dir, self.dirDepth)
            os.mkdir(new_dir_path)
        # Save the image as a PNG file
        cv2.imwrite(f"{self.dirDepth}/{rrf_file_name}_frame{frame}.png", img) 
        cv2.waitKey(0)


        
    def addImgGray(self, img, frame, rrf_file_name, BASE_DIR):
        self.dirGray, self.dirDepth = make_base_folder(BASE_DIR, rrf_file_name)
        if not os.path.exists(self.dirGray):
            current_dir = os.getcwd()
            new_dir_path = os.path.join(current_dir, self.dirGray)
            os.mkdir(new_dir_path)
        # Save the image as a PNG file
        cv2.imwrite(f"{self.dirGray}/{rrf_file_name}_frame{frame}.png", img) 
        cv2.waitKey(0)
    
def make_base_folder(base_dir, dirName):
    # Create the "processed_frames" directory
    processed_frames_dir = os.path.join(base_dir, "processed_frames")
    os.makedirs(processed_frames_dir, exist_ok=True)

    # Create the "ir_frames" and "depth_frames" directories
    ir_frames_dir = os.path.join(processed_frames_dir, "ir_frames")
    depth_frames_dir = os.path.join(processed_frames_dir, "depth_frames")
    os.makedirs(ir_frames_dir, exist_ok=True)
    os.makedirs(depth_frames_dir, exist_ok=True)

    # Use the new directories to save the frames
    dirGray = os.path.join(ir_frames_dir, f"{dirName}_Ir")
    dirDepth = os.path.join(depth_frames_dir, f"{dirName}_Depth")

    return dirGray, dirDepth
