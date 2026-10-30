"""Fit a lon/lat-to-pixel transform for the published Fig. 1 by matching Natural Earth province
boundaries to the black boundary lines in the image (chamfer matching)."""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage, optimize

im = np.asarray(Image.open('fig1.png').convert('RGB')).astype(int)
H, W, _ = im.shape
r, g, b = im[..., 0], im[..., 1], im[..., 2]
lines = (r < 90) & (g < 90) & (b < 90)
lines[560:920, 960:] = False                 # legend
dt = ndimage.distance_transform_edt(~lines)

def rings(geom):
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    for poly in polys:
        for ring in poly:
            yield np.asarray(ring, float)[:, :2]

pts = []
for f in json.load(open(sys.argv[1]))['features']:
    for ring in rings(f['geometry']):
        for a, c in zip(ring[:-1], ring[1:]):
            n = max(1, int(np.hypot(*(c - a)) / 0.005))
            pts.append(a + (c - a) * np.linspace(0, 1, n, endpoint=False)[:, None])
pts = np.vstack(pts)
lon, lat = pts[:, 0], pts[:, 1]
mlat = np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))   # Mercator y, in degree-like units

def project(p, merc):
    sx, sy, tx, ty = p
    return tx + sx * lon, ty - sy * (mlat if merc else lat)

def score(p, merc):
    x, y = project(p, merc)
    ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
    if ok.sum() < 2000:
        return 50.0
    d = np.minimum(dt[y[ok].astype(int), x[ok].astype(int)], 25)
    return d.mean() + 5 * (1 - ok.mean())

best = None
for merc in (False, True):
    for s in np.linspace(250, 360, 23):
        y0 = mlat if merc else lat
        p0 = [s, s, 275 - s * 104.72, 1035 + s * (float(np.degrees(np.log(np.tan(np.pi / 4 + np.radians(8.6) / 2)))) if merc else 8.6)]
        res = optimize.minimize(score, p0, args=(merc,), method='Nelder-Mead', options={'xatol': 0.05, 'fatol': 1e-3, 'maxiter': 3000})
        if best is None or res.fun < best[0]:
            best = (res.fun, merc, res.x)
fun, merc, p = best
print('best score', round(fun, 3), 'mercator' if merc else 'plate carree', [round(v, 3) for v in p])
json.dump({'mercator': bool(merc), 'sx': p[0], 'sy': p[1], 'tx': p[2], 'ty': p[3]}, open(sys.argv[2], 'w'))
