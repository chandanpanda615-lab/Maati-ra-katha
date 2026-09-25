#!/usr/bin/env python3
"""Self-check for tools/pages.py. Plain asserts, no framework, standard library only.

    python tools/test_pages.py

A checker that passes everything proves nothing. Each test copies the site into a
temporary folder, breaks one thing the way it has actually broken before (or would),
and asserts that `check` catches it. The last test runs `check` on the real site.
"""
import io, shutil, sys, tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pages as site_tool

REAL_ROOT = site_tool.ROOT
SITE_FILES = ["index.html", "land.html", "photographs.html", "days.html", "journal.html",
              "visit.html", "404.html", "sitemap.xml", "posts", "assets"]


def run_check(root):
    """(passed, output) for `check` run against the site copied into root."""
    real, site_tool.ROOT = site_tool.ROOT, root
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            site_tool.cmd_check()
        return True, out.getvalue()
    except SystemExit as e:
        return False, out.getvalue() + str(e)
    finally:
        site_tool.ROOT = real


def broken(edit):
    """Copy the site, apply edit(root), run check. Returns the check's output."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for name in SITE_FILES:
            src = REAL_ROOT / name
            if src.is_dir():
                # The photographs are only needed to exist; symlinks keep this fast.
                shutil.copytree(src, root / name, symlinks=True,
                                ignore=shutil.ignore_patterns("*.jpg") if name == "assets" else None)
            else:
                shutil.copy2(src, root / name)
        for jpg in (REAL_ROOT / "assets").rglob("*.jpg"):
            dst = root / jpg.relative_to(REAL_ROOT)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                dst.symlink_to(jpg)
        edit(root)
        ok, out = run_check(root)
        assert not ok, "check passed a site that was deliberately broken"
        return out


def replace(root, name, old, new):
    p = root / name
    text = p.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {name}: the test needs updating"
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_dead_link_is_caught():
    out = broken(lambda r: replace(r, "land.html", 'href="photographs.html#land"', 'href="photos.html#land"'))
    assert "photos.html" in out and "does not exist" in out, out


def test_missing_anchor_is_caught():
    """photographs.html#school-meal must have id="school-meal", or the link lands on nothing."""
    out = broken(lambda r: replace(r, "days.html", 'href="photographs.html#terraces"',
                                   'href="photographs.html#terrace"'))
    assert 'no id="terrace"' in out, out


def test_www_and_wrong_canonical_are_caught():
    """www 301-redirects and unfurlers drop the og:image — CLAUDE.md's <head> rule."""
    out = broken(lambda r: replace(r, "visit.html", '<link rel="canonical" href="https://maatirakatha.com/visit.html">',
                                   '<link rel="canonical" href="https://www.maatirakatha.com/visit.html">'))
    assert "canonical" in out and "www.maatirakatha" in out, out


def test_offsite_og_image_is_caught():
    out = broken(lambda r: replace(r, "land.html", 'content="https://maatirakatha.com/assets/land.jpg"',
                                   'content="https://raw.githubusercontent.com/x/land.jpg"'))
    assert "same origin" in out, out


def test_image_without_alt_is_caught():
    out = broken(lambda r: replace(r, "journal.html", '<img src="assets/photos/mist-hills.jpg" alt=""',
                                   '<img src="assets/photos/mist-hills.jpg"'))
    assert "has no alt" in out, out


def test_hand_edited_footer_is_caught():
    """The footer lives in tools/pages.py. An edit to one page's copy is drift."""
    out = broken(lambda r: replace(r, "days.html", "the story the soil tells", "the story of the soil"))
    assert "run: python tools/pages.py sync" in out, out


def test_post_missing_from_journal_and_sitemap_is_caught():
    def add_post(r):
        shutil.copy2(r / "posts" / "first-post.html", r / "posts" / "third-post.html")
        replace(r, "posts/third-post.html", "https://maatirakatha.com/posts/first-post.html",
                "https://maatirakatha.com/posts/third-post.html")
        replace(r, "posts/third-post.html", "https://maatirakatha.com/posts/first-post.html",
                "https://maatirakatha.com/posts/third-post.html")
    out = broken(add_post)
    assert "journal.html: does not link to posts/third-post.html" in out, out
    assert "third-post.html is a page but is not listed" in out, out


def test_banned_word_is_caught():
    out = broken(lambda r: replace(r, "visit.html", "Plain comforts, honestly.", "Authentic plain comforts."))
    assert "'authentic'" in out, out


def test_stale_image_dimensions_are_caught():
    """A photograph re-cropped after a page was written keeps its old width/height there."""
    out = broken(lambda r: replace(r, "journal.html", 'width="1600" height="661"', 'width="1600" height="739"'))
    assert "the file is 1600x661" in out, out


def test_the_real_site_passes():
    ok, out = run_check(REAL_ROOT)
    assert ok, out


def test_sync_is_a_no_op_on_the_real_site():
    for rel in site_tool.pages():
        assert site_tool.synced(rel) == (REAL_ROOT / rel).read_text(encoding="utf-8"), \
            f"{rel}: sync would change it — run python tools/pages.py sync"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} passed")
