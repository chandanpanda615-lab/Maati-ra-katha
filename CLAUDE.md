# Maati Ra Katha — working notes for Claude

## What this is

A static website for **Maati Ra Katha**: a seven-day village life-exchange in **Sarangada,
Nuagaon Block, Kandhamal, Odisha** (20.227°N, 84.124°E). It is **not open**. Chandan is in
Bangalore finishing CA Final; the village opens to visitors around 2028. Everything built
now is groundwork — the site, the photograph archive, and the writing.

Published at **`https://maatirakatha.com/`** from `main` (GitHub Pages, `CNAME` holds the
apex domain, Enforce HTTPS is on). The repo is `chandanpanda615-lab/Maati-ra-katha`.

The old `chandanpanda615-lab.github.io/life-with-love/` URL is **dead — it 404s**. If you
see `life-with-love` anywhere, it is a bug. `python tools/pages.py check` fails on it.

The site was redesigned on 25 Sep 2026. The version before it is in
`backups/site-2026-09-25/`, byte for byte, with a README on putting it back.

## The rules that are not negotiable

1. **No fake experiences. Just life as it is.** No stock photography, no AI-generated or
   AI-upscaled images, no invented detail. This was already violated once and reverted
   (commit `7f5e922`). Real photograph or an empty frame — never a substitute.
   `days.html` shows the rule: a day with no photograph of it gets an empty, drawn frame.
2. **No face is published before the person agreed.** For children that means the school
   and the family. `tools/photos.py` enforces this: a row with `people=yes` and an empty
   `consent` cell stops the render.
3. **Nothing is bookable and nothing is promised.** Say what is true today, including that
   the pilot is not open.
4. **Originals never enter git.** `_incoming/` is ignored. Only `assets/photos/` (built,
   EXIF-stripped) and `_incoming/manifest.csv` are committed.

And the one under all four: **only publish what is verified.** `maati-katha-research/
truth-audit.md` sorts every claim into TRUE, LIKELY, NOT YET and DO NOT SAY. Two lines on
the site broke it and were changed on 25 Sep: "our turmeric" (Sarangada does not grow it —
see the GI file in `maati-katha-research/02-land/`) and "no wifi after seven" (NOT YET).

## Stack

Plain HTML, one shared CSS file, two small vanilla JS files. **No framework, no build
step, no npm.** This was decided deliberately over a Vite + React rewrite: the problem was
never that HTML cannot hold 100 photos, it was that hand-editing 100 `<figure>` blocks is
unbearable. Generators solved that — `tools/photos.py` for the photographs, `tools/pages.py`
for the parts every page shares. Do not reintroduce a bundler without a concrete reason.

| File | Holds |
|---|---|
| `index.html` | hero, where this stands, four doors, the filmstrip, the journal, the manifesto |
| `land.html` | the four notes, open, and a door into the land album. No gallery of its own |
| `photographs.html` | "Moments and Memories" — seven album covers; click one to open that set |
| `days.html` | the consent box and the seven days, each with a photograph or a held frame. The copy is a **draft** Chandan intends to rewrite in his own words |
| `journal.html` | every post, newest first |
| `posts/*.html` | the posts. On the site template like every other page |
| `visit.html` | the route, what to know, and the pilot (`#interest`, where the nav's Pilot link lands) |
| `404.html` | served by GitHub Pages for any missing path, so every path in it is root-absolute |
| `assets/site.css` | everything visual. Tokens in `:root`; see `docs/BRAND.md` |
| `assets/site.js` | reveal, progress line, nav state, phone menu, filmstrip arrows — every page |
| `assets/gallery.js` | the archive: album bar, lightbox, swipe, `?tag=` filter |
| `assets/fonts/` | real `.woff2`, latin subsets, OFL licences beside them. Never inline them |
| `tools/photos.py` | the whole photo pipeline |
| `tools/pages.py` | the nav and footer (`sync`), and the site check (`check`) |
| `_config.yml` | what GitHub Pages must NOT publish. Without it, `CLAUDE.md` and `docs/` were live |

## The photo pipeline — how to add photographs

Everything flows from **`_incoming/manifest.csv`**. It is the single source of truth for
captions, alt text, consent, crops, sections, tags and notes. Edit the CSV, never the HTML.

```bash
# 1. drop originals into _incoming/<folder>/   (the folder name becomes the default group)
python tools/photos.py sheet      # contact sheets to look through the set
python tools/photos.py manifest   # add rows for new files, keep existing ones
# 2. edit _incoming/manifest.csv — see the columns below
python tools/photos.py build      # web-sized, EXIF/GPS-stripped -> assets/photos/, + sizes + covers
python tools/photos.py render     # writes the archive, the homepage strip, PHOTOS.md
python tools/test_photos.py       # self-check
```

**Look at the bottom edge of every new photograph before publishing it.** Phones burn
text into the pixels: a "Chandan" signature, "MR DEBENDRA" and a date, a "vivo V60 |
ZEISS" bar with the time the photo was taken. EXIF stripping does not touch any of it.
Nine photographs went live with one before 25 Sep. Put the trim in the `crop` column.

`python tools/photos.py sizes` rebuilds the 540px and 1080px copies and the album covers
from what is already in `assets/photos/` — it needs no originals, so it works on any
checkout. The gallery, the strip and the journal cards use them through `srcset`.

### Manifest columns

| Column | Meaning |
|---|---|
| `publish` | `yes` or nothing happens |
| `people` | `yes` if anyone is identifiable |
| `consent` | who agreed. Required when `people=yes` — render refuses otherwise |
| `by` | who took it. Blank means Chandan. Shown as the credit under the caption |
| `slug` | filename in `assets/photos/`, and the `#anchor` on the page |
| `caption` | the line under the photo |
| `alt` | screen-reader text; falls back to `caption` if blank |
| `group` | section on `photographs.html`. **Blank = a page backdrop, not a gallery photo** |
| `span` | `feature` (4×2), `tall` (2×2), `wide` (4×1), or blank for a plain cell |
| `cover` | `yes` makes this photo the album's cover image. One per group |
| `hero` | `yes` builds at 2400px instead of 1600px |
| `crop` | `4%` trims that much off the bottom; `l,t,r,b` is a box in original pixels |
| `tags` | comma separated. `photographs.html?tag=monsoon` shows only those, albums opened |
| `notes` | the long description — raw material for captions and posts |

Section order lives in `GROUPS` at the top of `tools/photos.py`; the homepage filmstrip's
eight photographs, in order, in `STRIP` beside it.

### Generated regions

Nothing between these markers is written by hand. Everything outside them is.

| Markers | In | Written by |
|---|---|---|
| `GALLERY:START` / `GALLERY:END` | `photographs.html`, `docs/PHOTOS.md` | `photos.py render` |
| `STRIP:START` / `STRIP:END` | `index.html` (the filmstrip and its "All N photographs") | `photos.py render` |
| `NAV:START` / `NAV:END`, `FOOT:START` / `FOOT:END` | every page | `pages.py sync` |

The nav and the footer live once, in `NAV`, `FOOT_NAV` and `FOLLOW` at the top of
`tools/pages.py`. Change them there and run `sync`; `check` fails on a page that drifted.
Both generators are idempotent — a second run must change nothing, and the tests check it.

The one photo count that used to be typed by hand (the homepage's "All N photographs",
which drifted to 42 while the archive held 40) is now generated.

## The `<head>` convention — every page

This has broken before. `python tools/pages.py check` now enforces all of it:

- `og:url` and `canonical` → `https://maatirakatha.com/<page>.html`, **apex, no `www.`**
  (`www` 301-redirects, and several unfurlers will not follow a redirect for `og:image`,
  so the photograph silently vanishes from the share card)
- `og:image` / `twitter:image` → `https://maatirakatha.com/assets/...jpg` — **same origin**,
  and the file has to exist. Never `raw.githubusercontent.com`; it serves `text/plain`.
- `<meta name="color-scheme" content="light dark">`, one `<h1>`, a closed `</head>`.

`robots.txt` and `sitemap.xml` sit in the repo root. Add a `<url>` to the sitemap when you
add a page — `check` fails until you do.

## Adding a post

1. Copy `posts/first-post.html` to `posts/<slug>.html` and write in it. Its `<head>` needs
   its own title, description, canonical, `og:*`, date and BlogPosting data.
2. Add a card to `journal.html` (newest first), and put the newest one or two on
   `index.html`.
3. Add the URL to `sitemap.xml`, run `python tools/pages.py sync` (it writes the nav and
   footer into the new page), then `check`.

## Current state (25 Sep 2026)

- **40 photographs** across 7 albums (land 10, village 11, work 1, school 13, festival 1,
  food 1, market 3), all on `photographs.html`. The archive lives there **once**; other
  pages link into it (`photographs.html#slug` opens that photograph in the lightbox).
- The 13 school photographs are live; consent is recorded per row in the manifest.
- The mobile hero (`hero-portrait.jpg`) is a **different photograph** from the desktop one,
  not a crop: women-earth, sorting harvest on red earth. The `<picture>` in `index.html`
  swaps it in on narrow portrait screens, and `.cap-desktop` / `.cap-mobile` swap at the
  same point. Change an image, change its caption. Its manifest row now points at the
  women-earth original; it used to point at the old road crop.
- Footer follow links, YouTube first (docs/SOCIAL.md: it is the main channel): YouTube,
  Instagram, X, email. `sameAs` in the homepage JSON-LD lists the same accounts.
- Homepage weight on a laptop: 1.0 MB (was 3.6 MB). Accessibility: axe-core reports no
  WCAG 2.1 AA violations on any page, in either theme, at 1280px or 390px.
- Video originals, `Village_Image/` and `youtube_assets/` are local only, all gitignored.

### Open questions — not fixed, because only Chandan can answer them

- `land.html` says "Three kilometres east and the floods would reach it." The Layer 1
  research found no flood hazard at any sampled point in Sarangada, but nothing on record
  covers three kilometres east. Verify, or cut the sentence.
- `visit.html` states the languages (Kui in the older Kondh homes, Hindi among the
  young) and the mixed-village description. truth-audit.md marks both LIKELY.
- `days.html` is still the draft.
- `maati-katha-research/` is published on purpose (with `noindex`). It holds a 47 MB video;
  if that page is no longer shared, add the folder to `_config.yml`'s `exclude`.

## Voice

Short sentences. Concrete nouns — chulha, paddy, jharana, borewell, laterite. Never
"authentic", "immersive", "vibrant", "nestled", "hidden gem", "undiscovered", "escape" —
`tools/pages.py check` fails on them. Say what is in the frame.
Full brand reference in **`docs/BRAND.md`**; do not restyle without reading it.
Social — who else is in this space, what earns engagement, and what we post — is in
**`docs/SOCIAL.md`** (measured 4 Aug 2026, $4.18 of Apify runs, re-runnable). The short
version: **YouTube is the main channel, not Instagram** — 15–25 minutes, one named
village, Odia title. `python tools/photos.py captions` turns the manifest into post
drafts in `docs/CAPTIONS.md`; the `/post` skill drafts against the rules in §5.

## Before you commit

```bash
python tools/photos.py render && python tools/pages.py sync   # both must be no-ops if nothing changed
python tools/pages.py check                                    # links, anchors, <head>, images, sitemap, journal, count, voice
python tools/test_photos.py && python tools/test_pages.py      # consent guard, idempotency, and a checker that is proven to fail
git diff --stat
```
