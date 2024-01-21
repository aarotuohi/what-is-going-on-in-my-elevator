# What is going in my elevator

## About The Project
This project is a comprehensive tool for image processing and indoor people detection, designed to be flexible and efficient. It utilizes depth and IR sensors, and is capable of handling both live camera feeds and pre-recorded .rrf files.

## Environment
This project has been successfully tested on the following operating systems:
- Windows 10
- Linux (Ubuntu 20.04)

## Setup
### Anaconda

1. Download the Anaconda installer for Windows and linux from the [official website](https://www.anaconda.com/products/distribution).
2. Run the installer and follow the prompts.
3. Open Anaconda navigator and go to "Environments".
4. Select "Create". Name your environment and select Python version based on following list (Note that these are only based on README from royale SDK and they might work with other python version):
 - Windows 10 - Python 3.10
 - Ubuntu 20.04 64bit    - Python 3.8
 - Linux ARM 32bit       - Python 3.7
 - Linux ARM 64bit       - Python 3.8
5. After new environment is created, click your environment, press green "play button" besides on your environment and select "open terminal". Next we will install royal SDK

### Royal SDK

#### Windows:

1. In terminal go to the path `.\royale\5.6.1.2299\python\packages`
2. Install the wheel:
```sh
pip install .\roypypack-5.6.1.2299-cp310-cp310-win_amd64.whl
```
3. If you encounter any issues, consider building and installing your own wheel via the sdist package. You'll need the "build" package and a working C++ build environment (e.g., CMake, Microsoft Visual Studio 2022). Install the sdist with (Remember change <PATH TO THE ROYALE FOLDER> with correcponding path):
```sh
pip install .\roypypack-5.6.1.2299.tar.gz --config-settings=cmake.define.ROYALE_DIR="<PATH TO THE ROYALE FOLDER>\royale\5.6.1.2299"
```
#### Linux:

1. In terminal go to the path `.\royale\5.6.1.2299\python\packages`
2. Install the wheel with:
```sh
pip install roypypack-5.6.1.2299-cp38-cp38-manylinux_2_31_x86_64.whl
```
3. Set the LD_LIBRARY_PATH to where the wheel is installed:
```sh
export LD_LIBRARY_PATH=/home/royale_user/.local/lib/python3.8/site-packages/roypypack
```
4. If you encounter any issues, consider building and installing your own wheel via the sdist package. You'll need the "build" package and a working C++ build environment (e.g., CMake, build-essential). Install the sdist with:
```sh
 pip install roypypack-5.6.1.2299.tar.gz --config-settings=cmake.define.ROYALE_DIR="/home/royale_user/apps/libroyale-5.6.1.2299-LINUX-x86-64Bit"
```
Please replace the placeholders with the actual paths and versions as per your setup!

### Libraries

This project uses the following Python libraries:

- OpenCV (cv2)
- pywin32 (ONLY FOR WINDOWS, contains the pythoncom packages needed by roypy)
- NumPy
- Matplotlib
- Pandas (optional as used only in `timo_frame_analyser.py` which is separate from main product)

Please note that NumPy and Matplotlib are also installed when the Royale SDK is installed, so you may not need to install them separately.

You can install these libraries using pip. Open a terminal and run the following commands:

```sh
pip install opencv-python
pip install pywin32
pip install numpy
pip install matplotlib
pip install pandas  # Optional
```

## How to Run the Project

To run the project in Visual Studio Code, follow these steps:

1. Open the `tof_stream_handler.py` file.
2. Press `Ctrl + Shift + P` to open the command palette.
3. Type `Python: Select Interpreter` and press Enter.
4. From the list of available interpreters, select the Anaconda environment you created for this project.
5. After selecting the correct interpreter, run the project.

## Initializing Parameters

This project uses several parameters that can be set to control its behavior:
### tof_stream_handler.py
- `SENSOR`: This parameter determines the type of sensor to use. It can be set to `"ir"` for an IR sensor or `"depth"` for a depth sensor.
- `INPUT_TYPE`: This parameter determines the input type. It can be set to `"--code"` to use a connected sensor camera or `"--rrf"` to use an .rrf file.
- `RRF_FILE_PATH`: This is the path to the .rrf file or the folder where .rrf files are located.
- `FORMAT`: This parameter determines the format of the output. For IR sensors, it can be set to `"grayscale"`. For depth sensors, it can be set to `"grayscale"`, `"colormapJET"`, `surfaceNormal`. If format is not given, `"grayscale"` is activated as initial mode.
- `SAVE`: This boolean parameter determines whether to save images (`True`) or stream the camera or .rrf files with object recognition using the current YOLO weights (`False`). Note that when Save mode is True it not show the image stream for provide better saving performance.
- `SAVE_PATH`: This is the path where images will be saved if `SAVE` is set to `True`.
- `MODE`: This parameter determines the mode and frame rate. For mode 9, it can be set to `"MODE_9_5FPS"`, `"MODE_9_10FPS"`, `"MODE_9_15FPS"`, `"MODE_9_20FPS"`, or `"MODE_9_30FPS"`. For mode 5, it can be set to `"MODE_5_15FPS"`, `"MODE_5_30FPS"`, `"MODE_5_45FPS"`, or `"MODE_5_60FPS"`. Mode 5 is for if precessor loading is a concern using 30% less processing overhead than mode 9. Mode 5 has lower depth range and quality.
- `TRACK`: This boolean parameter determines the tracking method for object detection. If set to `True`, a centroid tracker is used to track and count objects across multiple frames. If set to `False`, the system only counts the bounding boxes in the current frame without tracking objects across multiple frames.

### object_detection.py
- `CONF_THRESHOLD`: This is the minimum probability to filter weak detections. It is used to discard detections with a confidence score less than this threshold (usually discards false positive cases).
- `NMS_THRESHOLD`: This is the threshold for the non-maximum suppression algorithm, which eliminates redundant overlapping bounding boxes. A lower value means suppressing more.
- `CLASSES_FILE`: This is the path to the file containing the names of the classes that the YOLO model was trained to detect.
- `WEIGHT_FILE`: This is the path to the pre-trained weights of the YOLO model.
- `CONFIG_FILE`: This is the path to the configuration file of the YOLO model.

## Darknet

To create a YOLO model, it's recommended to install Darknet, DarkMark, and DarkHelp in the following order. You can find the instructions for building these tools at their respective GitHub pages:

- [Darknet](https://github.com/hank-ai/darknet)
- [DarkHelp](https://github.com/stephanecharette/DarkHelp)
- [DarkMark](https://github.com/stephanecharette/DarkMark)

For a step-by-step guide, consider following this [video tutorial](https://www.youtube.com/watch?v=WTT1s8JjLFk). If you're using Windows, it's highly recommended to use Windows Subsystem for Linux (WSL) or a Linux virtual machine when working with Darknet.

For additional information about Darknet, DarkHelp, and DarkMark, refer to the following resources:

- [Darknet API](https://darknetcv.ai/api/)
- [Darknet FAQ](https://www.ccoderun.ca/programming/darknet_faq/)
- [DarkHelp API Summary](https://www.ccoderun.ca/darkhelp/api/Summary.html)
- [DarkMark Summary](https://www.ccoderun.ca/darkmark/Summary.html)

For further assistance, join the [Discord server](https://discord.gg/zSq8rtW) where help is regularly provided.

## Dataset and Results

You can find the datasets and results for this project at the following location:

[SharePoint Link](https://tuni-my.sharepoint.com/:f:/g/personal/olli_lehmuskentta_tuni_fi/Ep_B0Dc8En5AkAcBOBcYeG8BWwc96b2nSOTWS_3q0bGlzw?e=S3h64h)

The most crucial folder is "G04 - Project Y - Kone" -> "Final". This folder contains the results, all training images and labels, as well as demo videos.

REMEMBER DOWNLOAD MATERIALS BEFORE SHAREPOINT LINK GOES OLD!



