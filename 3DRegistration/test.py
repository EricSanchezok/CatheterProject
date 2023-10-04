import numpy as np

def load_stl(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(80)
        num_triangles = np.fromfile(f, dtype=np.uint32, count=1)[0]
        data = np.fromfile(f, dtype=np.float32)
    triangles = np.reshape(data, (-1, 12))
    return triangles


from OpenGL.GL import *
from OpenGL.GLUT import *

def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_FLAT)


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_TRIANGLES)
    triangles = load_stl("Dataset\\MedModels\\0014_H_AO_COA\\Models\\0102_0001.stl")
    for triangle in triangles:
        for vertex in triangle.reshape(-1, 3):
            glVertex3fv(vertex)
    glEnd()
    glFlush()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
glutCreateWindow("OpenGL Window")
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutMainLoop()