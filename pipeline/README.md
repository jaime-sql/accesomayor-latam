# AccesoMayor-LatAm audit pipeline (v0.1.3)

Runner version is `PIPELINE_VERSION = "0.1.3"` in `audit.py` (readability sanity gate). Commands below match the repository root README.

## Run (one command)

From the repository root:

```bash
cd pipeline
./run.sh ../data/page_frame.csv out/                              # or: make audit
./run.sh ../data/page_frame.csv out/ --ids SV-034-02,SV-008-03   # page_id or frame_id
./run.sh ../data/page_frame.csv out/ --country SV                 # one ISO2 country
./run.sh ../data/page_frame.csv out/ --limit 3                    # first N rows after the filters above
.venv/bin/python -m pytest -q                                     # no crawl; or: make test
```

`./run.sh` creates `.venv` when it is missing, installs the pinned Python and npm dependencies, installs Chrome for Testing when it is missing, then runs `audit.py`. Filters apply in order: `--country`, then `--ids`, then `--limit`. `--ids` matches `page_id` or `frame_id` (comma-separated, no spaces), so `--ids SV-001` keeps every page of that frame.

`make audit` uses `FRAME` (default `../data/page_frame.csv`) and `OUT` (default `out`). Pass runner flags with `make audit ARGS="--country SV --limit 3"`.

Requires Node 20 and Python 3.12+. Writes `pages.csv`, `violations.csv`, and `run_log.csv` in the output directory. A full `./run.sh` contacts every auditable URL. `pytest` / `make test` do not. Frozen inputs, the Oct 11 measurement, and what the DataPort package should ship: [`docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md).

## Pinned versions

`run.sh` installs these from `requirements.txt`, `package.json`, and `package-lock.json`:

- axe-core 4.10.3
- lighthouse 12.3.0
- puppeteer-core 23.11.1
- Chrome for Testing 131.0.6778.204 (`@puppeteer/browsers` 2.6.1 installs it under `browsers/`)
- textstat 0.7.4 (setuptools 75.8.0, required by textstat's `pkg_resources`)
- pyphen 0.17.0
- beautifulsoup4 4.12.3
- pandas 2.2.3
- jsonschema 4.23.0
- requests 2.32.3
- pytest 8.3.4

Developed on Node 20.19 and Python 3.13. The requirement floor, as in the root README, is Node 20 and Python 3.12+.

## What a run does per URL

1. Rows whose `frame_status` is not `auditable` are written as `audit_status=skipped` with that status as `failure_reason`. No request.
2. Live `robots.txt` check (User-Agent token `AccesoMayor-LatAm`). Disallow, a non-200 other than 404/410, or a fetch error becomes `skipped_robots` with `failure_reason` `robots_disallow`, `robots_status_<code>`, or `robots_fetch_error:<type>`. A 404/410, or an HTML document served at `/robots.txt`, counts as no robots file (allowed).
3. At least 5 seconds per host between every request the runner makes (robots fetch, Lighthouse load, axe load). `DELAY = 5.0` in `audit.py`; `audit_page.mjs` waits 5 s between the Lighthouse pass and the axe load.
4. `audit_page.mjs` in pinned Chrome: Lighthouse (mobile 412×823, simulated slow 4G, performance + accessibility), then axe-core with tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa` in the same mobile viewport. The browser user-agent also carries `AccesoMayor-LatAm/0.1 accessibility-research`.
5. Visible text stays in memory long enough for textstat (`es`) and a SHA-256, then it is deleted. Fernández-Huerta and Szigriszt-Pazos are computed for `page_type=task` only. v0.1.3 nulls those scores when words per sentence exceed 80 or a score falls outside 0–100 (`read_flag` = `wps_gt_80` or `score_out_of_range`); word and sentence counts are kept.
6. Each page row is validated against `schema/pages.schema.json` and each violation row against `schema/violations.schema.json`. A page row that fails validation is written with `audit_status=failed` and `failure_reason=schema:...`. Outputs: `pages.csv`, `violations.csv`, `run_log.csv`.

Every selected input row becomes one `pages.csv` row and one `run_log.csv` row. `violations.csv` gets rows only when axe ran. Blocked pages (`failed`, `bot_challenge`, `skipped`, `skipped_robots`) store null metrics, never zeros.

Stored per page: metrics, violation counts, status, `failure_reason`, and `content_sha256`. HTML, visible text, screenshots, Lighthouse reports, axe node HTML/selectors, and cookies are discarded. No logins and no form posts. `final_url` has its query string and fragment removed.

## Known limitations

- **Readability is reported on task pages only.** Homepages are menu-dominated: their visible text is mostly navigation labels with almost no sentence punctuation (smoke test: 154–231 words in 2–4 "sentences"), so Fernández-Huerta / Szigriszt-Pazos would measure menu structure, not the language older adults must read. `read_*` scores are null for `page_type=home` (schema-enforced). Word and sentence counts follow the same rule: they are set only for task pages.
- In `violations.csv` a rule mapped to two success criteria appears twice (once per criterion). Sum `nodes` per rule, not per row, for element totals.
- Lighthouse millisecond values are simulated (lantern), not field data.
- Smoke test (Oct 10, 2026): SV-001, SV-011, SV-034 all `ok`, 10 violation rows, every `sc_id` joins to `ml/wcag_older_adult_map.csv`.

## Version notes

### v0.1.3 readability sanity gate

Current runner. `pipeline_version` on each new row is `0.1.3`. The frozen El Salvador pilot predates this gate; pilot row SV-049-02 has an out-of-range Fernández-Huerta score that this schema nulls. See `data/schema.md`.

### v0.1.2 task categories

Six values on `data/page_frame.csv`: `requirements_howto`, `appointments`, `fees_rates`, `service_info`, `faq`, `contact`. Keyword-assigned, then hand-screened on a stratified sample. Not gold-standard. Legacy `how_to` / `requirements` still validate and the runner maps them to `requirements_howto`.

### v0.1.1 bot-challenge gate

Still applied on every audited page. Redirect to a different registrable domain → `failed` / `offsite_redirect:<domain>`. Challenge interstitial → `bot_challenge`. Chrome's error page → `failed` / `navigation_error:chrome_error_page`. Metrics stay null. `final_url` query and fragment are stripped.

## Building the page list

`discover_tasks.py` follows homepage links (skips news/blog/press/PDF/Office/login/social, date-slugged and long-slug URLs; checks robots per path; ≥5 s/host) and keeps up to two pages of different categories. `build_page_frame.py` applies manual curation (dropped list in `data/page_frame_dropped.csv`) and re-checks status and robots for every page via `check_frame.py`.

Those scripts built the frozen frame. They are a live crawl. Publishing the measurement CSVs does not require running them again.

## Reproducibility

[`docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md) covers the frozen inputs (`sampling_frame`, `page_frame`, dictionary, schema), how `pages.csv` and `violations.csv` are produced, the ≥5 s/host and robots.txt rules, what is left out of the repository, and what the IEEE DataPort package should ship.
