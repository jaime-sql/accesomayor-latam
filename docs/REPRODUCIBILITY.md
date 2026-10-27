# Reproducibility — AccesoMayor-LatAm audit

This note is for competition judges and the Data Engineer. It states how `pages.csv`, `violations.csv`, and `run_log.csv` are produced, which inputs are frozen, and what the IEEE DataPort package should contain. It does not record DataPort registration status.

Pipeline version: **0.1.3** (`PIPELINE_VERSION` in `pipeline/audit.py`). One-command entry: `cd pipeline && ./run.sh ../data/page_frame.csv out/` (or `make audit`). Details and subset flags: `pipeline/README.md`.

## What to treat as the measurement

The publishable audit is the measurement triple from the full-frame run of the frozen page list (11 October 2026):

| file | one row per |
|---|---|
| `pages.csv` | page snapshot (`page_id` + `crawl_ts_utc`) |
| `violations.csv` | `(page_id, axe rule, WCAG success criterion)` |
| `run_log.csv` | attempted URL, including skips and failures |

On the audit host those files are `data/full_run/pages.csv`, `data/full_run/violations.csv`, and `data/full_run/run_log.csv`. They are the files to package. They are not committed in this repository. A clone has the frozen inputs and the runner. It does not have a second copy of that crawl, and it has no page bodies from which the numbers could be recomputed.

`pipeline_version` on each `pages.csv` row is the runner that wrote the row. The current runner writes `0.1.3`.

The DataPort package should ship that measurement triple together with the dictionary and schema below. Ship those CSVs. Run a live crawl only when someone is intentionally regenerating the audit.

Column definitions: `data/data_dictionary.csv` and `data/schema.md`. Machine-checked shapes: `pipeline/schema/pages.schema.json` and `pipeline/schema/violations.schema.json` (JSON Schema 2020-12). The runner validates every output row against those schemas before writing.

## Frozen inputs (this repository)

These files are the inputs. They are already checked in. Do not rebuild them to publish.

| path | what is frozen |
|---|---|
| `data/sampling_frame.csv` | 148 sites (10 countries × 5 sectors), with the HTTP and robots check and `frame_status`. `robots_checked_at` is 2026-10-11 (UTC). |
| `data/page_frame.csv` | 225 pages (home + task), `page_type`, `task_category`. `checked_at` spans 2026-10-11T03:48:55Z–2026-10-11T03:56:11Z. 220 rows are `frame_status=auditable`; any other status is skipped with no request. |
| `data/page_frame_dropped.csv` | Discovered links removed by curation, with the reason. |
| `data/data_dictionary.csv` | Per-field type, unit, tool version, and allowed range. |
| `data/schema.md` | Human-readable schema, collection rules, task categories (v0.1.2), readability gate (v0.1.3). |
| `pipeline/schema/*.schema.json` | Schemas the runner enforces on every output row. |
| `pipeline/requirements.txt`, `pipeline/package.json`, `pipeline/package-lock.json` | Pinned Python and Node dependencies. |

Frame counts, blocked sites, and empty cells: `data/frame_summary.md`. That summary is site-level. The runner reads `page_frame.csv` and obeys each row's `frame_status`.

`pilot/pilot.csv` and `pilot/pilot_violations.csv` are the 10 October 2026 El Salvador pilot (pipeline v0.1.1, 50 audited pages). They are a separate frozen artifact. They are not the full-frame measurement. The pilot predates the v0.1.3 readability gate (SV-049-02).

## How a row is produced

`./run.sh` installs pinned dependencies, then `audit.py` reads the page frame and, for each selected row:

1. If `frame_status` is not `auditable`, write `audit_status=skipped` and `failure_reason=<frame_status>`. No network.
2. Fetch `https://<host>/robots.txt` with User-Agent `AccesoMayor-LatAm` (20 s timeout). `RobotFileParser.can_fetch` uses the same token.
   - 404, 410, or an HTML document in the first 500 characters: treated as no robots file; the page may be audited.
   - Any other non-200: `skipped_robots` / `robots_status_<code>`.
   - Fetch exception: `skipped_robots` / `robots_fetch_error:<ExceptionName>`.
   - Disallow for this token: `skipped_robots` / `robots_disallow`.
3. Wait so that requests to the same host are at least 5 seconds apart (`DELAY = 5.0` in `audit.py`). The axe navigation waits another 5 seconds after Lighthouse (`audit_page.mjs`).
4. Run `audit_page.mjs` under Chrome for Testing 131.0.6778.204. Lighthouse: mobile viewport 412×823, simulated slow 4G, categories performance and accessibility. Then axe-core 4.10.3 with tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`. The browser user-agent suffix is `AccesoMayor-LatAm/0.1 accessibility-research`.
5. Keep visible text in memory only. Hash it (SHA-256, hex, `content_sha256`). For task pages, compute Fernández-Huerta and Szigriszt-Pazos with textstat 0.7.4, language `es`. v0.1.3 sets the scores to null when words per sentence exceed 80 or a score is outside 0–100, and records `read_flag`. Delete the text before any file is written. Homepage readability scores stay null.
6. Apply the v0.1.1 gate: offsite registrable-domain redirect → `failed`; bot-challenge interstitial → `bot_challenge`; Chrome error page → `failed` / `navigation_error:chrome_error_page`. Metrics on those rows are null, never 0. Strip `?` and `#` from `final_url`.
7. Validate against the JSON Schemas. Write the three CSVs. `run_log.csv` columns: `page_id`, `url`, `crawl_ts_utc`, `audit_status`, `failure_reason`.

No logins, no form submission, no clicks past page load. A disallowed or bot-challenged URL stays a skipped or blocked row. It is not fetched by another path.

Pinned tool versions (also listed in `pipeline/README.md`): axe-core 4.10.3, Lighthouse 12.3.0, puppeteer-core 23.11.1, Chrome for Testing 131.0.6778.204, textstat 0.7.4, pyphen 0.17.0, jsonschema 4.23.0, requests 2.32.3, pytest 8.3.4. Requires Node 20 and Python 3.12+ (developed on Node 20.19 and Python 3.13).

## Check the runner without a crawl

From `pipeline/`:

```bash
make test
# same thing:
.venv/bin/python -m pytest -q
```

`make test` creates `.venv` and installs `requirements.txt` when needed. The tests cover frame normalization, skip-without-network, legacy task categories, the readability sanity gate, and the bot-challenge / offsite gate. They do not fetch sites and they do not launch Chrome.

## Regenerating measurements

Regeneration is a live crawl. Use it to replace the measurement on purpose. It is not the publish step.

Full frame (every auditable row in `data/page_frame.csv`):

```bash
cd pipeline && ./run.sh ../data/page_frame.csv out/
# or: make audit
```

Subset, still live for the rows you name:

```bash
./run.sh ../data/page_frame.csv out/ --ids SV-034-02,SV-008-03
./run.sh ../data/page_frame.csv out/ --country SV
./run.sh ../data/page_frame.csv out/ --country SV --limit 3
make audit ARGS="--ids SV-034-02,SV-008-03"
```

Output under `pipeline/out/` (and `pipeline/*_out/`) is gitignored. Do not commit HTML, screenshots, or Lighthouse JSON from that directory.

`discover_tasks.py`, `check_frame.py`, and `build_page_frame.py` rebuild the frame. Leave the committed frame as the input unless the frame itself is being revised.

## Intentionally absent

The repository, the audit host's measurement directory, and the DataPort package keep the tables above. They do not keep:

- page HTML or HTTP bodies
- visible text (it exists in memory only until the hash and readability numbers are computed)
- screenshots, images, Lighthouse JSON reports, or traces
- axe node selectors or HTML snippets (those can contain page text)
- cookies, query strings, or fragments on stored URLs

`.gitignore` rejects `*.html`, `*.png`, `*.jpg`, `*.trace.json`, `lhr*.json`, and pipeline output directories so a local run cannot add those artifacts by accident.

## Rate limit and robots.txt

- Minimum gap: **5 seconds** between requests the runner starts to the same host (`DELAY = 5.0`). The October 10 pilot observed a wider gap on the wire; the enforced floor is 5 seconds.
- robots.txt is read live, once per audited URL, immediately before Lighthouse, with token `AccesoMayor-LatAm`.
- A 404 or 410, or an HTML document returned at `/robots.txt`, counts as no robots file and the page may be audited. Any other non-200, or a network error, skips the URL (`robots_status_<code>` or `robots_fetch_error:<type>`). A disallow rule for this token skips it with `robots_disallow`.
- `urllib.robotparser` applies the group that matches `AccesoMayor-LatAm`, including a `User-agent: *` group when no specific group matches.
- Rows whose frozen `frame_status` is anything other than `auditable` (including `robots_blocked`) are written as `skipped` with no request and no second robots fetch.

## DataPort package

Include:

- the measurement triple (`pages.csv`, `violations.csv`, `run_log.csv`) from `data/full_run/` on the audit host
- `data/data_dictionary.csv`
- `data/schema.md` and `pipeline/schema/*.schema.json`
- the frozen `data/sampling_frame.csv` and `data/page_frame.csv` so a reader can see which URLs were in scope
- license (MIT, `LICENSE`) and the ethics statement the Data Engineer owns

Leave out HTML, screenshots, page text, and a fresh crawl. This file does not state whether the dataset is registered or published on IEEE DataPort.
