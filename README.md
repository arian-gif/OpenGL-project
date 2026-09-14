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

## `modern_cube.py` — lit, tumbling cube (GLSL shaders + VBO/VAO)

A rotating cube rendered through the modern, programmable OpenGL pipeline — GLSL vertex/fragment shaders, vertex data in a VBO/VAO, and an MVP (model/view/projection) matrix stack — rather than the deprecated `glBegin`/`glEnd` calls in `main.py`. This is the OpenGL vocabulary most job postings actually mean (shaders, buffers, core profile) rather than the legacy fixed-function pipeline.

```bash
python modern_cube.py
```

Uses an OpenGL 3.3 core profile context. Matrix math (`perspective`, `look_at`, rotations) lives in [`matlib.py`](matlib.py) — a small hand-written helper instead of pulling in a dependency like `pyrr`.

**Resource use:** same habits as `main.py` — VSync on, ~30 FPS software cap, small window.

Optional flag:
- `--seconds N` — auto-close after N seconds (quick smoke test).

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

- [`main.py`](main.py) — live spinning-triangle demo (fixed-function pipeline)
- [`modern_cube.py`](modern_cube.py) — live tumbling-cube demo (GLSL shaders + VBO/VAO, core profile)
- [`matlib.py`](matlib.py) — small matrix math helpers (`perspective`, `look_at`, rotations) used by `modern_cube.py`
- [`render_scene.py`](render_scene.py) — one-shot offscreen scene render
- [`requirements.txt`](requirements.txt) — `PyOpenGL`, `glfw`, `Pillow`, `numpy`
