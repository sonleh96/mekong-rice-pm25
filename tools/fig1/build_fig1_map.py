"""Redraw the paper's Fig. 1 (rice areas by crop cycles a year) as a static, theme-aware SVG.

Rice classes are read off the published image at 0.01 degree (about 1 km), using the
transform fitted by georef_any.py; provinces are geoBoundaries (public domain) and
neighbouring countries Natural Earth (public domain).
Usage: python3 build_fig1_map.py  ->  fig1_map.svg
"""
import json
import numpy as np

merc = lambda lat: np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))
from PIL import Image

G = json.load(open('georef_gb.json'))
img_y = lambda lat: G['ty'] - G['sy'] * (merc(lat) if G['mercator'] else lat)

# 1. Classify image pixels by the legend colours.
im = np.asarray(Image.open('fig1.png').convert('RGB')).astype(float)
H, W, _ = im.shape
LEGEND = np.array([[177, 223, 137], [50, 160, 44], [23, 76, 19]], float)
dist = np.linalg.norm(im[..., None, :] - LEGEND[None, None], axis=-1)
cls = np.where(dist.min(-1) < 55, dist.argmin(-1) + 1, 0)
cls[560:920, 960:] = 0                                   # legend

# 2. Majority class per 0.01 degree cell.
STEP = 0.01
LON0, LON1, LAT0, LAT1 = 103.75, 107.65, 8.3, 12.15
lons = np.arange(LON0, LON1, STEP); lats = np.arange(LAT0, LAT1, STEP)
grid = np.zeros((len(lats), len(lons)), int)
for i, la in enumerate(lats):
    y0 = int(img_y(la + STEP)); y1 = int(np.ceil(img_y(la)))
    if y1 < 0 or y0 >= H: continue
    for j, lo in enumerate(lons):
        x0 = int(G['tx'] + G['sx'] * lo); x1 = int(np.ceil(G['tx'] + G['sx'] * (lo + STEP)))
        if x1 < 0 or x0 >= W: continue
        block = cls[max(y0, 0):min(y1, H), max(x0, 0):min(x1, W)].ravel()
        if block.size and (block > 0).mean() >= 0.3:
            grid[i, j] = np.bincount(block[block > 0], minlength=4).argmax()

# Drop one- and two-cell patches: they are boundary lines blended into the green, not plots.
from scipy import ndimage
for c in (1, 2, 3):
    lab_, n = ndimage.label(grid == c)
    sizes = ndimage.sum(np.ones_like(grid), lab_, index=np.arange(1, n + 1))
    grid[np.isin(lab_, np.where(sizes <= 2)[0] + 1)] = 0

# 3. Projection into the SVG frame (Mercator, like the published map).
VW = 560
K = VW / (LON1 - LON0)
MTOP = merc(LAT1)
VH = round((MTOP - merc(LAT0)) * K)
px = lambda lon: (lon - LON0) * K
py = lambda lat: (MTOP - merc(lat)) * K
f1 = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')

# 4. Rice: runs per row, merged downward into taller rectangles where rows repeat.
rects = {1: [], 2: [], 3: []}
open_runs = {}
for i in range(len(lats) - 1, -1, -1):                   # north to south
    row = grid[i]; runs = {}
    j = 0
    while j < len(row):
        c = row[j]
        if c:
            k = j
            while k < len(row) and row[k] == c: k += 1
            runs[(c, j, k)] = True; j = k
        else:
            j += 1
    nxt = {}
    for key in runs:
        top = open_runs.pop(key, lats[i] + STEP)
        nxt[key] = top
    for (c, j, k), top in open_runs.items():
        rects[c].append((lons[j], lons[k - 1] + STEP, top, lats[i] + STEP))
    open_runs = nxt
for (c, j, k), top in open_runs.items():
    rects[c].append((lons[j], lons[k - 1] + STEP, top, LAT0))
def rect_path(rs):
    return ''.join(f'M{f1(px(a))} {f1(py(t))}H{f1(px(b))}V{f1(py(bt))}H{f1(px(a))}Z' for a, b, t, bt in rs)

# 5. Boundaries, simplified with Douglas-Peucker at 0.35 px.
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
            if r[:, 0].max() < LON0 - 1 or r[:, 0].min() > LON1 + 1 or r[:, 1].max() < LAT0 - 1 or r[:, 1].min() > LAT1 + 1: continue
            p = np.column_stack([px(r[:, 0]), py(r[:, 1])])
            p = rdp(p, 0.35)
            if len(p) >= 3:
                out.append('M' + 'L'.join(f'{f1(x)} {f1(y)}' for x, y in p) + 'Z')
    return ''.join(out)

provinces = json.load(open('vn_south_gb.geojson'))['features']
countries = json.load(open('countries.geojson'))['features']
dong_thap = next(f for f in provinces if f['properties']['name'].endswith('ng Tháp'))
neighbours = ''.join(geom_path(f['geometry']) for f in countries if f['properties']['a3'] in ('KHM', 'THA'))
vn = ''.join(geom_path(f['geometry']) for f in provinces)

# 6. Labels and scale bar (lon, lat).
def lab(cls_, x, y, text, anchor='middle', second=None, second_cls=None):
    # A second line is a tspan one line below, so its spacing follows the font size.
    tail = f'<tspan class="{second_cls or cls_}" x="{f1(px(x))}" dy="1.1em">{second}</tspan>' if second else ''
    return f'<text class="{cls_}" x="{f1(px(x))}" y="{f1(py(y))}" text-anchor="{anchor}">{text}{tail}</text>'
km50 = 50 / (111.32 * np.cos(np.radians(8.6)))
sb_x, sb_y = px(103.95), py(8.55)
hcm = (106.70, 10.78)
svg = f'''<svg class="study-svg" viewBox="0 0 {VW} {VH}" role="img" aria-labelledby="study-title study-desc">
<title id="study-title">Rice-growing areas studied, by crop cycles a year</title>
<desc id="study-desc">Map of the Mekong Delta. Rice areas are shaded in three greens for one, two or three crop cycles a year. Three cycles dominate in the east and south-centre, one cycle in the north-west and centre, two cycles in the west and south. Dong Thap province, in the middle of the delta, is hatched: it was left out of the sample.</desc>
<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatch-line"/></pattern><path id="vn-shape" d="{vn}"/></defs>
<path class="nb" d="{neighbours}"/>
<use href="#vn-shape" class="vn"/>
<path class="rice r1" shape-rendering="crispEdges" d="{rect_path(rects[1])}"/>
<path class="rice r2" shape-rendering="crispEdges" d="{rect_path(rects[2])}"/>
<path class="rice r3" shape-rendering="crispEdges" d="{rect_path(rects[3])}"/>
<use href="#vn-shape" class="borders"/>
<path class="excluded" d="{geom_path(dong_thap['geometry'])}"/>
{lab('country', 104.55, 11.55, 'Cambodia')}
{lab('sea', 104.05, 9.15, 'Gulf of', second='Thailand')}
{lab('sea', 107.0, 8.95, 'South China Sea')}
<circle class="city" cx="{f1(px(hcm[0]))}" cy="{f1(py(hcm[1]))}" r="3.5"/>
{lab('place', hcm[0] - 0.05, hcm[1] + 0.1, 'Ho Chi Minh City')}
{lab('place', 105.58, 10.66, 'Dong Thap', second='left out', second_cls='note')}
<g class="scale"><line x1="{f1(sb_x)}" x2="{f1(sb_x + km50 * K)}" y1="{f1(sb_y)}" y2="{f1(sb_y)}"/><line x1="{f1(sb_x)}" x2="{f1(sb_x)}" y1="{f1(sb_y - 4)}" y2="{f1(sb_y + 4)}"/><line x1="{f1(sb_x + km50 * K)}" x2="{f1(sb_x + km50 * K)}" y1="{f1(sb_y - 4)}" y2="{f1(sb_y + 4)}"/><text x="{f1(sb_x + km50 * K / 2)}" y="{f1(sb_y - 8)}" text-anchor="middle">50 km</text></g>
</svg>'''
open('fig1_map.svg', 'w').write(svg)
cells = {c: int((grid == c).sum()) for c in (1, 2, 3)}
print('cells per class', cells, 'rects', {c: len(r) for c, r in rects.items()}, 'svg bytes', len(svg), 'viewBox', VW, VH)
