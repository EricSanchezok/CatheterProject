import sys
import os
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_path)


import cv2
import numpy as np
from config import *

from ToolKits import useful_colors as colors

def getpos(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("HSV:", hsv[y, x], "coordinate:", x, y)

# 根据颜色分割函数
def color_seg(img, lower=lower_catheter, upper=upper_catheter, roi_range=roi_range):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    result = np.zeros_like(mask, dtype=np.uint8)

    if roi_range:
        result[roi_range] = mask[roi_range]

    result = cv2.medianBlur(result, 7)

    result = cv2.erode(result, np.ones((3, 3), np.uint8), iterations=1)
    result = cv2.dilate(result, np.ones((3, 3), np.uint8), iterations=1)

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


def fit_polynomial(points, degree):
    x = points[:, 0]
    y = points[:, 1]
    coefficients = np.polyfit(x, y, degree)
    polynomial = np.poly1d(coefficients)
    return polynomial

def divide_thresh_into_points(thresh, num_points):
    # 寻找轮廓
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if len(contours) == 0:
        return None
    # 只保留轮廓面积最大的轮廓
    contour = max(contours, key=cv2.contourArea).reshape((-1, 2))

    # 多项式拟合
    polynomial = fit_polynomial(contour, degree=3)

    # ******************************************** # 可能会出问题
    # 按照x坐标等分曲线
    x_values = np.linspace(min(contour[:, 0]), max(contour[:, 0]), num_points)
    y_values = polynomial(x_values)

    # 输出等分点的坐标
    result = np.column_stack((x_values, y_values))
    return result

if __name__ == '__main__':
    path = "Dataset\\RGBDIMGS\\20231217\\img_1.png"
    img = cv2.imread(path)

    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("img", getpos)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    thresh = color_seg(img)


    curve_points = divide_thresh_into_points(thresh, 8)
    
    # 画出等分点
    # for i in range(curve_points.shape[0]):
    #     cv2.circle(img, (int(curve_points[i, 0]), int(curve_points[i, 1])), 3, colors.get_blue2red_list(8)[i], -1)
        

    # img[thresh > 0] = (0, 0, 255)
    cv2.rectangle(img, point1, point2, (0, 255, 0), 2)
    cv2.imshow("img", img)


    cv2.waitKey(0)
    cv2.destroyAllWindows()
