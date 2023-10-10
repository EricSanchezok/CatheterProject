import cv2
import numpy as np
import os
from torchvision import transforms
import torch
from model import ConvNet
from config import *

from PIL import Image



# 使用transforms来对图像进行预处理
transform = transforms.Compose([
    transforms.Resize((256, 256)),  # 调整图像大小
    transforms.ToTensor(),  # 将图像转换为PyTorch张量
])

model_path = '3DRegistration/models/convnet.pth'
model = ConvNet()
model.load_state_dict(torch.load(model_path, map_location=DEVICE))
model.eval()


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

    m = m if len(contour) > m else len(contour)

    for i in range(m):
        index = int(i / m * len(contour))
        contour_sample.append(contour[index])
    
    contour_sample = np.array(contour_sample, dtype=np.int32)

    return contour_sample


def get_thresh_img(path, img_name):
    # 读取该图片
    img_target = cv2.imread(path + img_name)

    # 提取轮廓
    img_gray = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 127, 255, 0)

    return thresh

def get_hu_moments(path, img_name):
    # 读取该图片
    img_target = cv2.imread(path + img_name)

    # 提取轮廓
    img_gray = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)

    moments = cv2.moments(img_gray)
    hu_moments = cv2.HuMoments(moments).flatten()

    return hu_moments



def get_suggest_τ(path, img_name):
    # 读取该图片
    img_target = cv2.imread(path + img_name)

    # 将 numpy.ndarray 转换为 PIL 图像
    pil_img = Image.fromarray(img_target)

    # 将图像转换为PyTorch张量
    img_tensor = transform(pil_img)

    output = model(img_tensor.unsqueeze(0)).squeeze(0).detach().numpy()

    return output


def save_image(img, path, name=None):
    if name is None:
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
    else:
        cv2.imwrite(path + name, img)