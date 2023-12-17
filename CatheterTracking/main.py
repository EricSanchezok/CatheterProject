import sys
import os
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_path)

import cv2
import numpy as np

from Segmentation import CatheterSeg
from ToolKits import useful_colors as colors
from ToolKits import camera




if __name__ == '__main__':

    # cv2.namedWindow('color', cv2.WINDOW_NORMAL)
    
    realSense_L515 = camera.RealSenseL515()

    while True:
        color_image, depth_image = realSense_L515.get_aligned_frames()

        thresh = CatheterSeg.color_seg(color_image, CatheterSeg.lower_catheter, CatheterSeg.upper_catheter, CatheterSeg.roi_range)
        
        curve_points = CatheterSeg.divide_thresh_into_points(thresh, 8)
        
        # if curve_points is not None:
        #     # 画出等分点
        #     for i in range(curve_points.shape[0]):
        #         cv2.circle(color_image, (int(curve_points[i, 0]), int(curve_points[i, 1])), 5, colors.get_blue2red_list(8)[i], -1)

        color_image[thresh == 255] = (0, 0, 255)
        cv2.imshow("color", color_image)
        # cv2.imshow("depth", depth_image)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break