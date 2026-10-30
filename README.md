# Air pollution and rice crop health: project page

Static project page for Go, Iddawela, Le and Tan, "Air pollution and rice crop health: evidence from Vietnam's Mekong Delta", *Scientific Reports* 16, 34813 (2026), https://doi.org/10.1038/s41598-026-75454-8.
It is one `index.html` with inline CSS and JS, plus `img/` and `fonts/`.
The page loads no scripts from elsewhere; the only outside request is the Inter font from Google Fonts.

## Files

- `index.html` holds the whole page.
  Its numbers come from Tables 1 to 4 of the article and Supplementary Tables A1, A3 and A5.
  The two maps are baked in as inline SVG between `<!-- fig1-map:start -->` and `<!-- season-map:start -->` markers; the diagrams and the Fig. 3 chart are drawn by the page's script.
- `img/fig2-fire-regions.webp` is the article's Fig. 2, fetched by `tools/fetch_figures.py`.
- `img/og.png` is the social card, rendered from `tools/og.html`.
- `fonts/katex/` holds the Computer Modern fonts the diagrams use, from KaTeX 0.16.9 under its MIT licence.
- `tools/` holds the scripts that rebuild the figures; each is described below.
- `.nojekyll` stops GitHub Pages from running Jekyll over the folder.

## Figures and the licence

The article is licensed CC BY-NC-ND 4.0, and the authors hold the copyright.
Fig. 2 is shown exactly as published.
Figs. 1 and 3 are redrawn from the published images, which counts as an adaptation under that licence; the footer says so.
Redrawing them from the underlying data would be more accurate than reading them off the images.

### Fig. 2: fetched

```bash
python3 tools/fetch_figures.py
```

### Fig. 1: study-area map

`tools/fig1/georef_any.py` fits the published map to real coordinates by matching province boundaries to its black lines.
`tools/fig1/build_fig1_map.py` then reads the three rice classes off the image at 0.01 degree, about 1 km, and draws them over the boundaries as SVG.
Provinces are geoBoundaries (gbOpen VNM ADM1, commit 9469f09) and neighbouring countries Natural Earth 10 m, both public domain.

```bash
cd tools/fig1
python3 georef_any.py vn_south_gb.geojson georef_gb.json
python3 build_fig1_map.py
cd ../..
python3 tools/embed_svg.py fig1-map tools/fig1/fig1_map.svg
```

### Fig. 3: fire activity and PM2.5

`tools/fig3/digitise_fig3.py` reads both series off the published chart, accurate to about ±0.03, and writes `fig3_digitised.csv`.
The page's `FIG3` arrays hold the same values; paste them in again after a rerun.
Only the 11 labelled months are known, so the chart's axis counts sample months rather than calendar time.

```bash
cd tools/fig3
python3 digitise_fig3.py fig3.png fig3_digitised.csv
```

### Season map

`tools/season_map/build_season_map.py` bakes the country outlines and labels, downloading Natural Earth 10 m into `tools/.cache` on first run.
The wind dial on the delta is drawn by the page's script, because the season toggle turns it.

```bash
cd tools/season_map
python3 build_season_map.py
cd ../..
python3 tools/embed_svg.py season-map tools/season_map/season_map.svg
```

## Social card

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --window-size=1200,630 --virtual-time-budget=5000 --screenshot=img/og.png tools/og.html
```

## Preview

```bash
python3 -m http.server 8766
```

Then open http://127.0.0.1:8766.

## Address

The canonical link and the `og:url` and `og:image` tags point at https://sonleh96.github.io/mekong-rice-pm25/.
If the page is published under another repository name, update them.
