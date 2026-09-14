"""
Modern OpenGL demo: a lit, tumbling cube using the programmable pipeline
(GLSL shaders + VBO/VAO) instead of the deprecated glBegin/glEnd calls used
in main.py. This is the vocabulary most "OpenGL" job postings actually mean.

Same low-power habits as main.py: VSync on, frame rate capped in software
as a fallback, small window.

Usage:
    python modern_cube.py
    python modern_cube.py --seconds 3   # auto-close, for a quick smoke test
"""

import argparse
import ctypes
import time

import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import matlib

TARGET_FPS = 30
FRAME_TIME = 1.0 / TARGET_FPS

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec3 aColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 Normal;
out vec3 VertColor;

void main() {
    Normal = mat3(model) * aNormal;
    VertColor = aColor;
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec3 Normal;
in vec3 VertColor;

uniform vec3 lightDir;

out vec4 FragColor;

void main() {
    vec3 norm = normalize(Normal);
    float diff = max(dot(norm, normalize(-lightDir)), 0.0);
    vec3 ambient = 0.25 * VertColor;
    vec3 diffuse = diff * VertColor;
    FragColor = vec4(ambient + diffuse, 1.0);
}
"""

# position(3), normal(3), color(3) per vertex -- 6 faces x 2 triangles x 3 verts
CUBE_VERTICES = np.array([
    # front (+Z) - red
    -0.5, -0.5, 0.5,  0, 0, 1,  0.9, 0.2, 0.2,
     0.5, -0.5, 0.5,  0, 0, 1,  0.9, 0.2, 0.2,
     0.5,  0.5, 0.5,  0, 0, 1,  0.9, 0.2, 0.2,
     0.5,  0.5, 0.5,  0, 0, 1,  0.9, 0.2, 0.2,
    -0.5,  0.5, 0.5,  0, 0, 1,  0.9, 0.2, 0.2,
    -0.5, -0.5, 0.5,  0, 0, 1,  0.9, 0.2, 0.2,
    # back (-Z) - green
     0.5, -0.5, -0.5,  0, 0, -1,  0.2, 0.9, 0.3,
    -0.5, -0.5, -0.5,  0, 0, -1,  0.2, 0.9, 0.3,
    -0.5,  0.5, -0.5,  0, 0, -1,  0.2, 0.9, 0.3,
    -0.5,  0.5, -0.5,  0, 0, -1,  0.2, 0.9, 0.3,
     0.5,  0.5, -0.5,  0, 0, -1,  0.2, 0.9, 0.3,
     0.5, -0.5, -0.5,  0, 0, -1,  0.2, 0.9, 0.3,
    # left (-X) - blue
    -0.5, -0.5, -0.5,  -1, 0, 0,  0.25, 0.45, 0.9,
    -0.5, -0.5,  0.5,  -1, 0, 0,  0.25, 0.45, 0.9,
    -0.5,  0.5,  0.5,  -1, 0, 0,  0.25, 0.45, 0.9,
    -0.5,  0.5,  0.5,  -1, 0, 0,  0.25, 0.45, 0.9,
    -0.5,  0.5, -0.5,  -1, 0, 0,  0.25, 0.45, 0.9,
    -0.5, -0.5, -0.5,  -1, 0, 0,  0.25, 0.45, 0.9,
    # right (+X) - yellow
     0.5, -0.5,  0.5,  1, 0, 0,  0.95, 0.85, 0.2,
     0.5, -0.5, -0.5,  1, 0, 0,  0.95, 0.85, 0.2,
     0.5,  0.5, -0.5,  1, 0, 0,  0.95, 0.85, 0.2,
     0.5,  0.5, -0.5,  1, 0, 0,  0.95, 0.85, 0.2,
     0.5,  0.5,  0.5,  1, 0, 0,  0.95, 0.85, 0.2,
     0.5, -0.5,  0.5,  1, 0, 0,  0.95, 0.85, 0.2,
    # top (+Y) - white
    -0.5, 0.5,  0.5,  0, 1, 0,  0.9, 0.9, 0.9,
     0.5, 0.5,  0.5,  0, 1, 0,  0.9, 0.9, 0.9,
     0.5, 0.5, -0.5,  0, 1, 0,  0.9, 0.9, 0.9,
     0.5, 0.5, -0.5,  0, 1, 0,  0.9, 0.9, 0.9,
    -0.5, 0.5, -0.5,  0, 1, 0,  0.9, 0.9, 0.9,
    -0.5, 0.5,  0.5,  0, 1, 0,  0.9, 0.9, 0.9,
    # bottom (-Y) - purple
    -0.5, -0.5, -0.5,  0, -1, 0,  0.6, 0.3, 0.8,
     0.5, -0.5, -0.5,  0, -1, 0,  0.6, 0.3, 0.8,
     0.5, -0.5,  0.5,  0, -1, 0,  0.6, 0.3, 0.8,
     0.5, -0.5,  0.5,  0, -1, 0,  0.6, 0.3, 0.8,
    -0.5, -0.5,  0.5,  0, -1, 0,  0.6, 0.3, 0.8,
    -0.5, -0.5, -0.5,  0, -1, 0,  0.6, 0.3, 0.8,
], dtype=np.float32)


def create_cube_vao():
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, CUBE_VERTICES.nbytes, CUBE_VERTICES, GL_STATIC_DRAW)

    stride = 9 * 4  # 9 floats/vertex, 4 bytes/float
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)
    return vao


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=None)
    args = parser.parse_args()

    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    width, height = 480, 360
    window = glfw.create_window(width, height, "Modern OpenGL Cube (GLSL + VBO/VAO)", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")

    glfw.make_context_current(window)
    glfw.swap_interval(1)  # VSync: GPU sleeps between frames

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.1, 1.0)

    program = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER),
    )
    vao = create_cube_vao()

    model_loc = glGetUniformLocation(program, "model")
    view_loc = glGetUniformLocation(program, "view")
    proj_loc = glGetUniformLocation(program, "projection")
    light_loc = glGetUniformLocation(program, "lightDir")

    projection = matlib.perspective(45.0, width / height, 0.1, 100.0)
    view = matlib.look_at(eye=(2.2, 1.8, 3.2), target=(0, 0, 0), up=(0, 1, 0))

    start_time = time.perf_counter()

    while not glfw.window_should_close(window):
        frame_start = time.perf_counter()
        elapsed_total = frame_start - start_time

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break
        if args.seconds is not None and elapsed_total >= args.seconds:
            break

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        model = matlib.rotate_y(elapsed_total * 0.8) @ matlib.rotate_x(elapsed_total * 0.4)

        glUseProgram(program)
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)
        glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_TRUE, projection)
        glUniform3f(light_loc, -0.4, -1.0, -0.3)

        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        glfw.swap_buffers(window)
        glfw.poll_events()

        elapsed_frame = time.perf_counter() - frame_start
        remaining = FRAME_TIME - elapsed_frame
        if remaining > 0:
            time.sleep(remaining)

    glfw.terminate()


if __name__ == "__main__":
    main()
