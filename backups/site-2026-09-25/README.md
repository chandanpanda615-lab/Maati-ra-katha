# maatirakatha.com as it was on 25 September 2026

A byte-for-byte copy of the five pages, the two journal posts and `assets/` exactly as
`main` served them at commit `2a8298d` ("Update website"), taken before the September
2026 redesign. Nothing in this folder has been edited.

It is a complete site on its own: every path in it is relative, so open
`backups/site-2026-09-25/index.html` from a local checkout (or serve the repo with
`python -m http.server` and visit `/backups/site-2026-09-25/`) and it renders as it did.

The photographs cost almost nothing to keep here. Git stores a file once by its
content, so these copies share their storage with `assets/photos/`.

## Putting it back

The cleanest way is to restore the commit itself, not to copy files out of here:

```bash
# The whole live site back to this snapshot, as a new commit on main:
git checkout main
git checkout 2a8298d -- index.html land.html photographs.html days.html visit.html posts assets favicon.ico
git commit -m "Restore the site from before the September 2026 redesign"
git push
```

Or just one page, e.g. the old homepage:

```bash
git checkout 2a8298d -- index.html
```
