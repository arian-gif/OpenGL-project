# openGL

Small, low-resource OpenGL demos in Python. Both scripts are designed to use as little CPU/GPU as possible, for running alongside other demanding stuff (streaming video, games, etc.).

## Setup

```bash
pip install -r requirements.txt
```

## `main.py` — spinning triangle (live window)

A window showing a rotating RGB triangle, using the fixed-function OpenGL pipeline (no shaders).

```bash
python main.py
```

Press `Esc` or close the window to quit.

**Resource use:** VSync is enabled (`glfw.swap_interval(1)`), so the GPU idles between frames instead of rendering as fast as possible. A software frame cap (~30 FPS) via `time.sleep` acts as a fallback in case VSync is ignored by the driver.

Optional flag:
- `--seconds N` — auto-close after N seconds (useful for a quick smoke test instead of leaving the window open).

## `render_scene.py` — one-shot scene render (no window, no loop)

Renders a single frame — a cube and a sphere on a checkerboard floor, lit by a point light, viewed in perspective — to an off-screen framebuffer, then saves it as a PNG and exits.

```bash
python render_scene.py
```

Output goes to `outputs/render.png` by default.

**Resource use:** zero ongoing CPU/GPU usage. There's no visible window and no render loop — it draws exactly one frame into a hidden GLFW context + FBO (framebuffer object), reads the pixels back, writes the image, and the process exits immediately.

Optional flags:
- `--out PATH` — output file path (default `outputs/render.png`)
- `--width N` / `--height N` — output resolution (default 1024x768)

## Files

- [`main.py`](main.py) — live spinning-triangle demo
- [`render_scene.py`](render_scene.py) — one-shot offscreen scene render
- [`requirements.txt`](requirements.txt) — `PyOpenGL`, `glfw`, `Pillow`
