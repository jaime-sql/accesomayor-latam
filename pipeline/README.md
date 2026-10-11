# AccesoMayor-LatAm audit pipeline (v0.1.1)

One command: `./run.sh ../data/page_frame.csv out/` (or `make audit FRAME=... OUT=...`).
Options: `--ids SV-001,SV-011`, `--country SV`, `--limit N`.

## Pinned versions
axe-core 4.10.3 · lighthouse 12.3.0 · puppeteer-core 23.11.1 · Chrome for Testing 131.0.6778.204 (installed by @puppeteer/browsers 2.6.1 into `browsers/`) ·
textstat 0.7.4 (+ setuptools 75.8.0, needed by textstat's `pkg_resources`) · pyphen 0.17.0 · jsonschema 4.23.0 · requests 2.32.3 · Node 20.19, Python 3.13. Lockfile: `package-lock.json`.

## What a run does per URL
1. Live robots.txt check (UA token `AccesoMayor-LatAm`); disallow / 403 / unreachable → `skipped_robots` with reason.
2. ≥5 s per host between every request the runner makes.
3. `audit_page.mjs`: Lighthouse (mobile 412×823, simulated slow 4G, perf + accessibility), wait 5 s, then axe-core with WCAG 2.0/2.1/2.2 A+AA tags in a mobile viewport.
4. Visible text → textstat (`es`): Fernández-Huerta, Szigriszt-Pazos, word/sentence count + SHA-256; text then discarded.
5. Rows validated against `schema/*.schema.json`; outputs `pages.csv`, `violations.csv`, `run_log.csv`.

Never stored: HTML, text, screenshots, LH reports, axe node HTML/selectors, cookies. No logins/forms.

## Known limitations
- **Readability is reported on task pages only.** Homepages are menu-dominated: their visible text is mostly navigation labels with almost no sentence punctuation (smoke test: 154–231 words in 2–4 "sentences"), so Fernández-Huerta / Szigriszt-Pazos would measure menu structure, not the language older adults must read. `read_*` are null for `page_type=home` (schema-enforced).
- In `violations.csv` a rule mapped to 2 SCs appears twice (once per SC); sum `nodes` per rule, not per row, for element totals.
- Lighthouse ms values are simulated (lantern), not field data.
- Smoke test (Oct 10, 2026): SV-001, SV-011, SV-034 → all `ok`, 10 violation rows, all `sc_id` join to `ml/wcag_older_adult_map.csv`. Output in `smoke_out/`.

## v0.1.1 bot-challenge gate
Offsite redirect (different registrable domain) → `failed` / `offsite_redirect:<domain>`; challenge interstitial → `bot_challenge`; metrics null, never 0; `final_url` query/fragment stripped. Tests: `.venv/bin/python -m pytest tests` (pytest 8.3.4).

## Building the page list
`discover_tasks.py` follows homepage links (skips news/blog/press/PDF/Office/login/social, date-slugged and long-slug URLs; checks robots per path; ≥5 s/host) and keeps ≤2 pages of different categories. `build_page_frame.py` applies manual curation (dropped list in `data/page_frame_dropped.csv`) and re-checks status + robots for every page.
