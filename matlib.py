"""
Minimal 4x4 matrix helpers for OpenGL — the handful of functions you'd
otherwise get from glm (C++) or pyrr (Python). Kept here instead of adding
a dependency, since a rotation/perspective/look-at matrix is only a few
lines each.

Matrices are built in standard row-major math notation. Upload them with
glUniformMatrix4fv(location, 1, GL_TRUE, matrix) — the GL_TRUE tells GL to
transpose into its own column-major layout, so no manual flattening needed.
"""

import numpy as np


def identity():
    return np.identity(4, dtype=np.float32)


def rotate_x(angle_rad):
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    m = identity()
    m[1, 1], m[1, 2] = c, -s
    m[2, 1], m[2, 2] = s, c
    return m


def rotate_y(angle_rad):
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    m = identity()
    m[0, 0], m[0, 2] = c, s
    m[2, 0], m[2, 2] = -s, c
    return m


def perspective(fovy_deg, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fovy_deg) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def look_at(eye, target, up):
    eye = np.array(eye, dtype=np.float32)
    target = np.array(target, dtype=np.float32)
    up = np.array(up, dtype=np.float32)

    forward = target - eye
    forward /= np.linalg.norm(forward)
    side = np.cross(forward, up)
    side /= np.linalg.norm(side)
    true_up = np.cross(side, forward)

    m = identity()
    m[0, :3] = side
    m[1, :3] = true_up
    m[2, :3] = -forward
    m[0, 3] = -np.dot(side, eye)
    m[1, 3] = -np.dot(true_up, eye)
    m[2, 3] = np.dot(forward, eye)
    return m
