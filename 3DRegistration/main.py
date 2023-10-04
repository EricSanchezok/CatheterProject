from Camera import RealSenseL515

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from stl import mesh

# 相机参数
fx, fy, cx, cy = 603.203230962510, 603.282035569803, 400.442038630029, 301.405795942410
w, h = 800, 600
near, far = 10, 2000.0

mesh = mesh.Mesh.from_file('Dataset\MedModels\\0014_H_AO_COA\\Models\\0102_0001.stl')

# 缩放比例
scale_factor = 20.0

# 遍历顶点并缩放
for i in range(len(mesh.vectors)):
    for j in range(3):
        mesh.vectors[i][j] *= scale_factor


# 获取顶点和法线信息
vertices = mesh.vectors
normals = mesh.normals

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

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(0, 0, -1000)

    # 渲染STL文件
    glBegin(GL_TRIANGLES)
    for i in range(len(normals)):
        for j in range(3):
            glNormal3fv(normals[i])  # 指定法线
            glVertex3fv(vertices[i, j])  # 指定顶点
    glEnd()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(w, h)
    
    # 将窗口标题转换为字节字符串
    title = b"STL Viewer"
    glutCreateWindow(title)

    glutDisplayFunc(display)

    # 设置投影矩阵
    set_projection_matrix(fx, fy, cx, cy, w, h, near, far)

    glEnable(GL_DEPTH_TEST)

    glutMainLoop()

if __name__ == "__main__":
    main()


