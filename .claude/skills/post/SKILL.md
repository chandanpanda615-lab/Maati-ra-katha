---
name: post
description: Draft the next Instagram or YouTube post for Maati Ra Katha from the photograph archive, against the measured rules in docs/SOCIAL.md. Use when Chandan says /post, "draft a caption", "what should I post", "write the post for <slug>", or asks for a YouTube title or description.
---

# Draft the next post

## Before writing anything

Read these three. They are the rules; this file only points at them.

- `docs/SOCIAL.md` §4 (what earns engagement, measured) and §5 (what we do)
- `docs/BRAND.md` (voice)
- `CLAUDE.md` — the four non-negotiable rules. Rule 1 and rule 3 both apply to a caption.

If `docs/CAPTIONS.md` is older than `_incoming/manifest.csv`, run
`python tools/photos.py captions` first.

## Instagram

1. Work on the slug Chandan named. If he did not name one, pick a photograph from
   `docs/CAPTIONS.md` that has a `place:` and rich `notes`, say why you picked it, and
   let him redirect you.
2. Write `EN:` — **11 to 30 words.** Name the place. One concrete noun from the frame
   (chulha, jharana, laterite, paddy, borewell). Everything you write must come from
   that entry's `notes` and `on the site` lines. If the notes do not say it, it does
   not go in the caption.
3. Write `Q:` — one question only someone who has lived it can answer. Not "have you
   ever been to a village like this".
4. Leave `ODIA:` blank. Chandan writes it. Never fill it in, even if asked to "just
   try" — a wrong Odia line goes out under his name.
5. If `place:` says `____`, stop and ask. Do not guess a place, and do not post
   without one.

Then check the draft against these, which the research measured as failures:

- Brochure verbs: escape, unwind, retreat, discover, immerse. And the words
  `docs/BRAND.md` already bans: authentic, immersive, vibrant, nestled, hidden gem.
- Greeting cards. "Wishing everyone a happy Rath Yatra" measured 1 like. Being at the
  festival works; wishing people well does not.
- Stylised unicode (`ˢᵒᵐᵉ ᵛⁱᵉʷˢ`). Unreadable to a screen reader.
- More than one question. Two questions get neither answered.

## YouTube

Different platform, opposite rules — §4b of `docs/SOCIAL.md`. If Chandan asks for a
video title or description: 15–25 minutes is the measured sweet spot, the title goes in
Odia, and one named village beats any general theme. Draft the title, three
alternatives, and a description whose first two lines name the village and the district.

## Always

Show the draft in the reply and stop. Do not post anything anywhere — there is no
posting tool here, and nothing goes out without Chandan reading it first.

`docs/CAPTIONS.md` is a workbench, not a ledger: `python tools/photos.py captions`
rewrites it from the manifest every run. Do not save approved drafts into it, they
would be regenerated away. Chandan copies a finished caption straight into Instagram.
If he ever wants posted/not-posted tracked, that belongs in a new manifest column —
the manifest is the source of truth for everything else already.
