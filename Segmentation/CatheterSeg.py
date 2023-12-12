import cv2
import numpy as np

from config import *

def getpos(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("HSV:", hsv[y, x], "coordinate:", x, y)

# 根据颜色分割函数
def color_seg(img, lower, upper, roi_range=None):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    result = np.zeros_like(mask, dtype=np.uint8)

    if roi_range:
        result[roi_range] = mask[roi_range]

    result = cv2.medianBlur(result, 7)

    result = cv2.erode(result, np.ones((3, 3), np.uint8), iterations=2)
    result = cv2.dilate(result, np.ones((3, 3), np.uint8), iterations=2)

    return result

def skeletonize_image(thresh, iterations=10):
    # 获取结构元素（这里使用椭圆形状的内核）
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    # 进行腐蚀操作，多次迭代，直到不能再腐蚀为止
    skeleton = np.zeros_like(thresh)
    for i in range(iterations):
        eroded = cv2.erode(thresh, kernel)
        temp = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(thresh, temp)
        skeleton = cv2.bitwise_or(skeleton, temp)
        thresh = eroded.copy()

    return skeleton

if __name__ == '__main__':
    path = "Dataset\\RGBDIMGS\\20231212\\img_3.png"
    img = cv2.imread(path)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("img", getpos)

    thresh = color_seg(img, lower_catheter, upper_catheter, roi_range)

    skeleton = skeletonize_image(thresh)

    # img[skeleton > 0] = (0, 0, 255)
    # cv2.rectangle(img, point1, point2, (0, 255, 0), 2)

    cv2.imshow("img", img)
    cv2.imshow("thresh", thresh)
    # cv2.imshow("skeleton", skeleton)

    cv2.waitKey(0)

    cv2.destroyAllWindows()
