import cv2
import numpy as np


def ir_image_filter(ir_img):
        mean = ir_img.mean() 
        ir_img2 = np.array(ir_img, np.uint8)
        np.where(ir_img2 == 0 , mean, ir_img2)
        np.log(ir_img2)
        cv2.normalize(ir_img2, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_8U)    
        return ir_img2


def depth_to_colormap(depth_image):
    # Normalize the depth image to fall within the range 0-255
    depth_image = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Apply the Jet colormap
    colored_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)

    return colored_image

def depth_to_HHA(depth_image, camera_matrix, height_above_ground=1.9):
    # Compute the surface normals
    normals = depth_to_surface_normal(depth_image)

    # Compute the horizontal disparity (inverse depth)
    disparity = np.reciprocal(depth_image, where=depth_image!=0)
    disparity[depth_image == 0] = 0

    # Compute the height above ground
    height = np.zeros_like(depth_image)
    height[depth_image != 0] = np.dot(camera_matrix[1, 1], height_above_ground) / depth_image[depth_image != 0]

    # Ensure normals[:, :, 2] is within the valid range for arccos
    normals[:, :, 2] = np.clip(normals[:, :, 2], -1, 1)

    # Compute the angle with gravity
    angle = np.arccos(normals[:, :, 2]) / np.pi * 180

    # Check the size and depth of the arrays
    assert disparity.shape == height.shape == angle.shape, "Input arrays must have the same size"
    assert disparity.dtype == height.dtype == angle.dtype, "Input arrays must have the same depth"

    # Stack the three channels to form the HHA image
    HHA = cv2.merge((disparity, height, angle))

    return HHA

def depth_to_surface_normal(depth, K):
    """
    depth: (h, w) of float, the unit of depth is meter
    K: (3, 3) of float, the depth camere's intrinsic
    """
    K = [[1, 0], [0, 1]] if K is None else K
    fx, fy = K[0][0], K[1][1]

    dz_dv, dz_du = np.gradient(depth)  # u, v mean the pixel coordinate in the image
    # u*depth = fx*x + cx --> du/dx = fx / depth
    epsilon = 1e-7  # small constant to avoid division by zero

    du_dx = np.divide(fx, depth + epsilon, where=depth!=0)
    dv_dy = np.divide(fy, depth + epsilon, where=depth!=0)

    dz_du = np.nan_to_num(dz_du)
    du_dx = np.nan_to_num(du_dx)
    dz_dv = np.nan_to_num(dz_dv)
    dv_dy = np.nan_to_num(dv_dy)
    dz_dx = dz_du * du_dx
    dz_dy = dz_dv * dv_dy
    # cross-product (1,0,dz_dx)X(0,1,dz_dy) = (-dz_dx, -dz_dy, 1)
    normal_cross = np.dstack((-dz_dx, -dz_dy, np.ones_like(depth)))
    # normalize to unit vector
    max_val = np.max(np.abs(normal_cross))
    normal_cross = normal_cross / max_val
    normal_unit = np.divide(normal_cross, np.linalg.norm(normal_cross, axis=2, keepdims=True) + epsilon, where=np.linalg.norm(normal_cross, axis=2, keepdims=True)!=0)
    normal_unit = np.nan_to_num(normal_unit)
    # set default normal to [0, 0, 1]
    normal_unit[~np.isfinite(normal_unit).all(2)] = [0, 0, 1]
    vis_normal = lambda normal: np.uint8((normal + 1) / 2 * 255)[..., ::-1]
    return vis_normal(normal_unit)