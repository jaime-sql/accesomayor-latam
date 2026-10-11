# AccesoMayor-LatAm — published dataset schema (v0.1, draft)

Owner: Data Engineer. Machine-readable source of truth: `pipeline/schema/pages.schema.json` and
`pipeline/schema/violations.schema.json` (JSON Schema 2020-12). Every output row is validated against them by the
runner; a row that fails validation is written with `audit_status=failed` and `failure_reason=schema:...`.
Field-level detail (type, unit, tool + version, range): `data_dictionary.csv`.

## Unit and keys
- **Unit of observation:** one page snapshot = one `page_id` audited at one `crawl_ts_utc`.
- `page_id` = `frame_id` + `-NN` (page index within a frame entry; `01` = the frame URL). Format `SV-001-01`.
- `frame_id` joins to `data/sampling_frame.csv`. `country`, `sector`, `site_type`, `org_name` are copied from the frame
  so each table stands alone.
- `registrable_domain` (e.g. `isss.gob.sv`) is the grouping key for the ML baseline (same domain never split across
  folds; at most 2 gold pages per domain). `country` is the leave-one-country-out group.
- A re-run (test-retest) of the same page keeps `page_id` and gets a new `crawl_ts_utc`; the pair `(page_id, crawl_ts_utc)` is unique.

## Tables
### 1. `pages.csv` — one row per page snapshot
| group | fields | type | null? |
|---|---|---|---|
| ids | page_id, frame_id, page_type (home, task), task_category (requirements_howto, appointments, fees_rates, service_info, faq, contact; null for home), task_category_source (ml_screen, keyword), org_group, country (ISO2: SV GT HN CR MX CO PE CL AR DO), sector (pensions, public_health, banking, id_tax, utilities), site_type (government, private, mixed), org_name, url, final_url, registrable_domain | string/enum | final_url null if not loaded |
| crawl | crawl_ts_utc (ISO 8601 `Z`), audit_status (ok, partial, failed, bot_challenge, skipped_robots, skipped_status), failure_reason, http_status, html_lang | string/int | failure_reason null when ok |
| content | content_sha256 (SHA-256 of visible text, hex) | string | null if no text |
| axe-core | axe_version, axe_rules_violated, axe_nodes_total, axe_nodes_critical, axe_nodes_serious, axe_nodes_moderate, axe_nodes_minor, axe_incomplete_rules | int ≥0 | null if axe failed |
| Lighthouse (mobile, simulated slow 4G, Moto G-class CPU 4x) | lighthouse_version, lh_perf_score, lh_a11y_score (0–1), lh_fcp_ms, lh_lcp_ms, lh_tbt_ms, lh_cls, lh_speed_index_ms, lh_total_bytes | number | null if Lighthouse failed |
| readability (textstat, lang `es`; **task pages only**, null for home) | textstat_version, read_word_count, read_sentence_count, read_fernandez_huerta (0–100), read_szigriszt_pazos (0–100), read_flag (ok, wps_gt_80, score_out_of_range) | number | null if no visible text |
| provenance | chrome_version, pipeline_version | string | — |

### 2. `violations.csv` — long table, one row per (page, axe rule, WCAG SC)
`page_id, axe_rule_id, sc_id, impact, nodes`
- `axe_rule_id`: axe-core rule id (e.g. `color-contrast`, `image-alt`, `target-size`).
- `sc_id`: WCAG success criterion in dotted form **identical to `sc_id` in `ml/wcag_older_adult_map.csv`** (e.g. `1.4.3`, `2.5.8`), parsed from axe tags `wcagXYZ`. A rule mapped to several SCs yields one row per SC; a rule with no WCAG SC tag (best-practice) yields `sc_id` empty — the runner only enables WCAG tags, so this is rare.
- `impact`: minor | moderate | serious | critical. `nodes`: number of failing elements (≥1).
- Rules checked: axe tags `wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa` (WCAG 2.2 A/AA automatable subset).
- Join: `violations.sc_id = wcag_older_adult_map.sc_id` → older-adult profile flags; `violations.page_id = pages.page_id`.

### 3. `run_log.csv` — one row per attempted URL
`page_id, url, crawl_ts_utc, audit_status, failure_reason`. Every skip or failure has a reason
(`robots_disallow`, `robots_status_403`, `robots_fetch_error:*`, `lighthouse:*`, `axe:*`, `runner:*`, `schema:*`).

## Collection rules (enforced in code)
- robots.txt re-checked live for every URL just before auditing (UA token `AccesoMayor-LatAm`); disallowed or
  unreadable (non-200/404) robots.txt → skipped, not audited.
- ≥5 s between any two requests the runner initiates to the same host (robots fetch, Lighthouse load, axe load).
- No logins, no form submission, no clicks beyond page load.

## Task categories (v0.1.2)
Six values: `requirements_howto` (merged from `how_to` + `requirements`), `appointments`, `fees_rates`, `service_info`, `faq`, `contact`.
Assigned by keyword heuristic, then **screened by hand on a stratified sample** (ML, Oct 10, 2026): keyword accuracy was **71%** (37/52, Wilson 95% CI 58–82%) before correction; 14 labels corrected (`task_category_source = ml_screen`) and 1 non-task page removed. **Not gold-standard.** Legacy values `how_to`/`requirements` in v0.1.1 outputs still validate; the runner maps them to `requirements_howto`.

## Readability sanity gate (v0.1.3)
Scores are set to null (word/sentence counts kept) when words per sentence > 80 (sentence segmentation failed — lists, menus, tables without punctuation; e.g. pilot SV-049-02: 1,222 words in 1 "sentence", Fernández-Huerta −1171) or when either score falls outside 0–100. `read_flag` records the reason; schema enforces nulls when `read_flag` ≠ ok.

## Blocked pages (v0.1.1)
- Redirect to a different registrable domain (www/subdomain of the same org is fine) → `audit_status=failed`, `failure_reason=offsite_redirect:<registrable_domain>`, `final_url` null, all metrics null.
- Chrome's own error page (`chrome-error://chromewebdata/`) = load failure → `failed`, `navigation_error:chrome_error_page`, `final_url` null (not an offsite redirect).
- Bot-challenge interstitial (Radware/perfdrive, Cloudflare "Just a moment"/cf-challenge, Incapsula, "Request unsuccessful" anywhere; captcha / "are you a robot" / Akamai / Imperva only in `<title>` or on short pages <1,500 chars) → `audit_status=bot_challenge`, metrics null.
- Blocked = missing (null), never 0 violations; the schema rejects non-null metrics when status is failed/bot_challenge/skipped_*.
- `final_url` always has query string and fragment stripped (schema rejects `?`/`#`).
- Input page list: `data/page_frame.csv` (one row per page).

## Never stored
- Page HTML, visible text, screenshots, Lighthouse JSON reports or traces, cookies, HTTP bodies.
- Any personal data. Visible text exists only in memory long enough to compute readability and its SHA-256, then is discarded.
- axe node selectors/HTML snippets (they can contain page text); only counts per rule.

## Gold labels (ML-owned, joins on `page_id`)
`gold_*` and `chk_*` fields from `ml/gold_rubric.md` live in a separate `gold_labels.csv` keyed by `page_id` (+ `annotator_id`), not in `pages.csv`.
