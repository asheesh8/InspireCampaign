"""Pop-art wave bands: layered red, yellow and blue swells with contour lines, speckle dots and halftone.

Output is inline SVG whose colours are CSS variables (--red, --yellow, --blue, --ink, --bg), so one drawing
recolours for light, dark and pop modes. The front layer is filled with the NEXT section's background, so the
band melts into whatever follows it. Deterministic: the same seed always draws the same band.
"""
import math
import random

W = 2160          # wider than the viewBox so layers can drift sideways without showing an edge
VIEW_W = 1440


def _edge(rng, base, amp, n=4):
    """Top edge of one swell: a few summed sines."""
    waves = [(rng.uniform(0.6, 2.4) / W * math.tau, rng.uniform(0, math.tau), amp * rng.uniform(0.35, 1)) for _ in range(n)]
    return lambda x: base + sum(a * math.sin(f * x + p) for f, p, a in waves)


def _path(fn, h, step=18):
    pts = [(x, fn(x)) for x in range(0, W + step, step)]
    d = f"M0 {h} L" + " L".join(f"{x} {y:.1f}" for x, y in pts) + f" L{W} {h} Z"
    return d


def _line(fn, off, step=18):
    return "M" + " L".join(f"{x} {fn(x) + off:.1f}" for x in range(0, W + step, step))


def waves(seed=1, h=240, next_bg="var(--bg)", flip=False):
    rng = random.Random(seed)
    layers = [("red", h * 0.22, 34), ("yellow", h * 0.40, 30), ("blue", h * 0.58, 26)]
    out = []
    for i, (tone, base, amp) in enumerate(layers):
        fn = _edge(rng, base, amp)
        dots = []
        for _ in range(26):
            x = rng.uniform(0, W)
            y = fn(x) + rng.uniform(10, h * 0.35)
            if y > h - 6:
                continue
            r = rng.choice([2, 2, 3, 3, 4, 6, 9])
            fill = "var(--ink)" if r < 6 else rng.choice(["var(--yellow)", "var(--red)", "var(--blue)"])
            ring = ' stroke="var(--ink)" stroke-width="2.5"' if r >= 6 else ""
            dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{fill}"{ring}/>')
        swirls = []
        for _ in range(3):
            x = rng.uniform(80, W - 80)
            y = fn(x) + rng.uniform(22, 44)
            if y < h - 20:
                swirls.append(
                    f'<path d="M{x:.0f} {y:.0f} a8 8 0 1 1 8 8 a14 14 0 1 1 -14 -14 a20 20 0 1 1 20 20" '
                    f'fill="none" stroke="var(--ink)" stroke-opacity=".45" stroke-width="2" stroke-linecap="round"/>')
        out.append(
            f'<g class="waves__layer waves__layer--{i}">'
            f'<path d="{_path(fn, h)}" fill="var(--{tone})"/>'
            f'<path d="{_line(fn, 9)}" fill="none" stroke="var(--ink)" stroke-opacity=".35" stroke-width="2" stroke-dasharray="120 26 60 34"/>'
            f'<path d="{_line(fn, 18)}" fill="none" stroke="var(--ink)" stroke-opacity=".22" stroke-width="1.6" stroke-dasharray="70 40 150 30"/>'
            f'{"".join(swirls)}{"".join(dots)}</g>')
    front = _edge(rng, h * 0.8, 20)
    out.append(f'<g class="waves__layer waves__layer--3"><path d="{_path(front, h)}" fill="{next_bg}"/>'
               f'<path d="{_line(front, 0)}" fill="none" stroke="var(--ink)" stroke-width="2.5"/></g>')
    hid = f"ht{seed}"
    halftone = (
        f'<defs><pattern id="{hid}" width="14" height="14" patternUnits="userSpaceOnUse">'
        f'<circle cx="7" cy="7" r="2.6" fill="var(--ink)"/></pattern>'
        f'<linearGradient id="{hid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
        f'<stop offset=".45" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="{hid}m"><rect width="{W}" height="{h}" fill="url(#{hid}g)"/></mask></defs>'
        f'<rect class="waves__halftone" width="{W}" height="{h}" fill="url(#{hid})" mask="url(#{hid}m)"/>')
    flip_attr = ' style="transform:scaleY(-1)"' if flip else ""
    return (f'<div class="waves" aria-hidden="true"{flip_attr}><svg viewBox="0 0 {VIEW_W} {h}" '
            f'preserveAspectRatio="xMidYMax slice" focusable="false">{halftone}{"".join(out)}</svg></div>')
