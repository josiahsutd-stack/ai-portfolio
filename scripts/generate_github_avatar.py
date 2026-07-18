from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
AVATAR_PATH = ROOT / "portfolio-site" / "assets" / "github-profile-avatar.png"
AVATAR_SIZE = 512
DRAW_SCALE = 4


def build_avatar_image() -> Image.Image:
    size = AVATAR_SIZE
    scale = DRAW_SCALE
    background = "#0d1b2a"
    image = Image.new("RGB", (size * scale, size * scale), background)
    draw = ImageDraw.Draw(image)

    def px(value: int) -> int:
        return value * scale

    for offset in range(64, size, 64):
        draw.line((px(offset), 0, px(offset), px(size)), fill="#153044", width=px(1))
        draw.line((0, px(offset), px(size), px(offset)), fill="#153044", width=px(1))

    draw.rounded_rectangle(
        (px(54), px(54), px(458), px(458)),
        radius=px(84),
        outline="#22a699",
        width=px(8),
    )

    draw.rounded_rectangle(
        (px(116), px(252), px(232), px(376)),
        radius=px(58),
        fill="#ffffff",
    )
    draw.rectangle((px(116), px(252), px(174), px(318)), fill=background)
    draw.rectangle((px(174), px(136), px(232), px(326)), fill="#ffffff")

    draw.rectangle((px(268), px(136), px(326), px(376)), fill="#22a699")
    draw.rectangle((px(326), px(318), px(408), px(376)), fill="#22a699")
    draw.rectangle((px(128), px(384), px(384), px(396)), fill="#dcae4f")

    return image.resize((size, size), Image.Resampling.LANCZOS)


def avatar_is_current(path: Path = AVATAR_PATH) -> bool:
    if not path.is_file():
        return False
    try:
        with Image.open(path) as current:
            normalized = current.convert("RGB")
            return (
                normalized.size == (AVATAR_SIZE, AVATAR_SIZE)
                and normalized.tobytes() == build_avatar_image().tobytes()
            )
    except OSError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the GitHub profile avatar asset.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the checked-in avatar does not match the deterministic renderer.",
    )
    args = parser.parse_args()

    if args.check:
        if not avatar_is_current():
            print("GitHub profile avatar is missing or stale.")
            sys.exit(1)
        print("GitHub profile avatar matches the deterministic renderer.")
        return

    AVATAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    build_avatar_image().save(AVATAR_PATH, format="PNG", optimize=True)
    print(f"Wrote {AVATAR_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
