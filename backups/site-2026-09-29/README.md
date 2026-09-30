# maatirakatha.com as it was on 29 September 2026

A copy of the site exactly as `main` served it at commit `90755f2` ("Redesign
maatirakatha.com (#1)"), taken before the October 2026 restructure. Nothing in this
folder has been edited. `pages.py` and `photos.py` are the generators that wrote it —
they hold the old nav, footer and gallery markup.

Every path is relative (except `404.html`, which is root-absolute), so serve the repo
with `python -m http.server` and open `/backups/site-2026-09-29/` to see it as it was.
The photographs cost nothing extra here: git stores identical files once.

An older snapshot, from before the September redesign, is in `../site-2026-09-25/`.

## Putting it back

Restore the commit, not the files in this folder:

```bash
git checkout main
git checkout 90755f2 -- index.html land.html photographs.html days.html journal.html \
    visit.html 404.html posts assets tools/pages.py tools/photos.py tools/test_pages.py \
    sitemap.xml CLAUDE.md docs/BRAND.md
git commit -m "Restore the site from before the October 2026 restructure"
git push
```
