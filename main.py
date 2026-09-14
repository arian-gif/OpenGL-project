
import argparse
import time

import glfw
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_TRIANGLES,
    glBegin,
    glClear,
    glClearColor,
    glColor3f,
    glEnd,
    glLoadIdentity,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glVertex2f,
)

TARGET_FPS = 30
FRAME_TIME = 1.0 / TARGET_FPS


def draw_triangle(angle: float) -> None:
    glPushMatrix()
    glRotatef(angle, 0.0, 0.0, 1.0)

    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.2, 0.2)
    glVertex2f(0.0, 0.6)
    glColor3f(0.2, 1.0, 0.2)
    glVertex2f(-0.6, -0.4)
    glColor3f(0.2, 0.2, 1.0)
    glVertex2f(0.6, -0.4)
    glEnd()

    glPopMatrix()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seconds",
        type=float,
        default=None,
        help="Auto-close after this many seconds (useful for a quick smoke test).",
    )
    args = parser.parse_args()

    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    window = glfw.create_window(480, 360, "Spinning Triangle (low-power demo)", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")

    glfw.make_context_current(window)
    glfw.swap_interval(1)  # VSync on: GPU sleeps between frames

    glClearColor(0.08, 0.08, 0.1, 1.0)

    angle = 0.0
    start_time = time.perf_counter()

    while not glfw.window_should_close(window):
        frame_start = time.perf_counter()

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break
        if args.seconds is not None and (frame_start - start_time) >= args.seconds:
            break

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        draw_triangle(angle)
        angle += 0.6

        glfw.swap_buffers(window)
        glfw.poll_events()

        elapsed = time.perf_counter() - frame_start
        remaining = FRAME_TIME - elapsed
        if remaining > 0:
            time.sleep(remaining)

    glfw.terminate()


if __name__ == "__main__":
    main()
