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

def remove_isolated_points(image, num_points=3):
    img = image.copy()
    points = np.nonzero(img)
    points = np.column_stack((points[1], points[0]))

    for i in range(points.shape[0]):
        point = points[i]
        roi = img[point[1]-1:point[1]+2, point[0]-1:point[0]+2]
        if np.sum(roi) <= 255*num_points:
            img[point[1], point[0]] = 0

    return img
       

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

    points = np.nonzero(skeleton)
    points = np.column_stack((points[1], points[0]))

    skeleton = remove_isolated_points(skeleton)

    # 保留起点和终点
    skeleton[points[0, 1], points[0, 0]] = 255
    skeleton[points[-1, 1], points[-1, 0]] = 255

    return skeleton


def fit_polynomial(points, degree):
    x = points[:, 0]
    y = points[:, 1]
    coefficients = np.polyfit(x, y, degree)
    polynomial = np.poly1d(coefficients)

    coefficients_inv = np.polyfit(y, x, degree)
    polynomial_inv = np.poly1d(coefficients_inv)

    return polynomial, polynomial_inv

def divide_thresh_into_points(thresh, num_points):
    # 寻找轮廓
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if len(contours) == 0:
        return None
    
    contour = max(contours, key=cv2.contourArea)

    img = np.zeros_like(thresh)
    cv2.drawContours(img, [contour], 0, 255, -1)

    # 骨架化
    skeleton = skeletonize_image(img, iterations=20)
    # cv2.imshow("skeleton", skeleton)

    # 将图像中白色的点作为一个numpy数组
    points = np.nonzero(skeleton)
    points = np.column_stack((points[1], points[0]))

    points_0 = points[0]
    points = points - points_0

    polynomial, polynomial_inv = fit_polynomial(points, degree=4)

    x_values = np.linspace(min(points[:, 0]), max(points[:, 0]), num_points)
    y_values = polynomial(x_values)

    result = np.column_stack((x_values, y_values))

    loss = 0
    for i in range(result.shape[0]):
        for j in range(points.shape[0]):
            loss += np.linalg.norm(result[i] - points[j])

    loss /= result.shape[0] * points.shape[0]

    y_values = np.linspace(min(points[:, 1]), max(points[:, 1]), num_points)
    x_values = polynomial_inv(y_values)

    result_inv = np.column_stack((x_values, y_values))

    loss_inv = 0
    for i in range(result_inv.shape[0]):
        for j in range(points.shape[0]):
            loss_inv += np.linalg.norm(result_inv[i] - points[j])

    loss_inv /= result_inv.shape[0] * points.shape[0]

    result = result + points_0
    result_inv = result_inv + points_0


    # print("loss:", loss, "loss_inv:", loss_inv)

    if loss < loss_inv:
        return result
    return result_inv 

if __name__ == '__main__':
    path = "Dataset\\RGBDIMGS\\20231220\\img_9.png"
    img = cv2.imread(path)

    point_num = 10

    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("img", getpos)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    thresh = color_seg(img)

    curve_points = divide_thresh_into_points(thresh, point_num)

    if curve_points is not None:    
        # 画出等分点
        for i in range(curve_points.shape[0]):
            cv2.circle(img, (int(curve_points[i, 0]), int(curve_points[i, 1])), 5, colors.get_blue2red_list(point_num)[i], -1)
            
    # img[thresh > 0] = (0, 0, 255)
    cv2.rectangle(img, point1, point2, (0, 255, 0), 2)
    cv2.imshow("img", img)





    cv2.waitKey(0)
    cv2.destroyAllWindows()
