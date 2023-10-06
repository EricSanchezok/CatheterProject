import cv2
import numpy as np
import os



def get_contour_points(path, img_name, m):

    # 读取该图片
    img_target = cv2.imread(path + img_name)

    # 提取轮廓
    img_gray = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 127, 255, 0)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 创建一个空的 NumPy 数组来存储所有点
    contour = np.array([], dtype=np.int32).reshape(0, 2)

    # 遍历所有轮廓，将轮廓的点连接起来
    for c in contours:
        contour = np.vstack((contour, c.reshape(-1, 2)))

    # 采样
    contour_sample = []
    for i in range(m):
        index = int(i / m * len(contour))
        contour_sample.append(contour[index])
    
    contour_sample = np.array(contour_sample, dtype=np.int32)

    return contour_sample


def save_image(img, path):
    # 读取路径下的所有文件名
    files = os.listdir(path)
    if len(files) == 0:
        cv2.imwrite(path + "1.png", img)
    else:
        max_num = 0
        for file in files:
            num = int(file.split('.')[0])
            if num > max_num:
                max_num = num
        cv2.imwrite(path + str(max_num + 1) + ".png", img)