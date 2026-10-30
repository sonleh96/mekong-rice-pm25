"""Read the two series off the published Fig. 3 image and write them to fig3_digitised.csv.

Axis calibration comes from the tick marks; each observation sits on a fixed 29.2 px step,
four steps per labelled tick. Values are approximate (about +/-0.02 on the y axis).
"""
import csv
import sys
import numpy as np
from PIL import Image

im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
H, W = r.shape
Y0, PX = 610.5, (610.5 - 24) / 4            # y pixel of 0 and pixels per unit, from the y ticks
X0, STEP = 77, (1244 - 77) / 40              # first observation and step, from the x ticks
N = 42

red = (r > 140) & (g < 90) & (b < 110) & (r - g > 80)
blue = (b > 60) & (r < 80) & (g < 110) & (b - r > 30)
legend = np.zeros_like(red); legend[:100, 630:830] = True   # legend samples, top right
red &= ~legend; blue &= ~legend

def centre(mask, x, lo=0, hi=640):
    rows = np.where(mask[lo:hi, x])[0] + lo
    return None if not len(rows) else (rows.min() + rows.max()) / 2

def value(mask, xk, lo=0, hi=640, reach=6):
    """Centre of the line at xk, interpolated from the nearest columns that have pixels."""
    xi = int(round(xk))
    hits = [(x, centre(mask, x, lo, hi)) for x in range(max(xi - reach, 0), min(xi + reach + 1, W))]
    hits = [(x, c) for x, c in hits if c is not None]
    if not hits:
        return None
    left = [h for h in hits if h[0] <= xk]; right = [h for h in hits if h[0] >= xk]
    if left and right:
        (xa, ca), (xb, cb) = left[-1], right[0]
        c = ca if xb == xa else ca + (cb - ca) * (xk - xa) / (xb - xa)
    else:
        c = min(hits, key=lambda h: abs(h[0] - xk))[1]
    return (Y0 - c) / PX

rows = []
for k in range(N):
    xk = X0 + k * STEP
    fire = value(red, xk, lo=400, reach=2)
    pm = value(blue, xk, reach=8)
    rows.append([k, round(xk, 1), None if pm is None else round(pm, 3), None if fire is None else round(max(fire, 0), 3)])

# A sharp peak's centre column sits below its tip by about half the line width; nudge peaks up.
for i in range(1, N - 1):
    f = rows[i][3]
    if f is not None and f > 0.3 and f >= (rows[i - 1][3] or 0) and f >= (rows[i + 1][3] or 0):
        tip = np.where(red[400:640, int(round(rows[i][1]))])[0]
        if len(tip):
            rows[i][3] = round((Y0 - (tip.min() + 400 + 2)) / PX, 3)

# Where a steep segment meets the baseline, the column centre sits above the vertex; read non-peaks from the line's bottom edge.
for i in range(N):
    f = rows[i][3]
    if f is None or (0 < i < N - 1 and f > 0.3 and f >= (rows[i - 1][3] or 0) and f >= (rows[i + 1][3] or 0)):
        continue
    col = np.where(red[400:640, int(round(rows[i][1]))])[0]
    if len(col):
        rows[i][3] = round(max(0, min(f, (Y0 - (col.max() + 400 - 2)) / PX)), 3)

LABELS = {0: '2017-01', 4: '2017-08', 8: '2018-02', 12: '2018-09', 16: '2019-05', 20: '2019-12',
          24: '2020-06', 28: '2021-01', 32: '2021-08', 36: '2022-02', 40: '2022-09'}
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['obs', 'labelled_month', 'log_pm25', 'avg_brightness_temperature'])
    for k, xk, pm, fire in rows:
        w.writerow([k, LABELS.get(k, ''), pm, fire])
print('\n'.join(f'{k:2d} {LABELS.get(k, ""):8s} pm={pm} fire={fire}' for k, xk, pm, fire in rows))
