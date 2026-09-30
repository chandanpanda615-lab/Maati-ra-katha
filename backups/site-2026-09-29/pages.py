#!/usr/bin/env python3
"""The parts every page shares, and the checks that keep the rest honest.
Standard library only — no Pillow, no build step, nothing to install.

    python tools/pages.py sync    # write the nav and the footer into every page
    python tools/pages.py check   # links, anchors, <head>, sitemap, journal — fails loudly

The nav and the footer live HERE, once, in NAV and FOOT below. Each page carries them
between markers, the same way photographs.html carries the archive:

    <!-- NAV:START ... -->  ...  <!-- NAV:END -->
    <!-- FOOT:START ... --> ...  <!-- FOOT:END -->

`sync` rewrites only what sits between them, with the right relative paths for the
page's folder and aria-current on the page you are on. Running it twice changes nothing,
and `check` fails if a page has drifted from what `sync` would write.

`check` is everything CLAUDE.md used to ask for by hand before a commit, plus the things
that broke without anyone noticing: a link to an anchor that does not exist, an og:image
on another domain, a post missing from the journal list, a page missing from the sitemap.
"""
import html, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://maatirakatha.com/"

# Pages are found, not listed: every .html at the root and in posts/. These are not
# pages of the site — the backup of the old one, an internal research prototype.
SKIP_DIRS = {"backups", "maati-katha-research", "Village_Image", "_incoming", "tools", "docs",
             "node_modules", ".git", ".claude"}

# Words the site does not use. docs/BRAND.md and docs/SOCIAL.md §5 both ban them; the
# data in SOCIAL.md says they lose as well. Checked against visible text only.
BANNED = ["authentic", "immersive", "vibrant", "nestled", "hidden gem", "undiscovered",
          "unspoiled", "off the beaten path", "escape", "unwind", "before it changes"]

# ---------------------------------------------------------------------------------------
# The nav. (href, label, key). `key` is what makes aria-current land on the right link.
NAV = [
    ("land.html", "The land", "land"),
    ("photographs.html", "Photographs", "photographs"),
    ("days.html", "The days", "days"),
    ("journal.html", "Journal", "journal"),
    ("visit.html", "How to reach", "visit"),
]
FOOT_NAV = [("index.html", "Home", "home")] + NAV

def logo(pad):
    """The mark, inline so its strokes take currentColor. Keep the two .frame paths and
    the .sun path in step with assets/logo-mark.svg, the drawing of record."""
    return "\n".join(pad + line for line in [
        '<svg class="brand-logo" viewBox="0 0 24 24" aria-hidden="true" focusable="false">',
        '  <path class="sun" d="M8.7 18.75a3.3 3.3 0 0 1 6.6 0z"/>',
        '  <path class="frame" d="M6.6 18.75V12.15a5.4 5.4 0 0 1 10.8 0v6.6"/>',
        '  <path class="frame" d="M4.65 18.75h14.7"/>',
        "</svg>",
    ])

# Follow links, YouTube first: docs/SOCIAL.md §5 — it is the main channel, Instagram the
# notice board. rel="me" ties each account to this domain.
FOLLOW = [
    ("https://www.youtube.com/@MaatiRaKatha", "YouTube", "@MaatiRaKatha",
     '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/>'
     '<path d="M10.2 9.4v5.2l4.6-2.6z" class="solid"/>'),
    ("https://www.instagram.com/maati.ra.katha/", "Instagram", "@maati.ra.katha",
     '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'
     '<circle cx="17.2" cy="6.8" r="1.1" class="dot"/>'),
    ("https://x.com/maatirakatha", "X", "@maatirakatha",
     '<path d="M4 3.5h4.2l5 6.6 5.4-6.6h2l-6.5 7.9 7 9.1h-4.2l-5.3-7-5.7 7h-2l6.8-8.3z" class="solid"/>'),
    ("mailto:hello@maatirakatha.com", "Email", "hello@maatirakatha.com",
     '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.8 7 8.2 6.2L20.2 7"/>'),
]

NAV_START, NAV_END = "<!-- NAV:START", "<!-- NAV:END -->"
FOOT_START, FOOT_END = "<!-- FOOT:START", "<!-- FOOT:END -->"


def pages():
    """Every page of the site, as paths relative to ROOT."""
    found = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS:
            continue
        found.append(rel)
    return found


def prefix(rel):
    """How a page reaches the site root. 404.html is served by GitHub Pages at whatever
    path was missing — /posts/nope/deeper — so only root-absolute links work there."""
    if rel.as_posix() == "404.html":
        return "/"
    return "../" * (len(rel.parts) - 1)


def current(rel):
    """Which nav key the page belongs to, and whether it IS that page or sits under it."""
    name = rel.as_posix()
    if name.startswith("posts/"):
        return "journal", "true"          # a post is inside the journal, not the journal
    for href, _, key in FOOT_NAV:
        if name == href:
            return key, "page"
    return None, None


def render_nav(rel):
    p = prefix(rel)
    key, how = current(rel)
    links = []
    for href, label, k in NAV:
        cur = f' aria-current="{how}"' if k == key else ""
        links.append(f'    <a href="{p}{href}"{cur}>{label}</a>')
    return "\n".join([
        f"{NAV_START} — written by tools/pages.py sync. Change NAV there, not here. -->",
        '<nav class="site-nav" aria-label="Primary">',
        f'  <a class="brand" href="{p}index.html">',
        logo("    "),
        '    <span class="brand-name">Maati Ra Katha</span>',
        "  </a>",
        '  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links"',
        '          aria-label="Open menu">',
        '    <span class="bars" aria-hidden="true"><i></i><i></i><i></i></span>',
        "  </button>",
        '  <div class="nav-links" id="nav-links">',
        *links,
        f'    <a class="nav-cta" href="{p}visit.html#interest">Pilot</a>',
        "  </div>",
        "</nav>",
        NAV_END,
    ])


def render_foot(rel):
    p = prefix(rel)
    key, how = current(rel)
    nav = []
    for href, label, k in FOOT_NAV:
        cur = f' aria-current="{how}"' if k == key else ""
        nav.append(f'      <a href="{p}{href}"{cur}>{label}</a>')
    follow = []
    for url, name, handle, icon in FOLLOW:
        external = "" if url.startswith("mailto:") else ' rel="me noopener" target="_blank"'
        follow += [
            f'      <a class="follow" href="{url}"{external}>',
            f'        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{icon}</svg>',
            f"        <span>{name} <small>{handle}</small></span>",
            "      </a>",
        ]
    return "\n".join([
        f"{FOOT_START} — written by tools/pages.py sync. Change FOOT there, not here. -->",
        '<footer class="site-foot on-night">',
        '  <div class="wrap foot-grid">',
        '    <div class="foot-brand">',
        f'      <a class="brand" href="{p}index.html">',
        logo("        "),
        '        <span class="brand-name">Maati Ra Katha</span>',
        "      </a>",
        '      <p class="foot-loc">Sarangada · Nuagaon Block · Kandhamal · Odisha<br>20.227°N, 84.124°E</p>',
        '      <p class="foot-note">Nothing on this site is bookable. No route, photograph, or host detail is',
        "      published before it is verified on the ground and consented to.</p>",
        "    </div>",
        '    <nav class="foot-nav" aria-label="Footer">',
        '      <p class="foot-h">The site</p>',
        *nav,
        "    </nav>",
        '    <div class="foot-follow">',
        '      <p class="foot-h">Follow the build</p>',
        *follow,
        "    </div>",
        "  </div>",
        '  <div class="wrap foot-base">',
        "    <p>&copy; 2026 Maati Ra Katha</p>",
        '    <p class="hand">the story the soil tells</p>',
        "  </div>",
        "</footer>",
        FOOT_END,
    ])


def swap(text, start, end, body, where):
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(text):
        raise SystemExit(f"{where}: no {start} ... {end} block. Add the two markers first.")
    return pat.sub(lambda _: body, text, count=1)


def synced(rel):
    text = (ROOT / rel).read_text(encoding="utf-8")
    text = swap(text, NAV_START, NAV_END, render_nav(rel), rel)
    return swap(text, FOOT_START, FOOT_END, render_foot(rel), rel)


def cmd_sync():
    changed = 0
    for rel in pages():
        path = ROOT / rel
        new = synced(rel)
        if new != path.read_text(encoding="utf-8"):
            path.write_text(new, encoding="utf-8")
            changed += 1
            print(f"  wrote  {rel}")
    print(f"{len(pages())} pages, {changed} changed. Run it again — nothing should change.")


# ---------------------------------------------------------------------------------------
class Page(HTMLParser):
    """Everything check needs from one page, in one pass."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.imgs, self.metas = set(), [], [], {}
        self.canonical, self.title, self.h1 = None, "", 0
        self.text, self._skip, self._in_title, self.lang = [], 0, False, None
        self.head_closed = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self.h1 += 1
        if tag == "meta":
            k = a.get("property") or a.get("name")
            if k:
                self.metas[k] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        for attr in ("href", "src"):
            if a.get(attr) and not (tag == "link" and a.get("rel") in ("canonical",)):
                self.links.append((tag, attr, a[attr]))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                self.links.append((tag, "srcset", part.strip().split(" ")[0]))
        if tag == "img":
            self.imgs.append(a)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        if tag == "title":
            self._in_title = False
        if tag == "head":
            self.head_closed = True

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip:
            self.text.append(data)


def image_size(path):
    """(width, height) of a JPEG or PNG, read from its header with the standard library.
    None for anything else. Enough to catch an <img width height> that no longer matches
    its file — which is what happens the moment a photograph is re-cropped."""
    with open(path, "rb") as f:
        head = f.read(26)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
        if head[:2] != b"\xff\xd8":
            return None
        f.seek(2)
        while True:
            b = f.read(1)
            while b and b != b"\xff":
                b = f.read(1)
            while b == b"\xff":
                b = f.read(1)
            if not b:
                return None
            marker = b[0]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                continue
            length = int.from_bytes(f.read(2), "big")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                f.read(1)
                h = int.from_bytes(f.read(2), "big")
                w = int.from_bytes(f.read(2), "big")
                return w, h
            f.seek(length - 2, 1)


def local_file(rel, url):
    """The file a local URL on page `rel` points at, or None for anything off-site."""
    parts = urlsplit(url)
    if parts.scheme or url.startswith("//") or url.startswith("mailto:") or not parts.path:
        return None
    path = unquote(parts.path)
    base = ROOT if path.startswith("/") else ROOT / rel.parent
    return Path(str((base / path.lstrip("/")).resolve()))


def parse(rel):
    raw = (ROOT / rel).read_text(encoding="utf-8")
    pg = Page()
    pg.feed(raw)
    pg.raw = raw
    return pg


def canonical_url(rel):
    name = rel.as_posix()
    return SITE if name == "index.html" else SITE + name


def cmd_check():
    problems = []

    def bad(rel, msg):
        problems.append(f"{rel}: {msg}")

    all_pages = pages()
    parsed = {rel: parse(rel) for rel in all_pages}

    for rel, pg in parsed.items():
        name = rel.as_posix()
        is_404 = name == "404.html"

        # --- the <head> convention (CLAUDE.md): apex domain, no www, same origin ------
        if pg.lang != "en":
            bad(rel, '<html lang="en"> missing')
        if not pg.head_closed:
            bad(rel, "no </head> — the head was left open")
        if not pg.title.strip():
            bad(rel, "no <title>")
        if not pg.metas.get("description"):
            bad(rel, "no meta description")
        if pg.metas.get("color-scheme") != "light dark":
            bad(rel, 'meta color-scheme must be "light dark" or Chrome force-darkens the page')
        if pg.h1 != 1:
            bad(rel, f"{pg.h1} <h1> elements, want exactly one")
        if 'href="' not in pg.raw or "site.css" not in pg.raw or "site.js" not in pg.raw:
            bad(rel, "does not load assets/site.css and assets/site.js")
        if is_404:
            if "noindex" not in pg.metas.get("robots", ""):
                bad(rel, "404 page must be noindex")
        else:
            want = canonical_url(rel)
            if pg.canonical != want:
                bad(rel, f"canonical is {pg.canonical!r}, want {want!r}")
            if pg.metas.get("og:url") != want:
                bad(rel, f"og:url is {pg.metas.get('og:url')!r}, want {want!r}")
            for k in ("og:title", "og:description", "og:image", "twitter:card", "twitter:image"):
                if not pg.metas.get(k):
                    bad(rel, f"no {k}")
            img = pg.metas.get("og:image", "")
            if not img.startswith(SITE):
                bad(rel, f"og:image must be on {SITE} (same origin), got {img!r}")
            elif not (ROOT / img[len(SITE):]).exists():
                bad(rel, f"og:image {img} does not exist in the repo")
            if pg.metas.get("twitter:image") != img:
                bad(rel, "twitter:image differs from og:image")
        for dead in ("life-with-love", "www.maatirakatha", "raw.githubusercontent"):
            if dead in pg.raw:
                bad(rel, f"contains {dead!r} — that URL is dead or wrong")

        # --- shared blocks match what sync writes ------------------------------------
        try:
            if synced(rel) != pg.raw:
                bad(rel, "nav or footer differs from tools/pages.py — run: python tools/pages.py sync")
        except SystemExit as e:
            bad(rel, str(e))

        # --- images: alt always, and dimensions so nothing jumps as they load -------
        # The dimensions must also be the file's own. A re-cropped photograph keeps its
        # old width/height in every hand-written page that shows it, and the browser
        # then reserves the wrong box — or picks the wrong size out of a srcset.
        for a in pg.imgs:
            src = a.get("src", "")
            if "alt" not in a:
                bad(rel, f"<img src={src!r}> has no alt (use alt=\"\" if decorative)")
            if not (a.get("width") and a.get("height")):
                bad(rel, f"<img src={src!r}> has no width/height")
                continue
            f = local_file(rel, src)
            size = image_size(f) if f and f.exists() else None
            if size:
                want, got = size[0] / size[1], int(a["width"]) / int(a["height"])
                if abs(want - got) / want > 0.01:
                    bad(rel, f"<img src={src!r}> says {a['width']}x{a['height']}, the file is {size[0]}x{size[1]}")
            for cand in (a.get("srcset") or "").split(","):
                bits = cand.split()
                if len(bits) == 2 and bits[1].endswith("w"):
                    f = local_file(rel, bits[0])
                    size = image_size(f) if f and f.exists() else None
                    if size and size[0] != int(bits[1][:-1]):
                        bad(rel, f"srcset says {bits[0]} is {bits[1]}, the file is {size[0]}px wide")

        # --- every local link, image and anchor resolves ----------------------------
        for tag, attr, url in pg.links:
            parts = urlsplit(url)
            if parts.scheme or url.startswith("//") or url.startswith("mailto:"):
                continue
            path = unquote(parts.path)
            if path.startswith("/"):
                target = ROOT / path.lstrip("/")
            elif path:
                target = (ROOT / rel.parent / path)
            else:
                target = ROOT / rel                       # "#fragment" on this page
            target = Path(str(target.resolve()))
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                bad(rel, f"{attr}={url!r} points at a file that does not exist")
                continue
            if parts.fragment and target.suffix == ".html":
                trel = target.relative_to(ROOT)
                ids = parsed[trel].ids if trel in parsed else parse(trel).ids
                if parts.fragment not in ids:
                    bad(rel, f"{attr}={url!r}: no id=\"{parts.fragment}\" in {trel}")

        # --- the voice rules, on what a reader actually sees -------------------------
        visible = " ".join(pg.text).lower()
        for word in BANNED:
            if re.search(r"\b" + re.escape(word) + r"\b", visible):
                bad(rel, f"uses {word!r} — banned in docs/BRAND.md and docs/SOCIAL.md")

    # --- sitemap: every page in it, and nothing in it that is not a page -------------
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    listed = set(re.findall(r"<loc>(.*?)</loc>", sitemap))
    wanted = {canonical_url(r) for r in all_pages if r.as_posix() != "404.html"}
    for url in sorted(wanted - listed):
        problems.append(f"sitemap.xml: {url} is a page but is not listed")
    for url in sorted(listed - wanted):
        problems.append(f"sitemap.xml: {url} is listed but there is no such page")

    # --- the journal lists every post ----------------------------------------------
    posts = [r for r in all_pages if r.parts[0] == "posts"]
    journal = parsed.get(Path("journal.html"))
    for post in posts:
        href = post.as_posix()
        if journal and not any(u == href for _, _, u in journal.links):
            problems.append(f"journal.html: does not link to {href}")

    # --- the homepage count is the archive's count ----------------------------------
    home = parsed.get(Path("index.html"))
    photos = len(list((ROOT / "assets" / "photos").glob("*.jpg")))
    m = re.search(r"All (\d+) photographs", home.raw if home else "")
    if not m:
        problems.append("index.html: no 'All N photographs' link — run: python tools/photos.py render")
    elif int(m.group(1)) != photos:
        problems.append(f"index.html: says All {m.group(1)} photographs, assets/photos/ has {photos}")

    if problems:
        print("\n".join(problems))
        sys.exit(f"\n{len(problems)} problem(s) in {len(all_pages)} pages.")
    print(f"{len(all_pages)} pages checked: links, anchors, <head>, images, sitemap, journal, count, voice. All good.")


if __name__ == "__main__":
    cmds = {"sync": cmd_sync, "check": cmd_check}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(f"usage: python tools/pages.py [{'|'.join(cmds)}]")
    cmds[sys.argv[1]]()
