# Social — what is out there, what works, what we do

Research run 4 August 2026 with the Apify CLI, in two rounds. Everything below is measured,
not guessed. Where a number is weak, it says so. Section 6 says plainly what none of this
proves.

Total cost: **$4.18** on the Apify account `fast_zone` — $2.19 for the Instagram round,
$1.99 for the YouTube and audience round.

`/post` reads §4 and §5 of this file every time it drafts a caption. Change a rule here and
the drafts change with it.

---

## 1. The findings, in four lines

1. **Nobody documents Kandhamal.** Two clusters exist on Instagram and neither is us:
   homestay advertising, and village nostalgia reels.
2. **We have been looking at the wrong platform.** On Instagram this niche tops out around
   11,000 likes. On YouTube, "Odia village vlog" returns a **median of 319,220 views**. One
   Odia video about one named village pulled 360,202 views and 640 comments.
3. **Instagram comments here are ritual, not conversation** — 38% are emoji only, 3% ask a
   question. On YouTube 45–63% are real sentences and 48 of 300 drew replies.
4. **The audience has already told us the risk.** The single most-upvoted comment we
   measured warns that videos like these attract moneyed outsiders and wreck the village.
   That is not a hostile comment. It is the brief.

---

## 2. How the research was done

Ten Apify runs. All re-runnable — the CLI is logged in as `fast_zone`.

| # | Actor | Input | Got | Cost | Dataset |
|---|---|---|---|---|---|
| 1 | `apify/instagram-hashtag-scraper` | 8 broad tags × 30 | 177 posts, 143 accounts | $0.46 | `scYqC1NghKMm1MOWa` |
| 2 | `apify/instagram-hashtag-scraper` | 8 Odisha tags × 30 | 189 posts, 140 accounts | $0.43 | `d2Mgizr0GIGTsWOAY` |
| 3 | `apify/instagram-profile-scraper` | 25 usernames | followers, bios, last post | $0.06 | `PjykKpcigecCKcd3Q` |
| 4 | `apify/instagram-post-scraper` | 12 accounts × 40 | 398 posts with engagement | $1.24 | `nWLAxw1i7CcP64ZmL` |
| 5 | `streamers/youtube-scraper` | 8 search queries × 20 | 160 videos | $0.64 | `iGGz5CEEYcYGycbk6` |
| 6 | `streamers/youtube-scraper` | 3 channels × 25 | 75 videos | $0.30 | `C3TBMLKfe7QvKnpRd` |
| 7–8 | `apify/instagram-hashtag-analytics-scraper` | 26 hashtags | post volumes, related tags | $0.06 | `HuvIW6sdhFPPbwvry` |
| 9 | `apify/instagram-comment-scraper` | 15 posts × 15 | 148 comments | $0.38 | `mqYVVr8gWVCOsTwSJ` |
| 10 | `streamers/youtube-comments-scraper` | 4 videos × 75 | 300 comments | $0.60 | `1EfuALygG0GNTMsCa` |

Instagram results cost **$0.0026 each**, YouTube videos **$0.004**, YouTube comments
**$0.002**. Multiply before running anything; that is the whole budgeting method.

```bash
apify actors search instagram                             # find an actor
apify actors info <actor> --input                         # read the schema, never guess fields
apify actors call <actor> -f input.json --silent
apify runs ls <actor> --limit 1 --desc --json             # id, defaultDatasetId, usageTotalUsd
apify datasets get-items <datasetId> --limit 1000 > out.json
```

Datasets expire on the free plan. The numbers in this file are the record; the JSON is not.

---

## 3. Who is in this space

### YouTube — where the audience actually is

| Channel | Subs | Median views | What it is |
|---|---|---|---|
| `@CharigarhVlogs1614` | 183,000 | 36,344 | **The closest thing to a peer.** Tribal Odisha — weddings, rituals, haats. All Odia titles, 18–31 minutes. Top video 1,973,037 views |
| `@Theodia_traveller` | 37,900 | 10,382 | Odia travel. Its biggest video by far is one named village. Also runs foreign guests through Odisha |
| `@DistrictPrisha` | 321,000 | — | Did the Kandhamal / Phulbani / Daringbadi tour video: 444,580 views |
| `@OdishaTourismOfficial` | 81,800 | — | State tourism. "Eco Retreat Daringbadi", 972,142 views on a 30-second clip |
| `@talkintravel` | 113,000 | — | "I Stayed With The Tribals In Their Village In A Jungle Of Odisha" — 821,779 views, **1,436 comments** |
| `@RSOdiaVlogger` | 7,450 | 379 | What a small Odia travel channel actually looks like. A floor, not a model |

Daringbadi — inside Kandhamal — already carries real search demand: 996,536 · 517,295 ·
271,545 · 258,872 views on plain tour videos. The district name itself is unserved:
"Kandhamal" returns a median of 1,741 views, "Kandhamal tourism" 1,836.

**71 of the 160 videos sampled were published in 2026.** This is a live space, not an archive.

### Instagram — small, and mostly advertising

| Account | Followers | Last post | What it is |
|---|---|---|---|
| `@the_odishaindex` | 40,598 | 3 Aug | Odisha news and culture aggregator. The only real reach. Does paid promotion |
| `@baevuthevillage` | 11,635 | 31 Jul | Village-stay resort, Karnataka. The commercial version of our idea |
| `@gramvikasodisha` | 3,816 | 31 Jul | Gram Vikas NGO, rural Odisha. Closest in seriousness, not in subject |
| `@adivasisocialhub` | 2,215 | 30 Jun | Ho and Santal tribal culture |
| `@captureboyz` | 1,704 | 3 Aug | Mayurbhanj video creator. Highest engagement of any Instagram account here |

The nearest peers are tiny and real: **`@fromod12`** (93 followers, Kandhamal — posts
Karanjikana, Belaghar Block, Phulbani), `@village_flux` (89, Odisha), `@cllickaway` (69,
"Documenting Everyday Life"), `@mitro.talab` (266, Koraput), `@rurallife_kanha` (75, Baiga
villages in MP — the nearest parallel project anywhere).

Operators already selling tribal Odisha: `@alternativetoursindia` (815), `@5sensestours`
(267), `@manasordipu` (3,998). They post to almost no engagement. When the pilot opens they
matter; for building an audience they are not the model.

**Kandhamal on Instagram is empty.** `@su_bham__nk` has 14 followers and six posts.
`@fromod12` is the only serious account in the district.

---

## 4. What earns engagement

### 4a. Instagram — measured across 398 posts from 12 accounts

Comments matter more than likes: likes are hidden on two of the strongest accounts, and a
comment is worth more to reach.

| Cut | Mean comments |
|---|---|
| **Video** | 2.9 |
| Carousel | 2.1 |
| **Single image** | **0.3** |
| **Odia-script caption** | **5.2** |
| Hindi / Devanagari | 0.8 |
| English | 1.5 |

Caption length: **11–30 words is the best bucket** (comment ratio 2.92, against 0.91 for
1–10 words and 0.76 for 31–70). A question in the caption: 1.94 against 1.33 without.
Hashtag count barely moves anything — 6–15 beats 1–5 slightly, and 1–5 is no better than
none.

**What won.** `@fromod12`, on 93 followers, took **341 likes** with a flat sentence:
*"Karanjikana is a small, remote tribal village located in the Belaghar Block of Kandhamal
district."* No adjectives, a real place named. It took 232 likes on *"Phulbani Ratha Yatra
1995 v/s Now"* — then and now, same frame. `@captureboyz` took **4,843 likes** on
*"ଆଉ ମାତ୍ର କିଛି ଦିନର ଅପେକ୍ଷା..."* — only a few days more to wait, before a festival, in Odia.

**What failed.** Brochure voice — *"Escape. Unwind. Belong."* and *"A slower kind of luxury,
rooted in the simple joys of village life"* — 2 and 3 likes. Greeting cards — *"Wishing
everyone a very happy Rath Yatra"* — 1 like. Long essays with no place in them. Stylised
unicode captions, which are also unreadable to a screen reader.

### 4b. YouTube — opposite rules, ten times the audience

Duration, across 160 videos:

| Length | Median views |
|---|---|
| **30m+** | **161,134** |
| 15–30m | 116,742 |
| 5–15m | 18,002 |
| 1–5m | 2,448 |
| under 1m | 1,263 |

Normalised within the three channels studied, **15–25 minutes** is the sweet spot (1.74×
that channel's median) and **under 5 minutes is 0.35×**. This is the exact inverse of
Instagram. Short does not work here.

Two results matter more than the averages:

- **One named village beats any general theme.** `@Theodia_traveller`'s single biggest video
  — 34.7× its own median, 360,202 views, 640 comments, 8,100 likes — is
  *"ଓଡ଼ିଶାର ସବୁଠୁ ସୁନ୍ଦର ଓ ସଫା ଗାଁ | Cleanest Village of Odisha Bobeijoda"*. Fifteen minutes,
  Odia title, one village, named. **That is our format, already proven, by someone else.**
- **Outsiders experiencing Odisha is a proven genre.** The same channel's next four best are
  a Colombian (128,818), a South African trying muri for the first time (102,905), and a
  Russian guest (39,552 and 33,513) — 3× to 12× its median. Talkin Travel's
  outsider-stays-with-tribals video took 821,779 views and 1,436 comments. A life-exchange
  *is* this genre.

**Sensationalism loses.** `@CharigarhVlogs1614`'s worst videos are its most lurid — a
"man-eating village" (10,814 views) and a "cursed snake village" (9,177), both 0.3× its
median — while its ceremony and ritual videos run 3× to 54×. The audience punishes the very
thing that would compromise us anyway.

Title language: nothing conclusive. Odia-script titles scored 1.00 against 0.77 for
Latin-only, but that is 62 videos against 13 and confounded with channel. Not proven.

### 4c. Hashtags — measured post volumes, not guesses

Six of the sixteen tags used in round 1 are effectively dead:

| Tag | Posts |
|---|---|
| `#ruraltourismindia` | 890 |
| `#kandhamaldiaries` | 1,030 |
| `#ruralodisha` | 1,270 |
| `#villagestay` | 5,404 |
| `#villagelifeindia` | 7,550 |
| `#tribalodisha`, `#kuidialect` | no data returned — treat as near-zero |

Worth using — small enough to rank in, real enough to reach:

| Tag | Posts | | Tag | Posts |
|---|---|---|---|---|
| `#homestayindia` | 16,150 | | `#kandhamal` | **49,770** |
| `#villagetourism` | 23,910 | | `#ruraltourism` | 165,120 |
| `#daringbadi` | 30,090 | | `#odiafood` | 540,500 |
| `#phulbani` | 30,180 | | `#adivasi` | 858,910 |
| `#odiablogger` | 43,770 | | `#odishatourism` | 1,100,000 |

`#sarangada` exists with 5,514 posts. By volume that is a dead tag, and it is on our list
anyway — not for reach, but so anyone who ever searches the village finds us. `#odisha`
(11.03m) and `#villagelife` (6.36m) are for company, not discovery.

This list is the `CORE_TAGS` constant in `tools/photos.py`. `#daringbadi` is deliberately
left out of it: it would pull traffic, and we are not there.

### 4d. Who is actually commenting — and what they are afraid of

**Instagram, 148 comments across 15 posts in this niche:**

| | |
|---|---|
| emoji only | 38% |
| devotional call-and-response ("Jay Badam", "ଜୟ ଜଗନ୍ନାଥ") | 24% |
| a real sentence | 20% |
| short praise, 1–3 words | 16% |
| **asks where / how / how much** | **3%** |

**This corrects the first round's reading.** The 125-comment flood of "Location?" that looked
like the engine was a Bengaluru weekend-getaway account with a bookable stay. Across the
Odisha village niche, almost nobody asks anything. Instagram here is applause, not
conversation. (One thing the first round overstated: author self-replies are only 4% of
comments, not enough to distort any account's numbers.)

**YouTube, 300 comments across 4 videos:** 45–63% are real sentences, median six words, and
48 of 300 drew replies. On the outsider-stays-with-tribals video, **13% ask where, how, or
how to book** — *"Where to do village stay booking please help us"* — the highest ask-rate of
any content measured anywhere. And in Odia, on the wedding video:
*"ଭାଇ ଏ ଗ୍ରାମ ର ନାମ କଣ ଆଉ କଉ ଜିଲ୍ଲା ରେ ଅଛି"* — brother, what is this village's name, and
which district.

Script: 77% Latin, 16% Odia. Odia-speakers largely type in Latin letters. **Do not read the
"Odia script wins" result in §4a as "post only in Odia script" — write Odia, but expect to be
answered in Latin.**

**The warning.** The most-upvoted comment in the entire sample — 85 votes, on the tribal
wedding video — is in Odia, and it bows to the simplicity of the tradition while grieving the
extreme poverty behind it. Another, plainer:

> *"ଏମିତି ଭିଡିଓ ଦେଖିକି ପୁଞ୍ଜିପତି ଆକୃଷ୍ଟ ହେଉଛନ୍ତି ତା ପରେ ଏମାନଙ୍କ ଜୀବନ ନର୍କ । ସେମାନେ ପ୍ରକୃତି ସହିତ ଆରାମ ରେ ଅଛନ୍ତି"*
> — watching videos like this, moneyed people are drawn in, and then these people's lives
> become hell. They are at peace with nature.

That is this audience describing, precisely, the failure mode of a village life-exchange. It
belongs in §5 as a rule, not in a footnote.

---

## 5. What we do

### The platform decision

**YouTube is the main channel. Instagram is the notice board.** One 15-minute video about
Sarangada has a measured ceiling ten to a hundred times higher than anything Instagram offers
in this niche, and it is the only place where people talk back. Instagram gets the stills and
points at the video.

### YouTube

1. **15 to 25 minutes.** Under five minutes measures at a third of the return. Do not cut the
   project into reels.
2. **One named village per video.** Sarangada, Nuagaon Block, Kandhamal. The best-performing
   video in this entire study is one village, named, for fifteen minutes.
3. **Odia title**, English in the second half of it for search.
4. **Never the lurid frame.** Poverty, superstition and "untouched tribe" framings measurably
   lose, and they would break rule 1 anyway.
5. **When the pilot opens, the outsider-guest format is proven** — a visitor's week in
   Sarangada, in their own words. Not before it opens, and never staged.

### Instagram

6. **Name the place in every caption.** Sarangada. Nuagaon Block. Kandhamal. Never "a village
   in Odisha".
7. **11–30 words, one concrete noun, one question.** The `notes` column of
   `_incoming/manifest.csv` is the raw material — it was written for this. Run
   `python tools/photos.py captions` and draft from what is there, never from imagination.
8. **Odia first, English second.** The site stays English; captions should not. Expect replies
   in Latin-script Odia.
9. **Carousels and video, not single frames.** A single image is the worst format measured.
   Post the album, not the photo.
10. **Anticipation before a festival, not greetings during it.** "A few days more" beat "happy
    festival" by three orders of magnitude.
11. **Answer "where is this?" in public, every time** — including that it is Sarangada and it
    is not open until around 2028. Rule 3 is also the best content we have.

### Never

12. No brochure verbs: escape, unwind, retreat, discover, immerse. No "authentic",
    "immersive", "vibrant", "nestled", "hidden gem" — `docs/BRAND.md` banned them and the data
    agrees.
13. No greeting cards. No stylised unicode captions.
14. **Nothing that invites the outcome that comment warned about.** No "undiscovered", no
    "before it changes", no scarcity framing, no drone-over-poverty. The audience that would
    love this project is watching for exactly that, and will say so.

### Engage with, in this order

`@CharigarhVlogs1614` and `@Theodia_traveller` on YouTube — both are doing our format well and
neither is in Kandhamal. `@the_odishaindex` on Instagram for reach. **`@fromod12`** — same
district, same instinct, no competition between you; worth a real relationship rather than a
follow. Then `@gramvikasodisha` and `@rurallife_kanha`.

---

## 6. What this does not prove

- 398 Instagram posts from 12 accounts, 235 YouTube videos, 448 comments. Enough to see a
  direction, not enough to trust any single number.
- YouTube view counts are lifetime; Instagram engagement decays in days. The two columns are
  not directly comparable — the gap is real, the exact ratio is not.
- Instagram hides like counts on `@captureboyz` (33 of 40 posts) and `@village_flux` (all 31).
  Like-based conclusions exclude them.
- The Odia-title result on YouTube is confounded with channel. Not established.
- Hashtag volumes come from Instagram's own related-tag data. `#odishavillage` reported zero
  posts when we had already scraped posts from it, so treat any single figure as indicative.
- Comment sampling took the top 15 per Instagram post and 75 per YouTube video, in the order
  the platform returned them. Newest and top-voted comments are over-represented.
- Every account measured is small to mid-sized. What works at 93 followers may not be what
  works at 9,000. **Re-run this after six months of posting, when we have our own numbers to
  compare against.**
