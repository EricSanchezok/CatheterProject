from config import *
import numpy as np
import cv2
import utils
import opengl

import random

import os
import csv


vertices, normals = opengl.load_mesh(PATH_MESH)

savePath = 'Dataset\\MedModels\\0014_H_AO_COA\\imgdata\\'
csvFilePath = 'Dataset\\MedModels\\0014_H_AO_COA\\tau_data.csv'

# 读取 savePath 目录下的所有文件名
files = os.listdir(savePath)
# 文件名格式为 image_0.jpg, image_1.jpg, ..., image_2999.jpg, 找到最大的编号
max_num = 0
if len(files) != 0:
    for file in files:
        num = int(file.split('.')[0].split('_')[1])
        if num > max_num:
            max_num = num
else:
    max_num = -1


opengl.init()

num = 2000

with open(csvFilePath, mode='a', newline='') as csvFile:
    csvWriter = csv.writer(csvFile)

    for i in range(num):

        while True:

            x = random.uniform(-200, 200)
            y = random.uniform(-200, 200)
            z = random.uniform(-400, -800)
            rx = random.uniform(0, 360)
            ry = random.uniform(0, 360)
            rz = random.uniform(0, 360)

            τ = np.array([x, y, z, rx, ry, rz], dtype=float)

            opengl.display(τ, vertices, normals)
            img = opengl.readPixels()

            # 二值化
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(img_gray, 127, 255, 0)

            if np.sum(thresh == 255) > 30000:
                # 生成图像文件名
                image_filename = f"image_{max_num + i + 1}.jpg"
                image_path = os.path.join(savePath, image_filename)
                # 将τ和图像文件名写入CSV文件
                csvWriter.writerow([x, y, z, rx, ry, rz, image_filename])
                # 保存图像
                cv2.imwrite(image_path, img)

                print(f"image_{max_num + i + 1}.jpg")

                break



opengl.shutdown()