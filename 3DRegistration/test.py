# -*- coding: utf-8 -*-

from OpenGL.GL import glGetString, GL_VERSION

try:
    print("OpenGL Version:", glGetString(GL_VERSION))
except OpenGL.error.GLError as e:
    error_code = e.err
    error_description = e.description.decode("utf-8", errors="replace")
    print(f"OpenGL Error ({error_code}): {error_description}")
