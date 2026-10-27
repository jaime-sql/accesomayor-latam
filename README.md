# AccesoMayor-LatAm

**v1.0 freeze** for the IEEE AgeTech Global Dataset Competition 2026 (Theme 5, Cognitive Health & Digital Inclusion), ready for IEEE DataPort.

Accessibility, mobile-performance and Spanish-readability audit dataset of essential-service websites that older adults
use in Latin America (pensions, public health, banking, ID/tax, utilities), with a deep El Salvador stratum.

v1.0 publishes the frozen Oct 22 SV snapshot (pipeline v0.1.3; crawl window 2026-10-11T04:37:41Z to 2026-10-11T08:11:09Z). The tables below are that snapshot.

No human subjects, no personal data, no page text stored (only metrics and a SHA-256 of visible text);
robots.txt respected and ≥5 s between requests to the same host. See [ETHICS.md](ETHICS.md).

## DataPort upload

One file for the deposit: [`publish/AccesoMayor-LatAm-v1.0.zip`](publish/AccesoMayor-LatAm-v1.0.zip).

The zip is the DataPort package (CC BY 4.0, including the `LICENSE` file at the root of the zip). It is built from these repository paths:

| path | rows (excl. header) | notes |
|---|---|---|
| `data/sampling_frame.csv` | 148 | sites |
| `data/page_frame.csv` | 225 | home + task pages |
| `data/page_frame_dropped.csv` | 27 | curation drops |
| `data/full_run/pages.csv` | 225 | audited page snapshots |
| `data/full_run/violations.csv` | 650 | axe rule × WCAG SC |
| `data/full_run/run_log.csv` | 225 | one row per attempted URL |
| `data/data_dictionary.csv` | 58 | field dictionary |
| `data/schema.md`, `data/frame_summary.md` | — | published schema and frame notes |
| `ETHICS.md` | — | public pages only; no HTML dumps |

The zip also carries `pipeline/schema/*.json`, the pilot tables, `ml/wcag_older_adult_map.csv`, and `analytics/full_run_report.md`. Upload `publish/AccesoMayor-LatAm-v1.0.zip` to DataPort. Its license is CC BY 4.0, separate from the MIT license on pipeline code in this repository.

## Run (one command)
```bash
cd pipeline
./run.sh ../data/page_frame.csv out/          # or: make audit
./run.sh ../data/page_frame.csv out/ --ids SV-034-02,SV-008-03   # subset
.venv/bin/python -m pytest -q                   # tests
```
Requires Node 20 and Python 3.12+. `run.sh` installs pinned deps (axe-core 4.10.3, Lighthouse 12.3.0,
puppeteer-core 23.11.1, Chrome for Testing 131.0.6778.204, textstat 0.7.4) and writes `pages.csv`, `violations.csv`, `run_log.csv`.

## Layout
| path | contents |
|---|---|
| `data/sampling_frame.csv` | 148 sites, 10 countries × 5 sectors, with HTTP/robots check and `frame_status` |
| `data/page_frame.csv` | 225 pages to audit (home + task pages), `page_type`, `task_category` |
| `data/page_frame_dropped.csv` | 27 curation drops |
| `data/full_run/pages.csv` | frozen v1.0 page snapshots (225) |
| `data/full_run/violations.csv` | frozen v1.0 axe rule × WCAG SC rows (650) |
| `data/full_run/run_log.csv` | frozen v1.0 run log, one row per attempted URL (225) |
| `data/schema.md`, `data/data_dictionary.csv` | published schema and per-field dictionary (58 fields) |
| `data/frame_summary.md` | counts, blocked sites, gaps, limitations |
| `pipeline/` | runner (v0.1.3), JSON Schemas, tests, discovery scripts — see `pipeline/README.md` |
| `ml/` | WCAG 2.2 → older-adult barrier map, gold annotation rubric, baseline plan, task-category check |
| `pilot/` | frozen 50-page El Salvador pilot (`pilot.csv`, `pilot_violations.csv`, pipeline v0.1.x) |
| `analytics/pilot_report.md` | pilot quality report |
| `analytics/full_run_report.md` | notes on the frozen full-frame audit |
| `ETHICS.md` | public pages only; metrics, URL, and hash; no HTML/DOM/screenshots/cookies |
| `publish/AccesoMayor-LatAm-v1.0.zip` | DataPort upload (CC BY 4.0) |

Note: the frozen pilot predates the v0.1.3 readability sanity gate; one row (SV-049-02) has an out-of-range
Fernández-Huerta score that the current schema would null. See `data/schema.md`.

## License
- Pipeline code in this repository: MIT (`LICENSE`).
- Published dataset tables and the IEEE DataPort deposit: CC BY 4.0. The deposit copy is the `LICENSE` file inside [`publish/AccesoMayor-LatAm-v1.0.zip`](publish/AccesoMayor-LatAm-v1.0.zip). See [ETHICS.md](ETHICS.md).
