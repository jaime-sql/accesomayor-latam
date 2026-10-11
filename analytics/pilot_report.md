# AccesoMayor-LatAm: El Salvador pilot report

The pilot ran Sat Oct 10, 2026, 10:00–10:33 PM SV, on pipeline v0.1.1. The source files are `pilot.csv` (50 rows) and `pilot_violations.csv` (177 rows). Task categories come from the corrected `data/page_frame.csv` (v0.1.2), joined on `page_id`. Every number below is computed from those files and nothing else.

## 1. Run outcome
There are 51 El Salvador frame rows in scope: 50 audited, plus SV-035-02, which robots.txt blocks, so it counts as skipped.

| Status | n | Share of 51 | Pages |
|---|---|---|---|
| ok | 46 | 90.2% | |
| bot_challenge | 2 | 3.9% | SV-037-02 (CNR), SV-045-02 (ANDA) |
| failed | 1 | 2.0% | SV-041-02 (MOP). This was a Chrome error page wrongly labeled `offsite_redirect`, and the patch is pending. |
| partial | 1 | 2.0% | SV-022-01 (Banco Cuscatlán home). Lighthouse finished; axe timed out at 60 s. |
| skipped | 1 | 2.0% | SV-035-02 (robots_blocked) |

- **Success rate:** 46 of 50 attempted pages, 92.0%, or 46 of 51 frame rows, 90.2%.
- **By sector (ok/attempted):** banking 15/16, utilities 10/11, id_tax 9/11, pensions 7/7, public_health 5/5. Both bot challenges are on government id_tax and utilities sites.
- **By page type:** task pages 40/43, homepages 6/7.

## 2. Timing
- 32.6 min wall time for 50 pages.
- Per page: median 29 s, range 22–39 s. Excluding the outlier, the mean is 28.9 s over 49 pages.
- One outlier, SV-022-01, took 549 s. That overlapped with a stall on our own computer, so the time can't be blamed on the site alone.
- **Full-run estimate:** about 30 s per page across the auditable rows of `page_frame.csv`. That estimate assumes today's pace and the new 120 s axe timeout, and I'll replace it with the measured time.

## 3. What the pilot shows (46 ok pages; quoted as pilot findings, not population estimates)
- **Lighthouse accessibility score:** median 0.87 (IQR 0.82–0.88, range 0.71–1.00). 37 of 46 pages score below 0.90.
- **axe-core violations:** 44 of 46 pages have at least one WCAG violation. Only SV-044-02 and SV-044-03 have none. The median is 3 rules and 8 affected elements per page. 25 of 46 pages have at least one critical element.
- **Most common rules (pages affected):** link-name 35, color-contrast 22, aria-input-field-name 19, link-in-text-block 18, image-alt 12.
- **Most common WCAG criteria (pages affected):** 4.1.2 Name, Role, Value 39; 2.4.4 Link Purpose 35; 1.4.3 Contrast 22; 1.4.1 Use of Color 18; 1.1.1 Non-text Content 12. Elements are counted once per rule, because a rule can map to two criteria.
- **Speed on a slow mobile connection:** median Lighthouse performance score 0.56. Median Largest Contentful Paint is 9.5 s; the worst is 89.4 s on SV-019-01.
- **Readability (task pages only, Fernández-Huerta):** median 56.6 (IQR 46.3–67.1) across 39 pages, with SV-049-02 excluded (see §4). 23 of 39 pages score below 60, which is roughly "somewhat difficult" or harder.
- **By sector:** median accessibility scores sit between 0.84 (public_health) and 0.87 (banking, pensions). With n=5–16 per sector, these differences are too small to claim.

## 4. Data quality issues found
1. **Readability outlier.** SV-049-02 scored −1171.6, because 1,222 words were counted as a single sentence, probably a table or list with no punctuation. Proposal: null any readability score where the average words per sentence goes above a cutoff such as 100, and flag the row.
2. **Wrong `html_lang`.** 5 ok pages declare English (`en` / `en-US`) on Spanish content (SV-025-02/03, SV-029-02, SV-051-02/03), and 2 declare no language (SV-029-03, SV-033-01). That's a real WCAG 3.1.1 finding, but it could also confuse language-based processing, so keep the declared value as is and add a `content_lang` check if it's cheap.
3. **Mislabeled failure.** On SV-041-02, the `offsite_redirect:chromewebdata` label should be a load failure. The Data Engineer's patch covers it.
4. **Skipped row missing.** SV-035-02 isn't in `pilot.csv` because `--ids` doesn't add skipped rows. The fix is pending, and until then I add it to the count by hand.
5. **Small groups.** Appointments has only 1 ok El Salvador page and contact has 5. Category-level results wait for the full run.
6. **Clean checks.** No duplicate `page_id`, no duplicate content hashes, and no null metrics on ok rows. Non-ok rows are null, never 0. There's no `?` and no IP anywhere, and all rows are schema-valid.

## 5. Metrics mapped to the 6 judging criteria (handbook weights)
| Criterion | Weight | Metric we report (pilot value → full run) |
|---|---|---|
| Problem relevance & impact | 20% | Share of essential-service pages with at least one WCAG violation (44/46), with critical violations (25/46), and below 0.90 accessibility (37/46). The top barriers are mapped to older-adult limitations through ML's `wcag_older_adult_map.csv`. |
| Quality, diversity & representativeness | 25% | Audit success rate (92.0% of attempted pages), coverage by country × sector (cells filled out of 50), counts by status and reason, the share of category labels checked by hand (51 of 112), and gold-subset kappa once it exists. |
| Documentation & reproducibility | 15% | Pinned versions (axe 4.10.3, Lighthouse 12.3.0, Chrome 131, textstat 0.7.4), one-command `make audit`, a data dictionary for every column, and run time per page. |
| Ethics & governance | 15% | 0 pages with stored text, 0 URLs with a query string or IP, 0 robots.txt violations, at least 5 s between requests to a domain (measured minimum 22 s), and 0 login or bypass attempts. Blocked pages are reported and never worked around. |
| Accessibility & usability | 10% | CSV and JSON Schema validation pass rate (100%), stable keys (`page_id` + `crawl_ts_utc`), and a 6-category task taxonomy. |
| AI readiness & benchmarking | 15% | Label balance across the 6 categories and the older-adult barrier profile, the country-held-out split, and ML's rules-vs-gradient-boosting baseline scores, reported only once they're computed. |

## 6. Limitations
- El Salvador only, 50 pages; nothing here generalizes to other countries yet.
- 9 `.gob.sv` sites are `blocked_outside_sv` and need a re-run from inside El Salvador.
- Category labels: 51 of 112 were checked by hand and 61 still come from keywords. The categories aren't gold-standard.
- Automated checks (axe, Lighthouse) catch only part of the WCAG barriers, so the gold subset is needed to judge the rest.
