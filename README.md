# Maati Ra Katha

**[maatirakatha.com](https://maatirakatha.com/)** — the site of a seven-day village
life-exchange being prepared in Sarangada, Nuagaon Block, Kandhamal, Odisha. It is not
open yet. No fake experiences. Just life as it is.

This repository is the site, the photograph archive behind it, and the notes around them.

## The site

Plain HTML, one stylesheet (`assets/site.css`), two small scripts (`assets/site.js`,
`assets/gallery.js`). No framework, no build step, no npm. GitHub Pages publishes `main`
as it is; `_config.yml` keeps the working files out of what gets published.

| Page | What it is |
|---|---|
| `index.html` | the front door: where this stands, four ways in, the filmstrip, the journal |
| `land.html` | notes from the village |
| `photographs.html` | the archive, in albums |
| `days.html` | what a week there is spent on |
| `journal.html`, `posts/` | the writing |
| `visit.html` | how to reach, and the pilot |

To look at it locally:

```bash
python -m http.server     # then open http://localhost:8000
```

## Photographs

Every caption, consent record, crop and album position lives in `_incoming/manifest.csv`.
The originals never enter git. `tools/photos.py` builds web copies with EXIF and GPS
stripped, and writes the archive into the pages. No face is published before the
person agreed — the render refuses a row with a person in it and no consent.

## Before a commit

```bash
python tools/photos.py render     # the archive, the homepage strip, the photo log
python tools/pages.py sync        # the nav and footer on every page
python tools/pages.py check       # links, anchors, <head>, images, sitemap, journal
python tools/test_photos.py && python tools/test_pages.py
```

The working notes — the rules, how everything fits together, what broke before and why —
are in **`CLAUDE.md`**. The look is in **`docs/BRAND.md`**.

`backups/site-2026-09-25/` is the site exactly as it was before the September 2026
redesign, byte for byte, with instructions for putting it back.
