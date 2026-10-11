# AccesoMayor-LatAm: gold-subset annotation rubric (v0.1, draft)

Owner: ML Engineer. Status: draft for Captain review. Column names are provisional: no Data Engineer `schema.md` / `data_dictionary.csv` existed in `/workspace/agetech/` when this was written (Oct 10, 2026). Rename to match the schema when it lands.

## 1. Purpose
Automated tools (axe-core, Lighthouse) detect only part of WCAG. The gold subset gives (a) a human older-adult usability label for benchmarking, (b) an estimate of what automation misses, and (c) the label target for `baseline_plan.md`.

## 2. Unit and size
- Unit: one page (URL + snapshot timestamp) from the pipeline output. Annotators look at the live page in the same emulated mobile viewport the pipeline used. Only labels are stored: no page text, no screenshots containing personal data, no logins.
- Size: 150-200 pages (target 180).

## 3. Sampling (stratified, country x sector)
- Strata: country x sector (pensions, public health, banking, ID/tax, utilities).
- El Salvador: ~60 pages (all 5 sectors, ~12 each), so SV can be reported on its own.
- Other 9 countries: ~13 each (~120); at least 2 per sector where available.
- Within a stratum, draw at random with a fixed seed (recorded), spreading across the axe-violation-count terciles so labels are not all "bad" or all "good".
- At most 2 pages per domain, to limit template clustering.
- Pages that failed to load / blocked by robots.txt are excluded and counted.

## 4. Labels
| Field (provisional) | Type | Definition |
|---|---|---|
| `gold_usability` | ordinal 1-4 | Overall older-adult usability: 1 = blocks the core task, 2 = major difficulty, 3 = minor difficulty, 4 = no notable barrier. Judged against the page's core task (e.g. find pension payment date, book appointment, find branch phone). |
| `gold_task_blocked` | 0/1 | 1 if the core task cannot be completed by an older adult without help. |
| `gold_barrier_<profile>` | 0/1 x 5 | `low_vision`, `dexterity`, `hearing`, `cognitive_load`, `digital_literacy`: a barrier of that profile is present (profiles as in `wcag_older_adult_map.csv`). |
| `gold_barrier_sc` | list | WCAG SC ids of the barriers observed (e.g. `1.4.3;2.5.8`). |
| `gold_notes` | short text | Free text, no PII, no copied page text. |

### Manual checks axe cannot automate (each 0/1/NA)
- `chk_captcha_alt`: CAPTCHA present without a non-visual/non-puzzle alternative (1.1.1, 3.3.8).
- `chk_otp_timeout`: OTP/session timeout without warning or extension (2.2.1, 2.2.6).
- `chk_human_channel`: phone, WhatsApp or in-person alternative visible (3.2.6).
- `chk_plain_language`: core instructions understandable without jargon/abbreviations (3.1.3-3.1.5).
- `chk_error_recovery`: errors explained and correctable; financial/legal steps reviewable (3.3.1, 3.3.3, 3.3.4).
- `chk_reflow_200`: at 200% zoom / 320 px, no loss of content (1.4.4, 1.4.10).
- `chk_target_size`: primary controls easy to tap (2.5.8; manual spot check).
- `chk_link_purpose`: link/button text meaningful ("Haga clic aquí" fails) (2.4.4).
- `chk_consistent_nav`: navigation consistent across the 2 sampled pages of a domain (3.2.3).

## 5. Procedure
1. Annotator guide with 1 worked example per score level (from the pilot).
2. Pilot: 20 pages (8 SV + 12 others, all sectors), both annotators, independently.
3. Compute Cohen's kappa (quadratic-weighted for `gold_usability`, unweighted for binaries). If kappa < 0.6 on `gold_usability` or `gold_task_blocked`, revise the guide and re-pilot 20 new pages.
4. Full set: both annotators label every page independently, blind to each other and to axe/Lighthouse scores.
5. Adjudication: disagreements (any score gap >= 1 on `gold_usability`, or any binary mismatch) go to a third pass: the two annotators discuss with the guide; unresolved cases decided by an adjudicator (Captain or designated). Record pre- and post-adjudication labels; kappa is reported on pre-adjudication labels.
6. Report: kappa with 95% bootstrap CI (1,000 resamples over pages), per label, overall and for SV.
- Target: kappa >= 0.6 (team-set target). Any label below target is reported as such and flagged "low-agreement" in the release, not dropped silently.

## 6. Annotators: DECISION NEEDED (Jaime / Captain)
Options:
- (a) Jaime + one human teammate: real human labels, kappa is meaningful. Needs a 2nd person (team max 4).
- (b) Jaime alone: no inter-annotator kappa possible; could do a test-retest on 20% after a week (intra-rater kappa) and say so.
- (c) Bots as annotators: NOT recommended as "gold"; would have to be described as model labels, which undercuts the dataset claim.
Note: annotators are team members labelling public web pages, not research subjects; no personal data collected about them beyond initials in the provenance log.

## 7. Time estimate (rough, not measured)
Unknown until the pilot; time per page from the pilot x 180 x 2 annotators sets the schedule. Must finish by Sun Oct 25 per the Captain's plan.
