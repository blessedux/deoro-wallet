#!/usr/bin/env python3
"""Generate placeholder Deoro PassKit PNGs (icon, logo, strip) at 1x/2x/3x."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

PASS_DIR = Path(__file__).resolve().parents[1] / "pass" / "Deoro Loyalty.pass"

ESPRESSO = (42, 28, 20, 255)
GOLD = (212, 175, 106, 255)
CREAM = (245, 230, 196, 255)
DARK = (28, 18, 14, 255)


def png(width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


def fill(w: int, h: int, color: tuple[int, int, int, int]) -> list[tuple[int, int, int, int]]:
    return [color] * (w * h)


def disc(pixels: list, w: int, h: int, cx: float, cy: float, r: float, color: tuple[int, int, int, int]) -> None:
    r2 = r * r
    for y in range(h):
        for x in range(w):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r2:
                pixels[y * w + x] = color


def write(name: str, w: int, h: int, pixels: list[tuple[int, int, int, int]]) -> None:
    path = PASS_DIR / name
    path.write_bytes(png(w, h, pixels))
    print(f"wrote {path.name} ({w}x{h})")


def icon(size: int) -> list[tuple[int, int, int, int]]:
    pixels = fill(size, size, ESPRESSO)
    disc(pixels, size, size, size / 2, size * 0.55, size * 0.28, GOLD)
    disc(pixels, size, size, size / 2, size * 0.52, size * 0.18, ESPRESSO)
    # cup handle
    for y in range(int(size * 0.42), int(size * 0.68)):
        for x in range(int(size * 0.68), int(size * 0.86)):
            dx = x - size * 0.72
            dy = y - size * 0.55
            if 0.35 * size * 0.35 * size > dx * dx + dy * dy > 0.18 * size * 0.18 * size and dx > 0:
                pixels[y * size + x] = GOLD
    return pixels


def logo(w: int, h: int) -> list[tuple[int, int, int, int]]:
    pixels = fill(w, h, ESPRESSO)
    # gold bar wordmark block — preview overlays "DEORO" as text
    margin = max(2, h // 10)
    for y in range(margin, h - margin):
        for x in range(margin, min(h - margin, w - margin)):
            pixels[y * w + x] = GOLD
    return pixels


def strip(w: int, h: int) -> list[tuple[int, int, int, int]]:
    pixels = fill(w, h, DARK)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(28 + (42 - 28) * t)
        g = int(18 + (28 - 18) * t)
        b = int(14 + (20 - 14) * t)
        for x in range(w):
            # quiet center so stamp text stays readable
            edge = min(x / w, 1 - x / w)
            if edge < 0.22:
                glow = int(40 * (0.22 - edge) / 0.22)
                pixels[y * w + x] = (
                    min(255, r + glow),
                    min(255, g + glow // 2),
                    min(255, b),
                    255,
                )
            else:
                pixels[y * w + x] = (r, g, b, 255)
    # gold cup mark on the trailing edge
    disc(pixels, w, h, w * 0.88, h * 0.62, h * 0.18, GOLD)
    disc(pixels, w, h, w * 0.88, h * 0.60, h * 0.11, DARK)
    return pixels


def main() -> None:
    PASS_DIR.mkdir(parents=True, exist_ok=True)
    for scale, suffix in ((1, ""), (2, "@2x"), (3, "@3x")):
        write(f"icon{suffix}.png", 29 * scale, 29 * scale, icon(29 * scale))
        write(f"logo{suffix}.png", 160 * scale, 50 * scale, logo(160 * scale, 50 * scale))
        write(f"strip{suffix}.png", 375 * scale, 144 * scale, strip(375 * scale, 144 * scale))


if __name__ == "__main__":
    main()
