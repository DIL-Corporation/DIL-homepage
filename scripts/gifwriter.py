"""
Minimal animated GIF89a writer with transparency. No dependencies.
"""
import struct
from pathlib import Path


def lzw_encode(data, min_bits=8):
    """Encode list of byte values (0-255) to LZW-compressed bytes for GIF."""
    clear_code = 1 << min_bits
    end_code = clear_code + 1
    max_code = 4095
    code_size = min_bits + 1
    next_code = end_code + 1

    table = {bytes([i]): i for i in range(256)}

    result = []
    chunk_bits = []
    prefix = b""

    def flush_bits():
        nonlocal chunk_bits
        while len(chunk_bits) >= 8:
            byte = sum((chunk_bits.pop(0) & 1) << i for i in range(8))
            result.append(byte)
        return

    def write_code(c):
        nonlocal code_size, chunk_bits
        for b in range(code_size):
            chunk_bits.append((c >> b) & 1)
        flush_bits()

    write_code(clear_code)

    for byte in data:
        new_prefix = prefix + bytes([byte])
        if new_prefix in table:
            prefix = new_prefix
        else:
            write_code(table[prefix])
            if next_code <= max_code:
                table[new_prefix] = next_code
                next_code += 1
                if next_code > (1 << code_size):
                    code_size = min(12, code_size + 1)
            prefix = bytes([byte])

    if prefix:
        write_code(table[prefix])
    write_code(end_code)
    if chunk_bits:
        while len(chunk_bits) < 8:
            chunk_bits.append(0)
        flush_bits()
    return bytes(result)


def write_gif(frames, palette, filepath, duration_ms=83, transparent_index=0):
    """
    Write animated GIF89a.
    frames: list of 2D arrays (H rows, W cols) of palette indices 0-255
    palette: list of (r,g,b), length 256; index transparent_index is transparent
    """
    if not frames:
        return
    H, W = len(frames[0]), len(frames[0][0])
    # Build global color table (256 colors, 3 bytes each)
    pal_bytes = bytearray(768)
    for i, c in enumerate(palette[:256]):
        pal_bytes[i * 3 : i * 3 + 3] = c[0], c[1], c[2]

    with open(filepath, "wb") as f:
        # GIF89a header
        f.write(b"GIF89a")
        # Logical Screen Descriptor: width, height, packed, bg, aspect
        f.write(struct.pack("<HH", W, H))
        # packed: global color table 1, color resolution 8, sort 0, size 7 (256 colors) -> 0xf7
        f.write(bytes([0xF7, 0, 0]))
        # Global Color Table
        f.write(pal_bytes)

        # Netscape Application Extension (loop)
        f.write(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

        for idx, frame in enumerate(frames):
            # Graphic Control Extension: disposal=2, transparent, duration
            f.write(b"\x21\xF9\x04\x02")  # disposal=2 (restore to background)
            f.write(struct.pack("<H", duration_ms))
            f.write(bytes([transparent_index, 0]))
            # Image Descriptor
            f.write(b"\x2C")
            f.write(struct.pack("<HHHHH", 0, 0, W, H, 0))
            # Image Data: LZW minimum code size (8), then LZW-compressed subblocks
            flat = []
            for row in frame:
                flat.extend(row)
            f.write(bytes([8]))  # LZW minimum code size
            compressed = lzw_encode(flat, min_bits=8)
            # Subblocks (max 255 bytes each)
            pos = 0
            while pos < len(compressed):
                block_len = min(255, len(compressed) - pos)
                f.write(bytes([block_len]))
                f.write(compressed[pos : pos + block_len])
                pos += block_len
            f.write(b"\x00")
        f.write(b";")


def create_canvas(w, h, default=0):
    """Create 2D list of default index (0 = transparent)."""
    return [[default] * w for _ in range(h)]


def draw_rect(canvas, x1, y1, x2, y2, idx, outline_idx=None):
    """Fill rectangle (inclusive), optional outline. Clips to canvas."""
    H, W = len(canvas), len(canvas[0])
    for y in range(max(0, y1), min(H, y2 + 1)):
        for x in range(max(0, x1), min(W, x2 + 1)):
            canvas[y][x] = idx
    if outline_idx is not None:
        for x in range(max(0, x1), min(W, x2 + 1)):
            if 0 <= y1 < H:
                canvas[y1][x] = outline_idx
            if 0 <= y2 < H:
                canvas[y2][x] = outline_idx
        for y in range(max(0, y1), min(H, y2 + 1)):
            if 0 <= x1 < W:
                canvas[y][x1] = outline_idx
            if 0 <= x2 < W:
                canvas[y][x2] = outline_idx


def draw_line(canvas, x0, y0, x1, y1, idx, thickness=1):
    """Bresenham line. thickness approximates by drawing multiple lines."""
    H, W = len(canvas), len(canvas[0])
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    half = thickness // 2
    for _ in range(max(dx, dy) + 1):
        for oy in range(-half, half + 1):
            for ox in range(-half, half + 1):
                nx, ny = x + ox, y + oy
                if 0 <= nx < W and 0 <= ny < H:
                    canvas[ny][nx] = idx
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def draw_ellipse(canvas, cx, cy, rx, ry, fill_idx, outline_idx=None):
    """Fill ellipse (cx,cy) radii rx,ry. outline optional."""
    H, W = len(canvas), len(canvas[0])
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            if (dx * dx) / (rx * rx + 1e-9) + (dy * dy) / (ry * ry + 1e-9) <= 1:
                x, y = cx + dx, cy + dy
                if 0 <= x < W and 0 <= y < H:
                    canvas[y][x] = fill_idx
    if outline_idx is not None and rx >= 2 and ry >= 2:
        for dy in range(-ry, ry + 1):
            for dx in range(-rx, rx + 1):
                if (dx * dx) / (rx * rx + 1e-9) + (dy * dy) / (ry * ry + 1e-9) >= 0.92 and (dx * dx) / (rx * rx + 1e-9) + (dy * dy) / (ry * ry + 1e-9) <= 1.02:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < W and 0 <= y < H:
                        canvas[y][x] = outline_idx


def draw_polygon(canvas, pts, fill_idx, outline_idx=None):
    """Fill polygon (list of (x,y)). Simple scanline fill."""
    if len(pts) < 3:
        return
    H, W = len(canvas), len(canvas[0])
    min_y = max(0, min(p[1] for p in pts))
    max_y = min(H - 1, max(p[1] for p in pts))
    for y in range(min_y, max_y + 1):
        intersections = []
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            if y1 <= y < y2 or (y == y2 and y2 != y1):
                if y2 != y1:
                    x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                    intersections.append(x)
        intersections.sort()
        for i in range(0, len(intersections), 2):
            x1, x2 = int(intersections[i]), int(intersections[i + 1]) if i + 1 < len(intersections) else int(intersections[i])
            for x in range(max(0, x1), min(W, x2 + 1)):
                canvas[y][x] = fill_idx
    if outline_idx is not None:
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            draw_line(canvas, int(x0), int(y0), int(x1), int(y1), outline_idx, 2)
