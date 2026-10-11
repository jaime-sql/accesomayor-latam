# AccesoMayor-LatAm

Accessibility, mobile-performance and Spanish-readability audit dataset of essential-service websites that older adults
use in Latin America (pensions, public health, banking, ID/tax, utilities), with a deep El Salvador stratum.
Entry for the IEEE AgeTech Global Dataset Competition 2026 (Theme 5, Cognitive Health & Digital Inclusion). Work in progress.

No human subjects, no personal data, no page text stored (only metrics and a SHA-256 of visible text);
robots.txt respected and ≥5 s between requests to the same host.

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
| `data/page_frame.csv` | pages to audit (home + task pages), `page_type`, `task_category` |
| `data/schema.md`, `data/data_dictionary.csv` | published schema and per-field dictionary |
| `data/frame_summary.md` | counts, blocked sites, gaps, limitations |
| `pipeline/` | runner (v0.1.3), JSON Schemas, tests, discovery scripts — see `pipeline/README.md` |
| `ml/` | WCAG 2.2 → older-adult barrier map, gold annotation rubric, baseline plan, task-category check |
| `pilot/` | frozen 50-page El Salvador pilot (`pilot.csv`, `pilot_violations.csv`, pipeline v0.1.x) |
| `analytics/pilot_report.md` | pilot quality report |

Note: the frozen pilot predates the v0.1.3 readability sanity gate; one row (SV-049-02) has an out-of-range
Fernández-Huerta score that the current schema would null. See `data/schema.md`.

## License
Code and data: MIT (see `LICENSE`).
