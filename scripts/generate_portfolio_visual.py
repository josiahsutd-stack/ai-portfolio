from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "portfolio-site" / "assets" / "hero-built-environment-ai.png"
WIDTH = 1400
HEIGHT = 900


def clamp(value: int) -> int:
    return max(0, min(255, value))


def set_pixel(buffer: bytearray, x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        idx = (y * WIDTH + x) * 3
        buffer[idx : idx + 3] = bytes(color)


def draw_rect(
    buffer: bytearray, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]
) -> None:
    for y in range(max(0, y0), min(HEIGHT, y1)):
        row = (y * WIDTH + max(0, x0)) * 3
        for _ in range(max(0, x0), min(WIDTH, x1)):
            buffer[row : row + 3] = bytes(color)
            row += 3


def draw_line(
    buffer: bytearray, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]
) -> None:
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        set_pixel(buffer, x, y, color)
        set_pixel(buffer, x + 1, y, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def png_bytes(rgb: bytes) -> bytes:
    raw = b"".join(b"\x00" + rgb[y * WIDTH * 3 : (y + 1) * WIDTH * 3] for y in range(HEIGHT))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def main() -> None:
    buffer = bytearray(WIDTH * HEIGHT * 3)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            depth = y / HEIGHT
            lateral = x / WIDTH
            r = clamp(int(30 + 28 * lateral + 18 * depth))
            g = clamp(int(47 + 46 * lateral + 34 * depth))
            b = clamp(int(45 + 42 * lateral + 26 * depth))
            set_pixel(buffer, x, y, (r, g, b))

    for x in range(-200, WIDTH, 80):
        draw_line(buffer, x, HEIGHT, x + 520, 420, (72, 105, 95))
    for y in range(470, HEIGHT, 58):
        draw_line(buffer, 0, y, WIDTH, y - 95, (61, 90, 83))

    blocks = [
        (780, 310, 925, 760, (69, 96, 92)),
        (940, 240, 1090, 760, (82, 116, 107)),
        (1110, 360, 1270, 760, (58, 89, 103)),
        (690, 500, 780, 760, (107, 88, 64)),
        (1275, 455, 1375, 760, (86, 119, 91)),
    ]
    for x0, y0, x1, y1, color in blocks:
        draw_rect(buffer, x0, y0, x1, y1, color)
        for wx in range(x0 + 18, x1 - 12, 34):
            for wy in range(y0 + 24, y1 - 20, 42):
                draw_rect(buffer, wx, wy, wx + 12, wy + 17, (188, 173, 123))

    nodes = [(530, 230), (670, 170), (830, 230), (1000, 155), (1160, 250), (920, 420), (650, 410)]
    for start, end in zip(nodes, nodes[1:], strict=False):
        draw_line(buffer, start[0], start[1], end[0], end[1], (202, 160, 76))
    for x, y in nodes:
        for yy in range(-8, 9):
            for xx in range(-8, 9):
                if math.sqrt(xx * xx + yy * yy) <= 8:
                    set_pixel(buffer, x + xx, y + yy, (218, 178, 80))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(png_bytes(bytes(buffer)))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
