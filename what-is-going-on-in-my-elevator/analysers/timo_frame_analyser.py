import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2

# Define the directory paths where the image files, mask files, and annotation data are located
# FILL THESE! example depth_directory =r"D:\TIMo\timo_training_depth"
depth_directory = r" "
ir_directory = r" "
mask_directory = r" "
annotation_directory = r" "

def find_v(matrix):
    v_values = set([v for row in matrix for v in row if v != 0])
    result = {}
    
    for v in v_values:
        first_row = None
        last_row = None
        first_col = None
        last_col = None

        # Loop through each row of the matrix
        for i, row in enumerate(matrix):
            if v in row:
                # Record the index of the first row where v appears
                if first_row is None:
                    first_row = i
                # Record the index of the last row where v appears
                last_row = i

        # Loop through each column of the matrix
        for j in range(len(matrix[0])):
            column = [matrix[i][j] for i in range(len(matrix))]
            if v in column:
                # Record the index of the first column where v appears
                if first_col is None:
                    first_col = j
                # Record the index of the last column where v appears
                last_col = j
        
        # x_min, y_min, x_max, y_max 
        result[v] = (first_col, first_row, last_col, last_row )
    
    return result

def get_image_files(directory):
    """
    Returns a list of all the png image files in the given directory and its subdirectories.
    """
    image_files = [os.path.join(root, file) for root, dirs, files in os.walk(directory) for file in files if file.lower().endswith('.png')]
    return image_files

def get_frame_name_parts(image_file):
    frame_name = os.path.splitext(os.path.basename(image_file))[0].lstrip('0')
    frame_name_parts = frame_name.split('_')
    return frame_name_parts

def get_annotation_data(image_file, annotation_directory):
    """
    Returns the annotation data for the given image file.
    """
    annotation_file_path = os.path.join(annotation_directory, os.path.relpath(os.path.dirname(image_file), depth_directory), 'boxes_2d.csv')
    annotation_data = pd.read_csv(annotation_file_path, sep=';')
    return annotation_data

def get_annotation_frame_data(annotation_data, image_file):
    """
    Returns the annotation data for the given image file.
    """
    frame_name_parts = get_frame_name_parts(image_file)
    frame = frame_name_parts[-1]
    if 'frame' in annotation_data.columns.tolist():
        annotation_frame_data = annotation_data[annotation_data['frame'] == int(frame)]
    else:
        print("Column 'frame' not found in annotation data")
    return annotation_frame_data

def get_mask_data(mask_file):
    """
    Returns the mask data for the given mask file in grayscale format.
    """
    mask_data = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)
    return mask_data

def plot_images(depth_image_file, ir_image_file, annotation_data, class_mask_file, instance_mask_file):
    """
    Plots the two given images side by side and draws rectangles on them based on the given annotation data.
    """
    depth_img = plt.imread(depth_image_file)
    ir_img = plt.imread(ir_image_file)
    class_mask = get_mask_data(class_mask_file)
    instance_mask = get_mask_data(instance_mask_file)
    fig, ax = plt.subplots(2, 2)
    frame_name_parts = get_frame_name_parts(depth_image_file)
    fig.suptitle( "Action: " +  frame_name_parts[0] + " - SequenceID: " + frame_name_parts[2] + ' - Frame: ' + frame_name_parts[-1])
    ax[0, 0].imshow(depth_img)
    ax[0, 0].set_title('Depth Image')
    ax[0, 1].imshow(ir_img)
    ax[0, 1].set_title('IR Image')
    ax[1, 0].imshow(class_mask)
    ax[1, 0].set_title('Mask (Classes)')
    ax[1, 1].imshow(instance_mask)
    ax[1, 1].set_title('Mask (Instances)')
    for index, row in annotation_data.iterrows():
        annotation_rect1 = patches.Rectangle((row['x_min'], row['y_min']), row['x_max']-row['x_min'], row['y_max']-row['y_min'], linewidth=1, edgecolor='r', facecolor='none')
        annotation_rect2 = patches.Rectangle((row['x_min'], row['y_min']), row['x_max']-row['x_min'], row['y_max']-row['y_min'], linewidth=1, edgecolor='r', facecolor='none')
        ax[0, 0].add_patch(annotation_rect1)
        ax[0, 1].add_patch(annotation_rect2)
    boxes = find_v(instance_mask)
    for index, row in boxes.items():  
        mask_rect1 = patches.Rectangle((row[0], row[1]), row[2]-row[0], row[3]-row[1], linewidth=1, edgecolor='b', facecolor='none')
        mask_rect2 = patches.Rectangle((row[0], row[1]), row[2]-row[0], row[3]-row[1], linewidth=1, edgecolor='b', facecolor='none')
        ax[1, 0].add_patch(mask_rect1)
        ax[1, 1].add_patch(mask_rect2)
    plt.rcParams.update({'font.size': 8})
    plt.subplots_adjust(top=0.9, bottom=0, left=0.1, right=0.9, hspace=0.25, wspace=0.35)
    plt.show()

# Get all the png image files in image_directory1 and store their paths in a list
depth_image_files = get_image_files(depth_directory)

# Get all the png image files in image_directory2 and store their paths in a list
ir_image_files = get_image_files(ir_directory)

# Get all the png mask files in mask_directory and store their paths in a list
mask_files = get_image_files(mask_directory)

sequence_flag = ""
# Loop through the list of image file paths in image_directory1 and check if the same named image file exists in image_directory2
for image_file in depth_image_files:
    if os.path.basename(image_file) in [os.path.basename(x) for x in ir_image_files]:
        # Get the annotation data for the current image
        sequenceID = get_frame_name_parts(image_file)[2]
        if sequence_flag != sequenceID: 
            annotation_data = get_annotation_data(image_file, annotation_directory)
            sequence_flag = sequenceID
        annotation_frame_data = get_annotation_frame_data(annotation_data, image_file)   
        # Get the mask files for the current image
        class_mask_file = os.path.join(mask_directory, os.path.relpath(image_file, depth_directory)).replace('.png', '_classes.png')
        instance_mask_file = os.path.join(mask_directory, os.path.relpath(image_file, depth_directory)).replace('.png', '_instances.png')
        # If the same named image file exists, plot both images side by side for comparison
        ir_image_path = os.path.join(ir_directory, os.path.relpath(image_file, depth_directory))
        plot_images(image_file, ir_image_path, annotation_frame_data, class_mask_file, instance_mask_file)
        
        
