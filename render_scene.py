import argparse

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluLookAt, gluPerspective, gluNewQuadric, gluSphere
from PIL import Image


def make_offscreen_context(width: int, height: int):
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(width, height, "offscreen", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create offscreen GLFW context")
    glfw.make_context_current(window)
    return window


def make_fbo(width: int, height: int):
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    color_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, color_tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_tex, 0)

    depth_rb = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_rb)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_rb)

    status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if status != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(f"Framebuffer incomplete: status {status}")

    return fbo, color_tex, depth_rb


def draw_checkerboard(size: int = 8, tile: float = 1.0) -> None:
    half = size / 2.0
    glBegin(GL_QUADS)
    for i in range(size):
        for j in range(size):
            x0, z0 = (i - half) * tile, (j - half) * tile
            x1, z1 = x0 + tile, z0 + tile
            if (i + j) % 2 == 0:
                glColor3f(0.85, 0.85, 0.9)
            else:
                glColor3f(0.25, 0.25, 0.3)
            glNormal3f(0.0, 1.0, 0.0)
            glVertex3f(x0, 0.0, z0)
            glVertex3f(x1, 0.0, z0)
            glVertex3f(x1, 0.0, z1)
            glVertex3f(x0, 0.0, z1)
    glEnd()


def draw_cube(size: float = 1.0) -> None:
    s = size / 2.0
    faces = [
        # (normal, 4 vertices)
        ((0, 0, 1), [(-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]),
        ((0, 0, -1), [(s, -s, -s), (-s, -s, -s), (-s, s, -s), (s, s, -s)]),
        ((0, 1, 0), [(-s, s, s), (s, s, s), (s, s, -s), (-s, s, -s)]),
        ((0, -1, 0), [(-s, -s, -s), (s, -s, -s), (s, -s, s), (-s, -s, s)]),
        ((1, 0, 0), [(s, -s, s), (s, -s, -s), (s, s, -s), (s, s, s)]),
        ((-1, 0, 0), [(-s, -s, -s), (-s, -s, s), (-s, s, s), (-s, s, -s)]),
    ]
    glColor3f(0.8, 0.3, 0.25)
    glBegin(GL_QUADS)
    for normal, verts in faces:
        glNormal3f(*normal)
        for v in verts:
            glVertex3f(*v)
    glEnd()


def render(width: int, height: int) -> bytes:
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_POSITION, [4.0, 6.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.95, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.15, 0.15, 0.18, 1.0])

    glViewport(0, 0, width, height)
    glClearColor(0.53, 0.7, 0.85, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, width / height, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(4.0, 3.5, 6.0, 0.0, 0.6, 0.0, 0.0, 1.0, 0.0)

    draw_checkerboard()

    glPushMatrix()
    glTranslatef(-1.3, 0.6, 0.0)
    glRotatef(30.0, 0.0, 1.0, 0.0)
    draw_cube(1.2)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1.3, 0.8, 0.3)
    glColor3f(0.25, 0.55, 0.85)
    quad = gluNewQuadric()
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    gluSphere(quad, 0.8, 48, 48)
    glPopMatrix()

    glFinish()

    pixels = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    return pixels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="outputs/render.png")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=768)
    args = parser.parse_args()

    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    window = make_offscreen_context(args.width, args.height)
    fbo, color_tex, depth_rb = make_fbo(args.width, args.height)

    pixels = render(args.width, args.height)

    image = Image.frombytes("RGB", (args.width, args.height), pixels)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)  # GL origin is bottom-left
    image.save(args.out)

    glDeleteFramebuffers(1, [fbo])
    glDeleteTextures([color_tex])
    glDeleteRenderbuffers(1, [depth_rb])
    glfw.destroy_window(window)
    glfw.terminate()

    print(f"Saved {args.out} ({args.width}x{args.height})")


if __name__ == "__main__":
    main()
