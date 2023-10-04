from Camera import RealSenseL515
from config import *

from pyinstrument import Profiler

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from stl import mesh

import cv2
import glfw

from scipy.optimize import leastsq

near, far = 10, 2000.0

scale_factor = 20.0

load_mesh = mesh.Mesh.from_file('Dataset\MedModels\\0014_H_AO_COA\\Models\\0102_0001.stl')

# 提取顶点和法线数据
vertices = load_mesh.vectors.reshape(-1, 3) * scale_factor
normals = load_mesh.normals.repeat(3, axis=0).reshape(-1, 3)

# 提取索引数据（构建索引列表）
indices = np.arange(len(vertices))

print(vertices.shape)
print(normals.shape)
print(len(vertices))

def save_image(img_render):

    path = "Dataset\\RegistrationImgs\\OpenGL\\"
    # 读取路径下的所有文件名
    files = os.listdir(path)
    if len(files) == 0:
        cv2.imwrite(path + "1.png", img_render)
    else:
        file_name = files[0]
        max_num = 0
        for file in files:
            num = int(file.split('.')[0])
            if num > max_num:
                max_num = num
        # 保存图片
        cv2.imwrite(path + str(max_num + 1) + ".png", img_render)


def set_projection_matrix(fx, fy, cx, cy, w, h, near, far):
    projection_matrix = np.zeros((4, 4), dtype=float)
    projection_matrix[0, 0] = 2 * fx / w
    projection_matrix[1, 1] = 2 * fy / h
    projection_matrix[0, 2] = 2 * cx / w - 1
    projection_matrix[1, 2] = 2 * cy / h - 1
    projection_matrix[2, 2] = -(far + near) / (far - near)
    projection_matrix[2, 3] = -2 * far * near / (far - near)
    projection_matrix[3, 2] = -1

    # 将投影矩阵设置为OpenGL当前投影矩阵
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(projection_matrix.T)
    glMatrixMode(GL_MODELVIEW)


def display(params):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # 平移
    glTranslatef(params[0], params[1], params[2])

    # 旋转
    glRotatef(params[3], 1, 0, 0)  # 绕x轴旋转
    glRotatef(params[4], 0, 1, 0)  # 绕y轴旋转
    glRotatef(params[5], 0, 0, 1)  # 绕z轴旋转

    # 启用顶点数组和法线数组
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    # 指定顶点和法线数组数据（使用顶点和法线列表）
    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glNormalPointer(GL_FLOAT, 0, normals)

    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)





def func(x, img_render, contour_sample):
    display(x)
    # 读取帧缓冲区中的像素数据
    glReadPixels(0, 0, W, H, GL_BGR, GL_UNSIGNED_BYTE, img_render)

    # 翻转图像垂直方向，因为OpenGL的坐标系统和OpenCV的坐标系统不同
    img_render = np.flipud(img_render)

    # 提取轮廓
    img_gray = cv2.cvtColor(img_render, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img_gray, 127, 255, 0)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 读取轮廓点
    contour = contours[0]
    contour = contour.reshape(-1, 2)
    contour = np.array(contour, dtype=float)

    distanceList = []
    for i in range(len(contour_sample)):
        distance = np.min(np.linalg.norm(contour_sample[i] - contour, axis=1))
        distanceList.append(distance)

    # 转换成numpy数组
    y = np.array(distanceList, dtype=float)

    return y


def main():



    path = "Dataset\\RegistrationImgs\\OpenGL\\"
    img_name = "30.png"
    # 读取该图片
    img_target = cv2.imread(path + img_name)

    # 提取轮廓
    img_gray = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img_gray, 127, 255, 0)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 对轮廓连续采样 m 个点
    m = 50

    # 读取轮廓点
    contour = contours[0]
    contour = contour.reshape(-1, 2)
    contour = np.array(contour, dtype=float)

    # 采样
    contour_sample = []
    for i in range(m):
        index = int(i / m * len(contour))
        contour_sample.append(contour[index])

    # 绘制采样的轮廓点
    for point in contour_sample:
        cv2.circle(img_target, (int(point[0]), int(point[1])), 1, (0, 0, 255), 2)


    # 初始化glfw
    if not glfw.init():
        return

    # 创建一个不可见的窗口
    glfw.window_hint(glfw.VISIBLE, False)
    window = glfw.create_window(W, H, "Hidden Window", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # 创建并设置帧缓冲区对象
    frame_buffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, frame_buffer)

    color_buffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, color_buffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, W, H)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color_buffer)

    depth_buffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_buffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, W, H)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_buffer)

    # 设置投影矩阵
    set_projection_matrix(FX, FY, CX, CY, W, H, near, far)

    glEnable(GL_DEPTH_TEST)

    # 渲染到帧缓冲区
    glBindFramebuffer(GL_FRAMEBUFFER, frame_buffer)


    x = np.array([0.0, 0.0, -500, 0.0, 0.0, 0.0], dtype=float)

    # 创建一个NumPy数组来存储图像数据
    img_render = np.zeros((H, W, 3), dtype=np.uint8)


    
    max_iterations = 1000  # 最大迭代次数


    for iteration in range(max_iterations):

        y = func(x, img_render, contour_sample)

        # 求 y 的模长
        e = 0.5 * y.T @ y
        print("iteration: %d, error: %f" % (iteration, e))
        # print("x: ", x)

        num_outputs = y.shape[0]
        num_inputs = x.shape[0]
        jacobian = np.zeros((num_outputs, num_inputs))

        for i in range(num_inputs):
            epsilon = 0.1
            delta_x = np.zeros_like(x)
            delta_x[i] = epsilon
            jacobian[:, i] = (func(x + delta_x, img_render, contour_sample) - func(x - delta_x, img_render, contour_sample)) / (2 * epsilon)


        I = np.eye(jacobian.shape[1], dtype=float) 

        u = 0.1 * np.linalg.norm(y) ** 2

        delta_x = - np.linalg.inv((jacobian.T @ jacobian + u * I)) @ jacobian.T @ y

        print("delta_x: ", delta_x)

        x += delta_x



        cv2.imshow("img_render", img_render)
        cv2.imshow("img_target", img_target)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break
        elif key == ord('c'):
            continue


                

    cv2.destroyAllWindows()
    glfw.terminate()

if __name__ == "__main__":
    main()
