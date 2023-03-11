from math import ceil
import cv2
import numpy as np
from typing import List, Tuple
# Camera configuration (radians)
CAMERA_FOV = [62 / 180 * np.pi, 53 / 180 * np.pi] # The VERTICAL anglular span that the camera can read
CAMERA_DEPRESSION = 45 / 180 * np.pi # angle of the camera below horizon

# Precompute the warp tables
def generate_warp_map(image_shape: Tuple[float,float], camera_fov:Tuple[float, float], camera_depression:float):
    print("[CAMERA > WARP CORRECTION] Generating warp map: 0.0% complete")
    phi_min = max(5.0 / 180 * np.pi, camera_depression - camera_fov[0] / 2)
    phi_max = camera_depression + camera_fov[0] / 2
    d_min = 1 / np.tan(phi_max)
    d_max = 1 / np.tan(phi_min)

    b_avg = np.sqrt((d_min+d_max)*(d_min+d_max)/4 + 1 * 1) * 0.5 * np.tan(camera_fov[1] / 2)
    x_map = np.zeros(image_shape, dtype=np.float32)
    y_map = np.zeros(image_shape, dtype=np.float32)
    
    progress = 0
    for y in range(image_shape[0]):
        d = d_max + (y/image_shape[0]) * (d_min - d_max)
        phi = np.arctan(1/d)
        mapped_y = image_shape[0] * (1/2 + (phi-camera_depression)/camera_fov[0])
        y_map[y,:] = [mapped_y for x in range(image_shape[1])]

        e = 1 / np.sqrt(d*d + 1 * 1)

        #b_0 = -0.5 * b_avg
        #m_0 = b_avg / image_shape[1]
        b_1 = -0.5 * b_avg * e
        m_1 = b_avg / image_shape[1] * e
        for x in range(image_shape[1]):
            #b = b_0 + m_0*x
            #psi = np.arctan(b * e)
            psi = np.arctan(b_1 + m_1 * x)
            #if(np.abs(psi) > camera_fov[1]/2):
            #    x_map[y,x] = 0
            #else:
            x_map[y,x] = image_shape[1] * (0.5 + psi / camera_fov[1])
        if y/image_shape[0] > (progress + 0.05):
            progress += 0.05
            print(f'[CAMERA > WARP CORRECTION] Generating warp map: {progress * 100}% complete')

    print("[CAMERA > WARP CORRECTION] Warp map completed")
    return [x_map, y_map]
    

def test(path = "data/img/45dep.jpg"):
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None :
        raise ValueError("Could not read file")
    [x_map, y_map] = generate_warp_map(image.shape[0:2],CAMERA_FOV, CAMERA_DEPRESSION)
    corrected_image = cv2.remap(image,x_map, y_map, cv2.INTER_LINEAR)
    
    cv2.namedWindow('original', cv2.WINDOW_KEEPRATIO)
    cv2.imshow('original', image)
    cv2.resizeWindow('original', 200, 700)

    cv2.namedWindow('corrected', cv2.WINDOW_KEEPRATIO)
    cv2.imshow('corrected', corrected_image)
    cv2.resizeWindow('corrected', 200, 700)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test()