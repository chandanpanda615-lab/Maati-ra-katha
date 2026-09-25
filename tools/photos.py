#!/usr/bin/env python3
"""Photo intake for Maati Katha. Standard library + Pillow, nothing else.

Drop originals in _incoming/ (gitignored), then:

    python tools/photos.py sheet    # contact sheets, so the whole set can be looked at
    python tools/photos.py manifest # write/refresh _incoming/manifest.csv
    python tools/photos.py build    # web-sized, EXIF-stripped copies -> assets/photos/
                                    #   (+ the small sizes and album covers made from them)
    python tools/photos.py sizes    # only the small sizes and covers — needs no originals
    python tools/photos.py render   # manifest -> the archive, the homepage strip, PHOTOS.md
    python tools/photos.py captions # manifest -> docs/CAPTIONS.md, one post draft per photo

Originals never enter git. Only what build/ produces is committed — plus manifest.csv,
which is the one file carrying every caption and consent record.
"""
import csv, html, os, re, sys, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_incoming"
SHEETS = SRC / "_sheets"
OUT = ROOT / "assets" / "photos"
COVERS = ROOT / "assets" / "covers"
MANIFEST = SRC / "manifest.csv"

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".wmv", ".mkv", ".3gp"}

COLS, ROWS, THUMB = 5, 4, 380          # 20 per sheet
WEB_MAX = 1600                          # longest edge of a published photo
HERO_MAX = 2400                         # the one photo marked hero=yes goes bigger
WEB_QUALITY = 82
# An album cover is a banner about 210px tall that every visitor downloads before
# they have opened anything. Serving the full 1600px gallery photo for that meant
# seven covers weighed 2.2 MB and pushed LCP to 11s on a slow connection. The cover
# is a separate, smaller derivative for exactly that reason.
COVER_MAX = 1000
COVER_QUALITY = 68
# Smaller copies of every gallery photograph, long edge in pixels, each in its own
# folder: assets/photos/540/terraces.jpg. The homepage strip showed 1600px files in
# 300px frames — 2.6 MB of a 3.6 MB page — because nothing smaller existed. With these
# in the srcset the browser takes the smallest that is sharp at the size on screen,
# and the full file is only fetched for a big screen, or the lightbox.
# They are made from the built photo, not the original, so they can be rebuilt on any
# clean checkout: `python tools/photos.py sizes`.
SIZES = {540: 76, 1080: 78}             # long edge -> JPEG quality

# The homepage filmstrip, in order. A teaser that links into the archive, not a
# second gallery — every frame opens that photograph on photographs.html. Captions,
# alt text and the "All N photographs" count come from the manifest, so none of it
# can drift from the archive the way the hand-written count once did (42 against 40).
STRIP = ["terraces", "paddy-plain", "cattle-hill", "tank-railing",
         "bike-dusk", "market-hills", "thali", "fire-night"]

FIELDS = ["file", "publish", "consent", "people", "by", "slug", "caption", "alt", "place",
          "when", "group", "span", "cover", "hero", "crop", "tags", "notes"]

# Section order on photographs.html. A group named in the manifest but missing here
# lands in "rest" at the end, so a typo loses the section heading, never the photo.
# A row with a BLANK group is a page image (hero.jpg, land.jpg, road.jpg) — published,
# but it belongs to a backdrop, not to the gallery, so it is skipped entirely.
GROUPS = [
    ("land",     "The land",      "Soil, hills, water, and what the monsoon does to all three."),
    ("village",  "The village",   "The ground, the road, the evenings. Where the day ends up."),
    ("work",     "Work",          "Paddy, harvest, firewood. What the day is actually spent on."),
    ("school",   "The school",    "The blackboard, the mid-day meal, and the break in between."),
    ("festival", "Festival",      "The pandal, the flag, the days the village stops."),
    ("food",     "Food",          "Rice, dal, greens, and a chulha that is lit before you wake."),
    ("jungle",   "Jungle & jharana", "The forest behind the village, and the streams inside it."),
    ("market",   "The market",    "The road, the shopfronts, and the haat when it comes."),
    ("rest",     "Everything else", "Photographs that do not sit in one of the sets above."),
]

MARK_START = "<!-- GALLERY:START"
MARK_END = "<!-- GALLERY:END -->"
STRIP_START = "<!-- STRIP:START"
STRIP_END = "<!-- STRIP:END -->"

# `sizes` for a gallery cell, matching .gallery-grid in site.css: six columns inside a
# 1180px column with a 48px gutter, one column under 700px. A plain or tall cell spans
# two columns (~385px), a wide or feature cell four (~785px). Change the grid, change these.
CELL_SIZES = {
    "narrow": "(max-width: 700px) calc(100vw - 2.5rem), (max-width: 1276px) 30vw, 385px",
    "broad":  "(max-width: 700px) calc(100vw - 2.5rem), (max-width: 1276px) 62vw, 785px",
}

# Hashtag reach, measured 4 Aug 2026 — docs/SOCIAL.md §3 has the numbers. Tags under
# about 5k posts are dead ends (#ruralodisha has 1,270 posts, #ruraltourismindia 890);
# tags over about 5m are noise to vanish into. These sit in between, and every one of
# them is true of where we actually are. #daringbadi is deliberately absent: it is the
# tourist name in this district, it would pull traffic, and we are not there.
CORE_TAGS = ["sarangada", "kandhamal", "phulbani", "odishatourism",
             "odisha", "adivasi", "ruraltourism", "villagetourism"]


def scan():
    """Every file under _incoming/, split into photos and videos. Sorted, so the
    index printed on a contact sheet is stable between runs."""
    photos, videos = [], []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file() or SHEETS in p.parents:
            continue
        ext = p.suffix.lower()
        if ext in PHOTO_EXT:
            photos.append(p)
        elif ext in VIDEO_EXT:
            videos.append(p)
    return photos, videos


def cmd_sheet():
    photos, videos = scan()
    if not photos:
        sys.exit(f"No photos in {SRC}. Put the originals there first.")
    SHEETS.mkdir(parents=True, exist_ok=True)
    for old in SHEETS.glob("sheet-*.jpg"):
        old.unlink()

    per = COLS * ROWS
    made = 0
    for start in range(0, len(photos), per):
        batch = photos[start:start + per]
        W, H = COLS * THUMB, ROWS * (THUMB + 26)
        sheet = Image.new("RGB", (W, H), (28, 24, 20))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            try:
                im = Image.open(path)
                im.draft("RGB", (THUMB * 2, THUMB * 2))   # fast JPEG downscale
                im = ImageOps.exif_transpose(im)          # phone shots carry orientation=6
                im = im.convert("RGB")
            except Exception as e:                        # unreadable file: leave a marker
                im = Image.new("RGB", (THUMB, THUMB), (60, 30, 30))
                ImageDraw.Draw(im).text((8, 8), f"unreadable\n{e}"[:120], fill=(255, 200, 200))
            im.thumbnail((THUMB - 8, THUMB - 8), Image.LANCZOS)
            cx, cy = (i % COLS) * THUMB, (i // COLS) * (THUMB + 26)
            sheet.paste(im, (cx + (THUMB - im.width) // 2, cy + (THUMB - 8 - im.height) // 2 + 4))
            draw.text((cx + 6, cy + THUMB + 4), f"{start + i:03d}  {path.name[:34]}", fill=(210, 200, 185))
        out = SHEETS / f"sheet-{start // per:02d}.jpg"
        sheet.save(out, quality=78, optimize=True)
        made += 1
        print(f"  {out.relative_to(ROOT)}  ({len(batch)} photos)")

    print(f"\n{len(photos)} photos across {made} contact sheet(s).")
    if videos:
        total = sum(v.stat().st_size for v in videos) / 1048576
        print(f"{len(videos)} video(s), {total:.0f} MB total — these do NOT go in git. See the README note.")


def cmd_manifest():
    """One row per photo. Nothing is published until `publish` says yes, which
    keeps the site's own consent rule enforceable rather than aspirational."""
    photos, _ = scan()
    existing = {}
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8", newline="") as f:
            existing = {r["file"]: r for r in csv.DictReader(f)}

    rows = []
    for i, p in enumerate(photos):
        rel = str(p.relative_to(SRC)).replace("\\", "/")
        row = existing.get(rel, {})
        # The folder a photo was dropped into is the best first guess at its group,
        # so sorting 100 files into sections is mostly a matter of where they landed.
        default_group = rel.split("/")[0] if "/" in rel else ""
        rows.append({
            "file": rel,
            "publish": row.get("publish", "no"),
            "consent": row.get("consent", ""),      # who agreed, if a person is in it
            "people": row.get("people", ""),        # yes if anyone is identifiable in it
            # Who took it. Blank means Chandan. Once other people in the village are
            # shooting for this, the credit has to live with the photograph — not in
            # somebody's memory, and never cropped off a corner.
            "by": row.get("by", ""),
            "slug": row.get("slug", f"photo-{i:03d}"),
            "caption": row.get("caption", ""),
            "alt": row.get("alt", ""),          # falls back to caption when left blank
            "place": row.get("place", ""),
            "when": row.get("when", ""),
            "group": row.get("group", default_group),   # section on photographs.html
            "span": row.get("span", ""),        # feature | tall | wide, or blank for a plain cell
            "cover": row.get("cover", ""),      # yes = this photo is the album's cover
            "hero": row.get("hero", "no"),      # exactly one row says yes; it builds at HERO_MAX
            "crop": row.get("crop", ""),        # see parse_crop: "4%" or "l,t,r,b", blank = none
            "tags": row.get("tags", ""),        # comma separated; drives ?tag= and "also"
            "notes": row.get("notes", ""),      # the long description, raw material for posts
        })
    # Write a sibling file and swap it in. Opening the manifest itself with "w"
    # truncates it before the write, so any error mid-write destroys every caption
    # and consent record in it. That has happened. Do not go back to the simple form.
    fd, tmp = tempfile.mkstemp(dir=str(MANIFEST.parent), suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        # "\n", not the csv module's default "\r\n": the committed file is LF, and a CRLF
        # rewrite turns a one-cell edit into a 103-line diff that hides what changed.
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, MANIFEST)
    kept = sum(1 for r in rows if r["publish"].strip().lower() == "yes")
    print(f"{MANIFEST.relative_to(ROOT)}: {len(rows)} rows, {kept} marked publish=yes")
    print("Edit it, set publish=yes on the ones you want, then run: python tools/photos.py build")


def parse_crop(value, size):
    """A `crop` cell -> a PIL box, or None. Originals are never edited; the crop is
    recorded here so the same build runs again on a clean checkout.

    Two forms, because there are two problems:
      "4%"              trim that much off the bottom. Several friends' cameras burn
                        "MR DEBENDRA <date>" into the bottom edge. The depth is not a
                        constant fraction across phones, so it is measured per photo.
      "0,657,1080,1195" an explicit left,top,right,bottom box. The two sunsets Ananta
                        sent are letterboxed screenshots — the photograph is a band in
                        the middle and the padding carries a Meta AI badge.
    """
    value = (value or "").strip()
    if not value:
        return None
    w, h = size
    if value.endswith("%"):
        pct = float(value[:-1])
        if not 0 < pct < 50:
            raise ValueError(f"crop {value!r}: percentage must be between 0 and 50")
        return (0, 0, w, h - int(round(h * pct / 100)))
    parts = [int(n) for n in value.split(",")]
    if len(parts) != 4:
        raise ValueError(f"crop {value!r}: want '<pct>%' or 'left,top,right,bottom'")
    left, top, right, bottom = parts
    # A typo here silently produces a sliver or an empty image, and the only place it
    # would show up is the live site. Fail on the spot instead.
    if not (0 <= left < right <= w and 0 <= top < bottom <= h):
        raise ValueError(f"crop {value!r}: box outside the {w}x{h} original")
    return (left, top, right, bottom)


def cmd_build():
    if not MANIFEST.exists():
        sys.exit("No manifest yet. Run: python tools/photos.py manifest")
    OUT.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["publish"].strip().lower() == "yes"]
    if not rows:
        sys.exit("Nothing marked publish=yes in the manifest.")

    total = skipped = 0
    for r in rows:
        src = SRC / r["file"]
        if not src.exists():
            print(f"  MISSING {r['file']}")
            continue
        # A blank group means this is a page backdrop (hero.jpg, land.jpg, road.jpg),
        # which site.css loads from assets/ — not a gallery photo. Writing it straight
        # to its real home removes a manual copy step that was easy to forget.
        dst = (ROOT / "assets" if not r.get("group", "").strip() else OUT) / f"{r['slug']}.jpg"
        # Re-encoding a hundred unchanged photos on every run buys nothing. Delete the
        # built file (or touch the original) to force one.
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            skipped += 1
            total += dst.stat().st_size / 1024
            continue
        im = Image.open(src)
        # Rotate upright while the orientation tag still exists — the repaste below
        # drops all EXIF, so doing this afterwards would lose the tag unread.
        im = ImageOps.exif_transpose(im).convert("RGB")
        # Crop before the resize, so the number in the manifest means original pixels
        # and stays correct if WEB_MAX ever changes.
        try:
            box = parse_crop(r.get("crop", ""), im.size)
        except ValueError as e:
            sys.exit(f"{r['file']}: {e}")
        if box:
            im = im.crop(box)
        max_edge = HERO_MAX if r.get("hero", "").strip().lower() == "yes" else WEB_MAX
        im.thumbnail((max_edge, max_edge), Image.LANCZOS)
        clean = Image.new("RGB", im.size)     # new image => EXIF, incl. GPS, is dropped
        clean.paste(im)
        # dst was already decided above — a blank group sends the file to assets/ as a
        # page backdrop. Recomputing it here as OUT sent hero.jpg to assets/photos/.
        clean.save(dst, quality=WEB_QUALITY, optimize=True, progressive=True)
        kb = dst.stat().st_size / 1024
        total += kb
        print(f"  {dst.name:28s} {im.width}x{im.height}  {kb:6.0f} KB")
    print(f"\n{len(rows)} photos -> {OUT.relative_to(ROOT)}, {total/1024:.1f} MB total")
    build_covers(rows)
    build_sizes(rows)
    print("These are the only image files that belong in a commit.")


def cmd_sizes():
    """The small sizes and the album covers, made from what is already in assets/photos/.
    Needs no originals — this is what to run on a checkout that has none."""
    if not MANIFEST.exists():
        sys.exit("No manifest yet. Run: python tools/photos.py manifest")
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["publish"].strip().lower() == "yes"]
    build_covers(rows)
    build_sizes(rows)


def published():
    """Manifest rows marked publish=yes, with the consent rule enforced rather than
    hoped for. The site promises "no face published without the person agreeing to it
    first" — so a row with a person in it and an empty consent cell stops the render."""
    if not MANIFEST.exists():
        sys.exit("No manifest yet. Run: python tools/photos.py manifest")
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("publish", "").strip().lower() == "yes"]

    unconsented = [r for r in rows
                   if r.get("people", "").strip().lower() == "yes"
                   and not r.get("consent", "").strip()]
    if unconsented:
        print("Refusing to render. These rows have a person in the frame and no consent:\n")
        for r in unconsented:
            print(f"  {r['file']}  (slug: {r.get('slug', '?')})")
        sys.exit("\nFill the consent column, or set publish=no. This rule is the site's own.")
    return rows


def replace_between(text, start_mark, end_mark, body, what):
    """Swap only what sits between the two markers. Everything a human wrote around
    them survives untouched, which is what makes re-running this safe."""
    pat = re.compile(re.escape(start_mark) + r".*?" + re.escape(end_mark), re.S)
    if not pat.search(text):
        sys.exit(f"No {start_mark} ... {end_mark} block in {what}. Add the markers first.")
    return pat.sub(lambda _: body, text, count=1)


def tidy_tags(raw):
    """Lower-case, comma-separated, no duplicates, order kept. Typing "Children, food"
    and "children,Food" in two rows should not make two different tags."""
    seen, out = set(), []
    for t in raw.split(","):
        t = " ".join(t.split()).lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return ",".join(out)


def cover_picks(rows):
    """{group key: row} — the photograph that fronts each album. cover=yes wins,
    otherwise the first in the set. build writes a small derivative for exactly
    these and render points the covers at them, so the two must not drift."""
    known = {g for g, _, _ in GROUPS}
    gallery = [r for r in rows if r.get("group", "").strip()]
    picks = {}
    for key, _, _ in GROUPS:
        if key == "rest":
            batch = [r for r in gallery if r.get("group", "").strip().lower() not in known]
        else:
            batch = [r for r in gallery if r.get("group", "").strip().lower() == key]
        if batch:
            picks[key] = next(
                (r for r in batch if r.get("cover", "").strip().lower() == "yes"), batch[0])
    return picks


def build_covers(rows):
    """Small banner versions of the album covers. Every visitor downloads these
    before opening anything, so they are the one set of images that has to be
    cheap."""
    COVERS.mkdir(parents=True, exist_ok=True)
    made = total = 0
    for r in cover_picks(rows).values():
        src = OUT / f"{r['slug']}.jpg"
        if not src.exists():
            continue
        dst = COVERS / f"{r['slug']}.jpg"
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            total += dst.stat().st_size / 1024
            continue
        im = Image.open(src)
        im.thumbnail((COVER_MAX, COVER_MAX), Image.LANCZOS)
        im.save(dst, quality=COVER_QUALITY, optimize=True, progressive=True)
        kb = dst.stat().st_size / 1024
        total += kb
        made += 1
        print(f"  cover  {dst.name:24s} {im.width}x{im.height}  {kb:6.0f} KB")
    print(f"  {len(cover_picks(rows))} covers, {total:.0f} KB total ({made} rebuilt)")


def build_sizes(rows):
    """assets/photos/<edge>/<slug>.jpg for every gallery photograph and every edge in
    SIZES that is smaller than the photograph itself. A size that would not be smaller
    is skipped rather than written: re-encoding a 1080px file at 1080px only loses detail."""
    made = total = 0
    for r in rows:
        if not r.get("group", "").strip():
            continue                     # page backdrops live in assets/, not the gallery
        src = OUT / f"{r['slug']}.jpg"
        if not src.exists():
            continue
        with Image.open(src) as full:
            long_edge = max(full.size)
        for edge, quality in SIZES.items():
            if edge >= long_edge:
                continue
            dst = OUT / str(edge) / f"{r['slug']}.jpg"
            if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                total += dst.stat().st_size / 1024
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            im = Image.open(src)
            im.thumbnail((edge, edge), Image.LANCZOS)
            im.save(dst, quality=quality, optimize=True, progressive=True)
            total += dst.stat().st_size / 1024
            made += 1
    print(f"  sizes  {', '.join(str(e) for e in SIZES)}px: {total / 1024:.1f} MB total ({made} rebuilt)")


def srcset(slug, prefix="assets/photos/"):
    """Every size of one photograph that exists, smallest first, then the full file:
    'assets/photos/540/x.jpg 540w, assets/photos/1080/x.jpg 1080w, assets/photos/x.jpg 1600w'.
    Widths are read off the files, so a portrait's 540px size is correctly '304w'."""
    parts = []
    for edge in sorted(SIZES):
        p = OUT / str(edge) / f"{slug}.jpg"
        if p.exists():
            with Image.open(p) as im:
                parts.append(f"{prefix}{edge}/{slug}.jpg {im.size[0]}w")
    with Image.open(OUT / f"{slug}.jpg") as im:
        parts.append(f"{prefix}{slug}.jpg {im.size[0]}w")
    return ", ".join(parts)


def figure(r, i):
    """One gallery cell. width/height come off the built file: without them a
    hundred lazy images collapse the page height and every scroll jumps."""
    src = OUT / f"{r['slug']}.jpg"
    if not src.exists():
        sys.exit(f"{src.relative_to(ROOT)} is missing. Run: python tools/photos.py build")
    with Image.open(src) as im:
        w, h = im.size
    span = r.get("span", "").strip().lower()
    cls = "photo-card" + (f" photo-card--{span}" if span in {"feature", "tall", "wide"} else "")
    sizes = CELL_SIZES["broad" if span in {"feature", "wide"} else "narrow"]
    cap = html.escape(r.get("caption", "").strip())
    alt = html.escape((r.get("alt") or r.get("caption", "")).strip())
    by = html.escape(r.get("by", "").strip())
    credit = f'<small class="credit">{by}</small>' if by else ""
    delay = min(0.06 + i * 0.04, 0.34)      # stagger the first few, then stop waiting
    tags = html.escape(tidy_tags(r.get("tags", "")))
    # The id makes every photograph addressable — photographs.html#school-meal opens
    # straight into it, so a written piece can point at one frame. src stays the full
    # file: that is what the lightbox shows, whichever size the cell happened to load.
    # The photograph sits in a real <button>, which answers to Enter and Space and is
    # announced as one. It used to be role="button" on the <figure>, which ARIA does not
    # allow on that element, and which needed a keydown handler to pretend to be a button.
    return (
        f'      <figure id="{r["slug"]}" class="{cls} reveal" style="--d:{delay:.2f}s"\n'
        f'              data-tags="{tags}">\n'
        f'        <button class="photo-open" type="button" aria-label="Open photograph: {cap}">\n'
        f'          <img src="assets/photos/{r["slug"]}.jpg" alt="{alt}"\n'
        f'               srcset="{srcset(r["slug"])}"\n'
        f'               sizes="{sizes}"\n'
        f'               width="{w}" height="{h}" loading="lazy" decoding="async">\n'
        f'        </button>\n'
        f'        <figcaption>{cap}{credit}</figcaption>\n'
        f'      </figure>'
    )


def strip_frame(r):
    """One frame of the homepage strip. Frames keep the photograph's own shape — a
    panorama is wide, a portrait is narrow — so the strip never crops what is in them.
    Their height is clamp(180px, 26vw, 300px) in site.css (.strip-frame img), so the
    width on screen is that height times the aspect ratio; `sizes` says exactly that."""
    slug = r["slug"]
    with Image.open(OUT / f"{slug}.jpg") as im:
        w, h = im.size
    a = w / h
    sizes = (f"(max-width: 692px) {round(180 * a)}px, "
             f"(max-width: 1153px) {26 * a:.1f}vw, {round(300 * a)}px")
    cap = html.escape(r.get("caption", "").strip())
    alt = html.escape((r.get("alt") or r.get("caption", "")).strip())
    return (
        f'      <a class="strip-frame" href="photographs.html#{slug}">\n'
        f'        <img src="assets/photos/{slug}.jpg" alt="{alt}"\n'
        f'             srcset="{srcset(slug)}"\n'
        f'             sizes="{sizes}"\n'
        f'             width="{w}" height="{h}" loading="lazy" decoding="async">\n'
        f'        <span class="strip-cap">{cap}</span>\n'
        f'      </a>'
    )


def cmd_render():
    # A blank group means the photo is a page backdrop, not a gallery cell.
    rows = [r for r in published() if r.get("group", "").strip()]
    note = f"{MARK_START} — generated by tools/photos.py render. Do not edit by hand. -->"

    # --- photographs.html: every published photo, in labelled sections -------------
    known = {g for g, _, _ in GROUPS}
    picks = cover_picks(rows)
    sections = []
    album_index = []          # (key, title, count) for the bar at the top of the page
    for key, title, blurb in GROUPS:
        if key == "rest":
            batch = [r for r in rows if r.get("group", "").strip().lower() not in known]
        else:
            batch = [r for r in rows if r.get("group", "").strip().lower() == key]
        if not batch:
            continue
        cells = "\n".join(figure(r, i) for i, r in enumerate(batch))
        # A closed <details> is the whole point — the page is seven covers until
        # something is opened, so there is nothing to scroll past. The cover image is
        # the small derivative from assets/covers/, not the full gallery photo.
        pick = picks[key]
        n = len(batch)
        album_index.append((key, title, n))
        # The cover is an <img>, not an inline background-image: lazy covers below the
        # fold wait until they are near, and the shade over the photograph is in CSS
        # (.album-cover::after) where it can follow the theme. alt is empty on purpose —
        # the title right beside it already says what the album is.
        cover = COVERS / f"{pick['slug']}.jpg"
        cw, ch = Image.open(cover).size if cover.exists() else (1000, 562)
        lazy = "" if not sections else ' loading="lazy"'
        sections.append(
            f'  <details class="album" id="{key}">\n'
            f'    <summary class="album-cover">\n'
            f'      <img class="album-img" src="assets/covers/{pick["slug"]}.jpg" alt=""\n'
            f'           width="{cw}" height="{ch}"{lazy} decoding="async">\n'
            f'      <span class="album-eyebrow">{n} photograph{"s" if n != 1 else ""}</span>\n'
            f'      <span class="album-title">{title}</span>\n'
            f'      <span class="album-sub">{blurb}</span>\n'
            f'      <span class="album-cue" aria-hidden="true"></span>\n'
            f'    </summary>\n'
            f'    <div class="gallery-grid inner">\n{cells}\n    </div>\n'
            f'  </details>'
        )
    # The bar names the albums, not the tags. It listed tags until "red earth",
    # "indoors" and "monsoon" ended up sitting directly above "The land" — two
    # different ways of cutting the same 29 photographs, stacked on top of each
    # other. Naming the albums makes the bar a table of contents: one entry per
    # set below it, and clicking an entry opens that set.
    #
    # href is a real "#key" fragment so it still jumps with JavaScript off; the
    # opening is done in gallery.js, which is also what closes the other albums.
    chips = "".join(
        f'      <a class="tag-chip" href="#{key}" data-album="{key}">'
        f'{html.escape(title)} <small>{n}</small></a>\n' for key, title, n in album_index)
    tagbar = ('  <nav class="tag-bar inner reveal" aria-label="Jump to an album">\n'
              '      <a class="tag-chip tag-all is-on" href="#" data-album="">everything '
              f'<small>{len(rows)}</small></a>\n{chips}  </nav>') if album_index else ""

    archive = ROOT / "photographs.html"
    text = archive.read_text(encoding="utf-8")
    body = note + "\n" + tagbar + "\n" + "\n\n".join(sections) + "\n  " + MARK_END
    archive.write_text(replace_between(text, MARK_START, MARK_END, body, archive.name),
                       encoding="utf-8")
    print(f"  photographs.html   {len(rows)} photographs in {len(sections)} section(s)")

    # --- index.html: the filmstrip, and the count at the end of it --------------------
    by_slug = {r["slug"]: r for r in rows}
    missing = [s for s in STRIP if s not in by_slug]
    if missing:
        sys.exit(f"STRIP names photographs that are not published: {', '.join(missing)}")
    frames = "\n".join(strip_frame(by_slug[s]) for s in STRIP)
    more = ('      <a class="strip-more" href="photographs.html">\n'
            f'        <span class="strip-more-n">All {len(rows)} photographs</span>\n'
            '        <span class="strip-more-go" aria-hidden="true">&rarr;</span>\n'
            '      </a>')
    home = ROOT / "index.html"
    body = (f"{STRIP_START} — generated by tools/photos.py render from STRIP. Do not edit by hand. -->\n"
            f"{frames}\n{more}\n      {STRIP_END}")
    home.write_text(replace_between(home.read_text(encoding="utf-8"),
                                    STRIP_START, STRIP_END, body, home.name), encoding="utf-8")
    print(f"  index.html         {len(STRIP)} frames in the strip, count {len(rows)}")

    # land.html deliberately has no gallery. A curated copy of the archive put eight
    # photographs on two pages at once; one photograph belongs in exactly one place.

    # --- PHOTOS.md: the log, below whatever preamble is written above the marker ----
    # Moved under docs/ with the other notes; keep working if it is still at the root.
    log = next((p for p in (ROOT / "docs" / "PHOTOS.md", ROOT / "PHOTOS.md") if p.exists()),
               ROOT / "docs" / "PHOTOS.md")
    lines = ["<!-- GALLERY:START — generated by tools/photos.py render. Do not edit by hand. -->",
             "", "| slug | caption on site | place · when | notes |", "|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r.get("group", ""), r.get("slug", ""))):
        when = " · ".join(x for x in (r.get("place", "").strip(), r.get("when", "").strip()) if x)
        cells_md = [r.get("slug", ""), r.get("caption", ""), when, r.get("notes", "").strip()]
        if r.get("consent", "").strip():
            cells_md[3] = (cells_md[3] + " " if cells_md[3] else "") + f"Consent: {r['consent'].strip()}."
        lines.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells_md) + " |")
    lines += ["", MARK_END]
    log.write_text(replace_between(log.read_text(encoding="utf-8"),
                                   MARK_START, MARK_END, "\n".join(lines), log.name),
                   encoding="utf-8")
    print(f"  PHOTOS.md          {len(rows)} rows")
    print("\nRun it again — the files should not change. That is the check.")


def cmd_captions():
    """manifest.csv -> docs/CAPTIONS.md, one draft per published gallery photograph.

    It fills in only what is already recorded: the place, the date, the caption that is
    on the site, the notes, the tags. The caption line, the question and the Odia are
    left blank on purpose. A script writing a sentence about a village it has never seen
    is the same failure as a stock photograph — rule 1 in CLAUDE.md. Claude drafts EN
    and Q from the notes (see /post); Chandan writes the Odia."""
    rows = [r for r in published() if r.get("group", "").strip()]
    order = {g: i for i, (g, _, _) in enumerate(GROUPS)}
    rows.sort(key=lambda r: (order.get(r.get("group", "").strip().lower(), len(order)),
                             r.get("slug", "")))

    out = ["# Captions — drafts",
           "",
           "Generated by `python tools/photos.py captions` from `_incoming/manifest.csv`.",
           "Do not hand-edit: the next run overwrites it. Fix the manifest, or copy a",
           "finished entry out of here and into the app you are posting from.",
           "",
           "Fill in `EN:`, `Q:` and `ODIA:`. `/post` drafts EN and Q against the rules in",
           "`docs/SOCIAL.md` §5. The Odia line is Chandan's — nothing goes out in Odia that",
           "he has not written.",
           "",
           f"{len(rows)} photographs.",
           ""]

    for r in rows:
        slug = r.get("slug", "").strip()
        # Every caption has to name the place, so a missing one is stated, not hidden
        # behind a tidy dash. Same for the date.
        missing = "____  ← not in the manifest. Fill it there before posting."
        tags = tidy_tags(",".join([",".join(CORE_TAGS), r.get("tags", "")]))
        out += [
            f"## {slug} — {r.get('group', '').strip()}",
            "",
            f"- place: {r.get('place', '').strip() or missing}",
            f"- when: {r.get('when', '').strip() or missing}",
            f"- photo: `assets/photos/{slug}.jpg` · "
            f"https://maatirakatha.com/photographs.html#{slug}",
            f"- on the site: {r.get('caption', '').strip() or '—'}",
            # A hashtag cannot hold a space: the manifest tag "red earth" is #redearth.
            f"- tags: {' '.join('#' + t.replace(' ', '') for t in tags.split(',') if t)}",
            f"- notes: {r.get('notes', '').strip() or '—'}",
            "",
            "```",
            "EN:   ",
            "Q:    ",
            "ODIA: ",
            "```",
            "",
        ]

    path = ROOT / "docs" / "CAPTIONS.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"  CAPTIONS.md        {len(rows)} drafts")
    print("\nRun it again — the file should not change. That is the check.")


if __name__ == "__main__":
    cmds = {"sheet": cmd_sheet, "manifest": cmd_manifest, "build": cmd_build,
            "sizes": cmd_sizes, "render": cmd_render, "captions": cmd_captions}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(f"usage: python tools/photos.py [{'|'.join(cmds)}]")
    SRC.mkdir(exist_ok=True)
    cmds[sys.argv[1]]()
