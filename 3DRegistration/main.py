from Camera import RealSenseL515
from config import *

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from stl import mesh

import cv2
import glfw

near, far = 10, 2000.0

scale_factor = 20.0

load_mesh = mesh.Mesh.from_file('Dataset\MedModels\\0014_H_AO_COA\\Models\\0102_0001.stl')
# 遍历顶点并缩放
for i in range(len(load_mesh.vectors)):
    for j in range(3):
        load_mesh.vectors[i][j] *= scale_factor
# 获取顶点和法线信息
vertices = load_mesh.vectors
normals = load_mesh.normals


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


def display(trans, rotat):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # 平移
    glTranslatef(trans[0], trans[1], trans[2])

    # 旋转
    glRotatef(rotat[0], 1, 0, 0)  # 绕x轴旋转
    glRotatef(rotat[1], 0, 1, 0)  # 绕y轴旋转
    glRotatef(rotat[2], 0, 0, 1)  # 绕z轴旋转

    # 渲染STL文件
    glBegin(GL_TRIANGLES)
    for i in range(len(normals)):
        for j in range(3):
            glNormal3fv(normals[i])  # 指定法线
            glVertex3fv(vertices[i, j])  # 指定顶点
    glEnd()


def save_image(img_array):

    path = "Dataset\\RegistrationImgs\\OpenGL\\"
    # 读取路径下的所有文件名
    files = os.listdir(path)
    if len(files) == 0:
        cv2.imwrite(path + "1.png", img_array)
    else:
        file_name = files[0]
        max_num = 0
        for file in files:
            num = int(file.split('.')[0])
            if num > max_num:
                max_num = num
        # 保存图片
        cv2.imwrite(path + str(max_num + 1) + ".png", img_array)


def main():
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

    trans = np.array([0.0, 0.0, -500], dtype=float)
    rotat = np.array([0.0, 0.0, 0.0], dtype=float)

    while True:

        display(trans, rotat)

        # 创建一个NumPy数组来存储图像数据
        img_array = np.zeros((H, W, 3), dtype=np.uint8)

        # 读取帧缓冲区中的像素数据
        glReadPixels(0, 0, W, H, GL_BGR, GL_UNSIGNED_BYTE, img_array)

        # 翻转图像垂直方向，因为OpenGL的坐标系统和OpenCV的坐标系统不同
        img_array = np.flipud(img_array)

        cv2.imshow("Image", img_array)


        # 对trans和rotat进行取随机数
        trans[2] = - np.random.rand() * 600 - 400
        rotat = np.random.rand(3) * 360

        # save_image(img_array)

        key = cv2.waitKey(30)

        if key == ord('q'):
            break
                

    cv2.destroyAllWindows()

    glfw.terminate()

if __name__ == "__main__":
    main()
