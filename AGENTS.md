# Maati Ra Katha — for any coding agent

The working notes for this repository are in **`CLAUDE.md`**. Read all of it before you
change anything; it is kept current and this file is not a copy of it. The look of the
site is in **`docs/BRAND.md`**.

Four rules that are not negotiable, whatever else you are asked to do:

1. **No fake experiences.** No stock photography, no AI-generated or AI-upscaled images,
   no invented detail. A real photograph or an empty frame — never a substitute.
2. **No face is published before the person agreed.** For children, the school and the
   family. `tools/photos.py` refuses to render a row with `people=yes` and no `consent`.
3. **Nothing is bookable and nothing is promised.** The pilot is not open.
4. **Originals never enter git.** Only built, EXIF-stripped copies in `assets/photos/`.

Before a commit:

```bash
python tools/photos.py render && python tools/pages.py sync
python tools/pages.py check && python tools/test_photos.py && python tools/test_pages.py
```
