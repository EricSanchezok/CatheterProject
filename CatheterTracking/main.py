import cv2
import numpy as np
import camera

import sys
sys.path.append("D:\\0-TJU\\CatheterProject\\Segmentation")

import CatheterSeg


cv2.namedWindow('color', cv2.WINDOW_NORMAL)

if __name__ == '__main__':
    
    realSense_L515 = camera.RealSenseL515()

    while True:
        color_image, depth_image = realSense_L515.get_aligned_frames()

        thresh = CatheterSeg.color_seg(color_image, CatheterSeg.lower_catheter, CatheterSeg.upper_catheter, CatheterSeg.roi_range)

        skeleton = CatheterSeg.skeletonize_image(thresh)

        # 把result画在原图上
        color_image[skeleton > 0] = (0, 0, 255)


        cv2.imshow("color", color_image)
        # cv2.imshow("depth", depth_image)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break