import cv2
import numpy as np
from config import *


def getpos(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("HSV:", hsv[y, x], "coordinate:", x, y)

# 根据颜色分割函数
def color_seg(img, lower, upper, roi_range=None):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # mask = cv2.Canny(gray, 50, 150)

    mask = cv2.inRange(hsv, lower, upper)

    result = np.zeros_like(mask, dtype=np.uint8)

    if roi_range:
        result[roi_range] = mask[roi_range]

    

    result = cv2.medianBlur(result, 5)

    result = cv2.dilate(result, np.ones((3, 3), np.uint8), iterations=1)
    # result = cv2.erode(result, np.ones((5, 5), np.uint8), iterations=25)
    
    # result = cv2.erode(result, np.ones((5, 5), np.uint8), iterations=2)

    return result

if __name__ == '__main__':
    path = "Dataset\\RGBDIMGS\\20231212\\img_1.png"
    img = cv2.imread(path)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("img", getpos)

    result = color_seg(img, lower_wall, upper_wall, roi_range)

    # 把result画在原图上
    img[result > 0] = (0, 0, 255)

    # roi画在原图上
    cv2.rectangle(img, point1, point2, (0, 255, 0), 2)

    cv2.imshow("img", img)
    cv2.imshow("result", result)

    cv2.waitKey(0)

    cv2.destroyAllWindows()