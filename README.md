# Air pollution and rice crop health: project page

Static project page for Go, Iddawela, Le and Tan, "Air pollution and rice crop health: evidence from Vietnam's Mekong Delta", *Scientific Reports* 16, 34813 (2026), https://doi.org/10.1038/s41598-026-75454-8.
It is one `index.html` with inline CSS and JS, an `img/` folder, and no build step.

## Files

- `index.html` holds the whole page.
  Its numbers come from Tables 1 to 4 of the article and Supplementary Tables A1, A3 and A5.
- `img/fig1-study-area.webp`, `img/fig2-fire-regions.webp` and `img/fig3-fire-pm25.webp` are the article's Figs. 1 to 3, fetched by `tools/fetch_figures.py`.
- `img/og.png` is the social card, rendered from `tools/og.html`.
- `.nojekyll` stops GitHub Pages from running Jekyll over the folder.

## Figures and the licence

The article is licensed CC BY-NC-ND 4.0.
The page may show its figures with credit and a licence link, but it may not share adapted versions.
The script therefore only converts the figures to WebP at their published size, and the page shows them on white in both themes.
A restyled figure has to be drawn from the underlying data, not from the published image.

```bash
python3 tools/fetch_figures.py
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
