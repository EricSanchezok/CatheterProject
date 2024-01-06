import cv2
import os
import CatheterSeg
from config import *

if __name__ == '__main__':
    cap = cv2.VideoCapture(1)

    # 创建窗口
    cv2.namedWindow('Fullscreen', cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        

        thresh = CatheterSeg.color_seg(frame, lower_catheter, upper_catheter, roi_range)

        skeleton = CatheterSeg.skeletonize_image(thresh, 15)

        # 把result画在原图上
        frame[skeleton > 0] = (0, 0, 255)

        # roi画在原图上
        cv2.rectangle(frame, point1, point2, (0, 255, 0), 2)

        cv2.imshow("Fullscreen", frame)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()