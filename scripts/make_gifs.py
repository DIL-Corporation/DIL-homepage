#!/usr/bin/env python3
"""
Create animated GIFs with transparent background for DIL site.
Saves to ../assets/ (edge-*.gif, engine-*.gif).
No external deps: uses scripts/gifwriter.py (pure Python).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gifwriter import (
    write_gif,
    create_canvas,
    draw_rect,
    draw_line,
    draw_ellipse,
    draw_polygon,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"
W, H = 480, 280
FPS = 12
DURATION_MS = 1000 // FPS
NUM_FRAMES = 24

# Palette indices: 0=transparent, 1-4=colors
TRANS, IDX_DARK, IDX_MID, IDX_LIGHT, IDX_WHITE = 0, 1, 2, 3, 4
BLUE_DARK = (37, 99, 235)
BLUE_MID = (59, 130, 246)
BLUE_LIGHT = (147, 197, 253)
WHITE = (255, 255, 255)
PALETTE = [(0, 0, 0), BLUE_DARK, BLUE_MID, BLUE_LIGHT, WHITE]
while len(PALETTE) < 256:
    PALETTE.append(WHITE)


def draw_planning_frames():
    """Bar chart growth (product planning)."""
    frames = []
    for i in range(NUM_FRAMES):
        t = (i + 1) / NUM_FRAMES
        c = create_canvas(W, H, TRANS)
        cx, cy = W // 2, H // 2
        bar_w, gap = 44, 20
        heights = [0.6, 0.85, 0.5, 0.9, 0.7]
        for j, h in enumerate(heights):
            x = cx - (len(heights) * (bar_w + gap) - gap) // 2 + j * (bar_w + gap)
            fill_h = int(120 * h * t)
            y_top = cy + 60 - fill_h
            draw_rect(c, x, y_top, x + bar_w, cy + 60, IDX_LIGHT, IDX_MID)
        frames.append(c)
    return frames


def draw_marketing_frames():
    """Rising trend line (marketing)."""
    frames = []
    margin = 60
    x0, y0 = margin, H - margin - 40
    x1, y1 = W - margin, margin + 40
    n_pts = 8
    for i in range(NUM_FRAMES):
        t = (i + 1) / NUM_FRAMES
        c = create_canvas(W, H, TRANS)
        pts = []
        for k in range(n_pts + 1):
            x = x0 + (x1 - x0) * k / n_pts
            progress = (k / n_pts) * t
            y = y0 - (y0 - y1) * (0.3 + 0.7 * progress)
            pts.append((x, y))
        for k in range(len(pts) - 1):
            draw_line(c, int(pts[k][0]), int(pts[k][1]), int(pts[k + 1][0]), int(pts[k + 1][1]), IDX_MID, 4)
        head = min(int(t * n_pts), n_pts)
        px, py = int(pts[head][0]), int(pts[head][1])
        draw_ellipse(c, px, py, 8, 8, IDX_DARK, IDX_MID)
        frames.append(c)
    return frames


def draw_data_frames():
    """Pulsing nodes (data-driven)."""
    frames = []
    for i in range(NUM_FRAMES):
        phase = (i / NUM_FRAMES) * 2 * math.pi
        c = create_canvas(W, H, TRANS)
        cx, cy = W // 2, H // 2
        nodes = [(cx - 100, cy), (cx, cy), (cx + 100, cy)]
        for j, (nx, ny) in enumerate(nodes):
            pulse = 0.85 + 0.15 * (1 + math.sin(phase + j * 2.1))
            r = int(20 * pulse)
            draw_ellipse(c, nx, ny, r, r, IDX_LIGHT, IDX_MID)
        draw_line(c, cx - 100, cy, cx, cy, IDX_MID, 3)
        draw_line(c, cx, cy, cx + 100, cy, IDX_MID, 3)
        frames.append(c)
    return frames


def draw_discovery_frames():
    """Magnifying glass (discovery)."""
    frames = []
    for i in range(NUM_FRAMES):
        t = (i + 1) / NUM_FRAMES
        c = create_canvas(W, H, TRANS)
        cx, cy = W // 2, H // 2
        r = int(50 * min(t * 1.2, 1.0))
        draw_ellipse(c, cx, cy - 20, r, r, IDX_LIGHT, IDX_MID)
        hx, hy = cx + r, cy + r - 20
        draw_line(c, hx, hy, hx + 30, hy + 40, IDX_MID, 5)
        bx, by = cx + 70, cy - 50
        draw_ellipse(c, bx, by, 15, 15, IDX_LIGHT, IDX_DARK)
        frames.append(c)
    return frames


def draw_operation_frames():
    """Horizontal bars (operation)."""
    frames = []
    for i in range(NUM_FRAMES):
        t = (i + 1) / NUM_FRAMES
        c = create_canvas(W, H, TRANS)
        cx, cy = W // 2, H // 2
        bar_h, bar_w_max = 24, 180
        ys = [cy - 50, cy - 10, cy + 30]
        for j, y in enumerate(ys):
            fill_t = min(t * 1.2 - j * 0.15, 1.0)
            if fill_t > 0:
                w = int(bar_w_max * fill_t)
                x1 = cx - bar_w_max // 2
                draw_rect(c, x1, y - bar_h // 2, x1 + w, y + bar_h // 2, IDX_LIGHT, IDX_MID)
        frames.append(c)
    return frames


def draw_expansion_frames():
    """Upward arrow (expansion)."""
    frames = []
    for i in range(NUM_FRAMES):
        t = (i + 1) / NUM_FRAMES
        c = create_canvas(W, H, TRANS)
        cx, cy = W // 2, H // 2 + 20
        stem_h = int(100 * t)
        draw_rect(c, cx - 8, cy + 40 - stem_h, cx + 8, cy + 40, IDX_MID, IDX_DARK)
        if t >= 0.5:
            head_y = cy + 40 - stem_h
            draw_polygon(c, [(cx, head_y - 25), (cx - 20, head_y), (cx + 20, head_y)], IDX_DARK, IDX_MID)
        frames.append(c)
    return frames


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    configs = [
        ("edge-planning.gif", draw_planning_frames),
        ("edge-marketing.gif", draw_marketing_frames),
        ("edge-data.gif", draw_data_frames),
        ("engine-discovery.gif", draw_discovery_frames),
        ("engine-operation.gif", draw_operation_frames),
        ("engine-expansion.gif", draw_expansion_frames),
    ]
    for name, drawer in configs:
        frames = drawer()
        out = ASSETS / name
        write_gif(frames, PALETTE, out, duration_ms=DURATION_MS, transparent_index=0)
        print("Saved:", out)
    print("Done. All GIFs in", ASSETS)


if __name__ == "__main__":
    main()
