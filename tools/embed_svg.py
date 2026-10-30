"""Replace a baked SVG in index.html with a freshly built one.

Usage: python3 tools/embed_svg.py fig1-map tools/fig1/fig1_map.svg
       python3 tools/embed_svg.py season-map tools/season_map/season_map.svg

index.html marks each baked SVG with <!-- NAME:start --> and <!-- NAME:end -->.
"""
import re
import sys
from pathlib import Path

name, svg_file = sys.argv[1], sys.argv[2]
page = Path(__file__).resolve().parent.parent / 'index.html'
html = page.read_text()
svg = Path(svg_file).read_text().strip()
html, n = re.subn(rf'<!-- {re.escape(name)}:start -->.*?<!-- {re.escape(name)}:end -->',
                  lambda m: f'<!-- {name}:start -->{svg}<!-- {name}:end -->', html, flags=re.S)
if n != 1:
    raise SystemExit(f'expected one {name} block in index.html, found {n}')
page.write_text(html)
print(f'embedded {svg_file} ({len(svg) / 1000:.0f} kB) as {name}')
