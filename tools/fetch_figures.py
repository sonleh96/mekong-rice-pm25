"""Download the paper's Fig. 2 from Scientific Reports into img/.

Usage:
    python3 tools/fetch_figures.py

The article is licensed CC BY-NC-ND 4.0, so the figures may be shown but not
adapted. This script only converts it to WebP at its published size; it
never crops, recolours or resizes it. Figs. 1 and 3 are redrawn from the
published images by the scripts in tools/fig1 and tools/fig3.

Needs Pillow.
"""
import io
import urllib.request
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "img"
BASE = "https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41598-026-75454-8/MediaObjects/41598_2026_75454_"
FIGURES = {"fig2-fire-regions": "Fig2_HTML.jpg"}


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
