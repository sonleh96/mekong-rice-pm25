"""Download the paper's three figures from Scientific Reports into img/.

Usage:
    python3 tools/fetch_figures.py

The article is licensed CC BY-NC-ND 4.0, so the figures may be shown but not
adapted. This script only converts them to WebP at their published size; it
never crops, recolours or resizes them.

Needs Pillow.
"""
import io
import urllib.request
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "img"
BASE = "https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41598-026-75454-8/MediaObjects/41598_2026_75454_"
FIGURES = {"fig1-study-area": "Fig1_HTML.png", "fig2-fire-regions": "Fig2_HTML.jpg", "fig3-fire-pm25": "Fig3_HTML.png"}


def main():
    OUT.mkdir(exist_ok=True)
    for name, remote in FIGURES.items():
        with urllib.request.urlopen(BASE + remote) as r:
            im = Image.open(io.BytesIO(r.read()))
            im.load()
        im.convert("RGB").save(OUT / f"{name}.webp", quality=90, method=6)
        print(f"{name}.webp {im.width}x{im.height}")


if __name__ == "__main__":
    main()
