# Maati Ra Katha — brand notes

This documents what the site does, as restructured on 29 September 2026. It is the
reference for keeping new pages consistent. Everything visual is defined once in the
`:root` block of `assets/site.css` — change it there, not in individual rules. The
previous system (Cormorant Garamond, Caveat marginalia, text over photographs) is in
`backups/site-2026-09-29/`.

## The idea

**Sarangada lies along one road. Its fields are to the east and its forest to the west.
The sun comes up over the fields and goes down into the forest.**

That is a fact from the Layer 1 research (ISRO Bhuvan data and a resident's description),
marked TRUE in `maati-katha-research/truth-audit.md`, and the whole design hangs on it.
The site is one day crossing the village:

- **The sundial** in the nav is a small arc, W on the left and E on the right, as on a
  north-up map. The sun sits at sunrise when a page opens and sets as you read to the end.
  `sundial()` in `tools/pages.py` draws it; `site.js` moves it.
- **The homepage** walks through four hours — morning (the fields), day (the market road),
  evening (the forest), night — each on its own surface.
- **The east–west drawing** on the homepage is the village as a line: the road, the way in
  from Baliguda, fields east, forest west. Nothing goes on it that has not been mapped.

Do not extend the metaphor past what is true. The hours describe sides of the village and
what is in each photograph; they do not claim a photograph faces east or was taken at dawn.

## Name

**Maati Ra Katha.** *Maati* is soil, and also the place you are from. *Katha* is story.
Written as three words, each capitalised. On the homepage wordmark *Ra* is set in italic
and the accent colour — the one word that joins the soil to the story.

**The Weight of Belonging** is the name of the writing: the journal's title, and the label
on every post. It is not a tagline for the site.

The line under everything is **"No fake experiences. Just life as it is."** — at the top of
every footer.

No Odia text goes on the site that Chandan has not written (`docs/CAPTIONS.md`).

## Mark

A doorway standing on the ground, with the sun rising on its threshold. Unchanged in the
restructure.

- `assets/logo-mark.svg` — 24 viewBox, the drawing of record
- `assets/favicon.svg` — 32 viewBox, laterite tile, for browser tabs
- `assets/favicon-48.png`, `favicon-96.png`, `apple-touch-icon.png` (180×180) — raster fallbacks
- The nav and footer copies are inline, written by `tools/pages.py` (`logo()`), so their
  strokes take `currentColor`. The same drawing marks an empty frame on `days.html`.

Clear space one jamb-width on all sides; minimum 20px on screen; never recolour the sun.

## Colour

The five colours of the place, named once:

| Brand | Value | |
|---|---|---|
| `--laterite` | `#8B3A1F` | wet red soil after the first shower — the accent on paper |
| `--turmeric` | `#C8842B` | late light on a mud wall — the sun, and the accent at night |
| `--sal` | `#2D3B26` | the canopy at noon — in reserve |
| `--ash` | `#EAE3D6` | cooled wood-ash — the second paper |
| `--indigo` | `#1A2130` | the sky after sunset — the ink |

Rules use **roles** (`--paper`, `--ink`, `--ink-2`, `--ink-3`, `--rule`, `--accent`,
`--on-accent`, `--sun`), never a hex, so both themes and every surface hold.

**Surfaces.** Paper by default. Then the hours:

| Class | Light | Dark | |
|---|---|---|---|
| `.hour--morning` | `#E3E4DD` cool ash | `#151A22` | the fields |
| `.hour--day` | paper | paper | the road |
| `.hour--evening` | `#7A3119` laterite dusk, ash ink, turmeric accent | `#3B1A0F` | the forest |
| `.on-night` | `#11161E` | `#0A0D12` | night: the footer, the follow band, the lightbox |

`.on-night` and `.hour--evening` redefine the roles inside them, so any component placed
in one just works. Every text pair is at least 4.5:1; axe-core reports no contrast failure
on any page in either theme. Turmeric on paper is 2.6:1 — never text on a light surface.

The page declares `color-scheme: light dark`. Without it Chrome force-darkens the page.

## Type

Three faces, each with one job. Real `.woff2` files in `assets/fonts/`, latin subsets from
Fontsource, OFL licences beside them. Every page preloads the serif.

| Token | Face | Job |
|---|---|---|
| `--f-display` | Instrument Serif 400, italic | the wordmark, every heading, ledes, pull quotes |
| `--f-body` | Instrument Sans 400 / 500 / 600, italic 400 | reading text, buttons, the nav |
| `--f-mono` | IBM Plex Mono 400 / 500 | **facts**: coordinates, dates, numbers, labels, captions' place and month |

The rule for the mono: if it is something you could check — a coordinate, a date, a count,
a source — it is set in mono. It is the voice of the field record.

Instrument Serif is a display face: big sizes, tight line-height, slight negative tracking.
Never set body text in it.

**Check any replacement font with fontTools before it goes in** — family, weight, that the
letter A is in it. Until 25 Sep 2026 a "600" file had no A–Z and every heading fell back
to Georgia for months. **Nothing may be added to a font stack without shipping the file.**

## Structure

| Page | Holds |
|---|---|
| `index.html` | wordmark, where this stands, east to west, the four hours, the week, the filmstrip, the journal |
| `land.html` | The place: the ground record, four notes, what is not known yet, the land album door |
| `days.html` | The week: the draft note, consent, the seven days |
| `photographs.html` | the archive: album covers in a grid, generated by `tools/photos.py` |
| `journal.html` + `posts/` | The Weight of Belonging |
| `visit.html` | Coming here: checked / not decided, the route, what to know, follow the build |
| `404.html` | for any address that is not a page |

Every page opens on **type** (`.page-head`: a mono kicker, a very large serif title, a
serif lede); the photograph comes after, whole. Every page ends with a link to the next
page along the nav, then the night footer with the manifesto at its top.

All pages share `assets/site.css` and `assets/site.js`. **Keep it that way.**

## Photographs

Shown whole and sharp, with their captions — never blurred, darkened, or with text laid on
top. No rounded corners. The caption sits under the frame; the place and month sit at its
right in mono, and **only when the manifest records them**.

- Page photographs and the hero are `<img>` / `<picture>` elements, not CSS backgrounds.
- The filmstrip keeps each photograph's own shape.
- Every gallery photograph has 540px and 1080px copies, used through `srcset`.
- **Nothing is upscaled.** Video frames at native resolution or not at all.
- **No burnt-in camera text.** Crop it in the manifest's `crop` column; EXIF stripping
  does not remove it. Look at the bottom edge of every image before it goes live.
- An empty frame is allowed; a substitute is not. `days.html` draws a held frame (`.held`)
  where no photograph of that day exists yet.

## Voice

- Say what is true now, including that the pilot is not open. "Where this stands" (home)
  and "Checked / Not decided yet" (`visit.html`) exist for exactly this. A line moves from
  the right column to the left only when the truth audit moves it.
- Short sentences. Concrete nouns — chulha, paddy, borewell, laterite — not "authentic" or
  "immersive". `python tools/pages.py check` fails on the banned words.
- Say what is in the frame. The night section on the homepage says only what its
  photograph shows, and says that it is doing so.
- Never publish a route, a photograph, a sacred or private place, or a host detail before
  it is verified on the ground and consented to.
