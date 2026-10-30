"""Bake the policy section's season map: country outlines and labels as a static SVG.

The wind dial on the delta is drawn by the page's script on top of this SVG.
Countries are Natural Earth 10 m (public domain), downloaded once into tools/.cache.
Usage: python3 build_season_map.py  ->  season_map.svg
"""
import json
import math
import urllib.request
from pathlib import Path

import numpy as np

CACHE = Path(__file__).resolve().parent.parent / '.cache'
URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_0_countries.geojson'
W, H = 560, 620
LON0, LAT0, LON1, LAT1 = 93, -9, 123, 25                 # the extent the map is fitted to
SOURCES = {'KHM', 'LAO', 'THA', 'MMR', 'MYS', 'IDN'}     # countries with candidate fire regions
DELTA = (105.8, 9.9)
LABELS = [('Myanmar', 96.2, 21.5), ('Laos', 102.6, 19.6), ('Thailand', 100.2, 15.6),
          ('Cambodia', 103.4, 14.2), ('Malaysia', 101.6, 4.6), ('Indonesia', 113.6, -1.2)]

# Mercator fitted to the extent and centred, as d3.geoMercator().fitExtent does.
my = lambda lat: np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
xw, yh = np.radians(LON1 - LON0), my(LAT1) - my(LAT0)
K = min(W / xw, H / yh)
OX = (W - K * xw) / 2 - K * np.radians(LON0)
OY = (H - K * yh) / 2 + K * my(LAT1)
px = lambda lon: OX + K * np.radians(lon)
py = lambda lat: OY - K * my(lat)
f1 = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')

def rdp(p, eps):
    if len(p) < 3: return p
    a, b = p[0], p[-1]; ab = b - a; n = np.hypot(*ab)
    d = np.abs(np.cross(ab, p - a)) / n if n else np.hypot(*(p - a).T)
    i = int(d.argmax())
    return np.vstack([rdp(p[:i + 1], eps)[:-1], rdp(p[i:], eps)]) if d[i] > eps else np.vstack([a, b])

def geom_path(geom):
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    out = []
    for poly in polys:
        for ring in poly:
            r = np.asarray(ring, float)[:, :2]
            if r[:, 0].max() < LON0 - 2 or r[:, 0].min() > LON1 + 2 or r[:, 1].max() < LAT0 - 2 or r[:, 1].min() > LAT1 + 2:
                continue
            p = np.column_stack([px(r[:, 0]), py(r[:, 1])])
            area = 0.5 * abs(np.dot(p[:-1, 0], p[1:, 1]) - np.dot(p[1:, 0], p[:-1, 1]))
            if area < 4:                                 # islands too small to see
                continue
            p = rdp(p, 0.8)
            if len(p) >= 3:
                out.append('M' + 'L'.join(f'{f1(x)},{f1(y)}' for x, y in p) + 'Z')
    return ''.join(out)

def main():
    CACHE.mkdir(exist_ok=True)
    src = CACHE / 'ne_10m_admin_0_countries.geojson'
    if not src.exists():
        urllib.request.urlretrieve(URL, src)
    paths = []
    for f in json.load(open(src))['features']:
        a3, d = f['properties']['ADM0_A3'], geom_path(f['geometry'])
        if d:
            cls = 'land' + (' src' if a3 in SOURCES else '') + (' vn' if a3 == 'VNM' else '')
            paths.append(f'<path class="{cls}" d="{d}"/>')
    labels = ''.join(f'<text class="country on-src" text-anchor="middle" x="{f1(px(lo))}" y="{f1(py(la))}">{n}</text>' for n, lo, la in LABELS)
    cx, cy = px(DELTA[0]), py(DELTA[1])
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-cap" data-cx="{f1(cx)}" data-cy="{f1(cy)}">'
           f'<g class="land-g">{"".join(paths)}</g>'
           f'<g class="marks">{labels}<circle class="delta" cx="{f1(cx)}" cy="{f1(cy)}" r="8"/></g></svg>')
    Path('season_map.svg').write_text(svg)
    print(f'{len(paths)} countries, {len(svg) / 1000:.0f} kB, delta at {cx:.1f},{cy:.1f}')

if __name__ == '__main__':
    main()
