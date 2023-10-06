from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *  
import glfw
from config import *
import numpy as np
from stl import mesh

import cv2

def init():
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
    set_projection_matrix(FX, FY, CX, CY, W, H, NEAR, FAR)

    glEnable(GL_DEPTH_TEST)

    # 渲染到帧缓冲区
    glBindFramebuffer(GL_FRAMEBUFFER, frame_buffer)


def shutdown():
    glfw.terminate()

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


def load_mesh(path):

    load_mesh = mesh.Mesh.from_file(path)

    vertices = load_mesh.vectors.reshape(-1, 3) * SACLE_FACTOR
    normals = load_mesh.normals.repeat(3, axis=0).reshape(-1, 3)

    return vertices, normals



def display(τ, vertices, normals):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # 平移
    glTranslatef(τ[0], τ[1], τ[2])

    # 旋转
    glRotatef(τ[3], 1, 0, 0)  # 绕x轴旋转
    glRotatef(τ[4], 0, 1, 0)  # 绕y轴旋转
    glRotatef(τ[5], 0, 0, 1)  # 绕z轴旋转

    # 启用顶点数组和法线数组
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    # 指定顶点和法线数组数据（使用顶点和法线列表）
    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glNormalPointer(GL_FLOAT, 0, normals)

    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)

def readPixels():

    img = np.zeros((H, W, 3), dtype=np.uint8)
    glReadPixels(0, 0, W, H, GL_BGR, GL_UNSIGNED_BYTE, img)
    img = np.flipud(img)

    opencv_mat = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return opencv_mat