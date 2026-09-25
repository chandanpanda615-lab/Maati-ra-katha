# Maati Ra Katha — brand notes

This documents what the site does. It is a reference for keeping new pages consistent,
not a rebrand. Everything visual is defined once in the `:root` block of
`assets/site.css` — change it there, not in individual rules. The locked decisions behind
it (name, palette, type, mark) are in `maati-katha-research/Layer_1/brand-identity-master.md`.

## Name

**Maati Ra Katha.** *Maati* is soil, and also the place you are from. *Katha* is story.
`land.html` explains this in its first note, so the name never needs a tagline next to it.
The editorial line is *The Weight of Belonging* — under the wordmark on the homepage, and
in its `<title>`.

Written as three words, each capitalised. Not "MaatiKatha", not all-caps in body text.

## Mark

A doorway standing on the ground, with the sun rising on its threshold.

- `assets/logo-mark.svg` — 24 viewBox, the drawing of record
- `assets/favicon.svg` — 32 viewBox, laterite tile, for browser tabs
- `assets/favicon-48.png`, `favicon-96.png`, `apple-touch-icon.png` (180×180) — raster fallbacks
- The nav and footer copies are inline, written by `tools/pages.py` (`logo()`), so their
  strokes take `currentColor`. Keep the two `.frame` paths and the `.sun` path in step with
  `logo-mark.svg`. The same drawing marks an empty frame on `days.html`.

Rules:

- **Clear space** — one jamb-width (about 1/5 of the mark) on all four sides.
- **Minimum size** — 20px on screen. Below that the arch fills in; use the favicon tile.
- **Do not** recolour the sun, stretch the mark, add a stroke to the sun, or put the
  open-stroke version on a busy photograph. Over imagery, use the laterite tile.

## Two registers

The brand lives in the tension between two surfaces, and the site uses exactly two.

**Paper** — the journal. Chulha ash, indigo ink, laterite for anything that asks to be
clicked. Every page's reading surface in the light theme.

**Night** — the village sky thirty minutes after sunset. The manifesto, the pilot band, the
footer, the lightbox. It is night in both themes; add `.on-night` to a section and every
token inside it flips to ash-on-indigo.

Dark mode turns the paper to night as well, and the accent to turmeric.

## Colour

The five brand colours are named once. Rules use the **roles**, never a hex, so both themes
hold.

| Brand | Value | |
|---|---|---|
| `--laterite` | `#8B3A1F` | wet red soil after the first monsoon shower |
| `--turmeric` | `#C8842B` | late light on a mud wall |
| `--sal` | `#2D3B26` | the canopy at noon — held in reserve |
| `--ash` | `#E8E1D4` | cooled wood-ash, unbleached cotton |
| `--indigo` | `#1F2A3A` | the sky after sunset; `theme-color` is its night shade `#161D28` |

| Role | Light | Dark | Use |
|---|---|---|---|
| `--paper` | `#F2EDE3` | `#11161E` | the page |
| `--paper-2` | ash | `#18202B` | bands: where this stands, the journal band, the consent box |
| `--card` | `#F8F4EC` | `#1B2330` | cards on paper |
| `--ink` / `--ink-2` / `--ink-3` | indigo / `#544C40` / `#6B6254` | ash / `#B8AD99` / `#9C917E` | text, quieter text, captions and dates |
| `--rule`, `--rule-2` | indigo at 14% / 28% | ash at 12% / 26% | hairlines |
| `--accent` | laterite | turmeric | links, labels, the primary button |
| `--night`, `--night-ink` | `#161D28`, `#EAE3D6` | `#0B0F15` | the night register |
| `--sun` | turmeric | turmeric | the logo's sun, the progress line, accents on night |

Every pair above is at least 4.5:1, and axe-core finds no contrast failure on any page in
either theme. Turmeric on paper is 2.6:1 — never use it for text on a light surface.

The page declares `color-scheme: light dark`. Without it Chrome force-darkens the page.
Do not remove it.

## Type

| Token | Face | Use |
|---|---|---|
| `--f-display` | Cormorant Garamond 500 / 600, italic 500 / 600 | the wordmark, every heading, the status line, captions on photographs |
| `--f-body` | the system UI stack | everything else, including labels |
| `--f-hand` | Caveat | **one handwritten line on a page**, as marginalia (`.hand`) |

Small labels above headings (`.label`) are the body face in tracked capitals, not Caveat —
handwriting at 12px read as a scribble.

The faces are real `.woff2` files in `assets/fonts/`, latin subsets from Fontsource, with
their OFL licences beside them. **Check any replacement with fontTools before it goes in**
— family, weight, and that the letter A is in it. Until 25 Sep 2026 the 600 file was a
latin-*extended* subset with no A–Z, so every heading on the site fell back to Georgia and
nobody noticed for months, and the "500" was the Light cut. Every page preloads the 600.

**Nothing may be added to a font stack without shipping the file.** `'Inter'` was named
once with no font behind it, and every line of body text silently fell back.

## Structure

| Page | Holds |
|---|---|
| `index.html` | hero, where this stands, four doors, the filmstrip, the journal, the manifesto |
| `land.html` | the notes, open on the page, and a door into the land album |
| `photographs.html` | the archive: seven albums, generated by `tools/photos.py` |
| `days.html` | the consent box and the seven days, each with a frame |
| `journal.html` + `posts/` | the writing |
| `visit.html` | the route, what to know, the pilot |
| `404.html` | for any address that is not a page |

Every page opens on a photograph (`.page-head`, or `.hero` on the homepage) except a post,
which opens on paper (`.paper-head`, `body.nav-solid`) like the first page of an essay.
Every page ends with a link to the next one along the nav, then the night footer.

All pages share `assets/site.css` and `assets/site.js`. **Keep it that way.**

## Photographs

Shown whole and sharp, with their captions — not blurred and darkened behind text. That
treatment was decoration, and it made the words on top harder to read.

- **Page heads and the hero are `<img>` / `<picture>` elements**, not CSS backgrounds: the
  browser's preload scanner finds them while it reads the HTML, and a `url()` inside a
  custom property can never again be resolved against the wrong file.
- The **filmstrip keeps each photograph's own shape**; nothing is cropped to fit a card.
- **Every gallery photograph has 540px and 1080px copies** (`python tools/photos.py sizes`),
  used through `srcset`. `src` stays the full file — that is what the lightbox shows.
- **Nothing is upscaled.** An earlier pass ran Real-ESRGAN over 1080p video frames; it
  invented detail that was never in the footage. Video frames are published at native
  resolution or not at all.
- **No burnt-in camera text.** Phones stamp names, models and times into the pixels. Crop
  them in the manifest's `crop` column; EXIF stripping does not remove them.
- An empty frame is allowed; a substitute is not. `days.html` draws a held frame where no
  photograph of that day exists yet.

`hero-portrait.jpg` is a **separate photograph**, not a crop of `hero.jpg`. The desktop and
mobile hero captions differ on purpose, and both must stay true to their own frame.

## Voice

Set by the manifesto line on the homepage: **"No fake experiences. Just life as it is."**

- Say what is true now, including that the pilot is not open. "Where this stands" exists
  for exactly this.
- Short sentences. Concrete nouns — chulha, paddy, borewell — not "authentic" or
  "immersive". `python tools/pages.py check` fails on the banned words.
- Never publish a route, a photograph, or a host detail before it is verified on the
  ground and consented to. This is a content rule, not a style one.
