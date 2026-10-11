# AccesoMayor-LatAm: baseline plan (v0.1, draft)

Owner: ML Engineer. Optional for the competition, but it supports the 15% "AI Readiness & Benchmarking" criterion. No results exist yet; nothing here is a measured number.

## 1. Task
- Primary target: `gold_task_blocked` (binary) from the gold subset (150-200 pages).
- Secondary: `gold_usability` (1-4, ordinal) and the 5 `gold_barrier_<profile>` labels (multi-label).
- Alternative target if gold is late: a page-level barrier score from automated data only. This is circular for the rules baseline (it is built from the same map), so it is reported only as a sanity check, never as a benchmark.

## 2. Features (from the Data Engineer's pipeline; names provisional until schema.md exists)
- axe-core: violation counts per WCAG SC (aggregated via `wcag_older_adult_map.csv`), by impact (minor/moderate/serious/critical), nodes affected.
- Lighthouse mobile slow-network: accessibility score, performance score, LCP, TBT, CLS, total bytes.
- textstat Spanish readability: Fernández-Huerta, Szigriszt-Pazos, word/sentence counts (computed on the fly, page text not stored).
- Context: sector (one-hot). Country is NOT a feature (it is the CV group).

## 3. Models
1. Rules baseline (no training): score = sum over violated SCs of (number of profile flags in the map) x impact weight (minor 1, moderate 2, serious 3, critical 4). Rows marked "no source" get weight 0. Threshold for the binary label chosen on training folds only.
2. LightGBM: small trees (num_leaves <= 15, min_data_in_leaf >= 10, strong regularization) because n is small. Class weights for imbalance. Also report logistic regression as a simple learned reference.
3. Trivial baseline: majority class / stratum prior, so gains are visible.

## 4. Evaluation
- Leave-one-country-out CV (10 folds). Each fold: train on 9 countries, test on the held-out one.
- El Salvador reported separately (it is the largest fold, ~60 pages), plus pooled out-of-fold metrics for the other 9.
- Metrics: binary: balanced accuracy, macro F1, AUROC, Brier score; ordinal: quadratic-weighted kappa vs gold; multi-label: macro F1 per profile.
- Uncertainty: Wilson 95% CI for proportions (accuracy, recall); bootstrap 95% CI (1,000 resamples, clustered by domain) for AUROC, F1, kappa. Paired bootstrap for model differences.
- Hyperparameters: nested CV inside the 9 training countries only (inner leave-one-country-out or grouped k-fold by domain). The held-out country is never used for tuning, thresholding, feature selection, or early stopping.
- Fixed seeds; config and fold assignment committed so results reproduce with one command.

## 5. Leakage risks and mitigations
- Same domain or same institution in several countries (e.g. regional banks, shared vendors): group by registrable domain and by parent institution; keep a group in one fold, and flag cross-country groups.
- Templated sites (same CMS/government platform, e.g. shared gov.xx templates): near-duplicate pages leak across folds. Detect via DOM/axe-violation fingerprint similarity; cluster and keep a cluster in one fold, or report results with and without them.
- Same domain within a country: at most 2 pages per domain in gold; bootstrap clustered by domain.
- Annotators seeing automated scores: annotation is blind to axe/Lighthouse (see rubric).
- Map-derived target: the rules baseline uses the same map that defines the profile labels; we report that the multi-label task is partly aligned by construction.
- Temporal: pages change; features and gold labels must come from the same snapshot date (+/- a few days). Record both dates.

## 6. Honest limits
- n is small (150-200 labels; ~13 per non-SV country). Per-country metrics for non-SV folds will have very wide CIs; we report them but do not rank countries on them.
- LightGBM may not beat the rules baseline at this n; that is a valid finding and will be reported as is.
- Gold labels reflect 2 annotators' judgment, not older-adult user testing.

## 7. Deliverables
`baselines/` code + config, `results.csv` (per fold, per model, with CIs), and a short table for the report. Timing: after gold set is done (Captain plan: Oct 19-25).
