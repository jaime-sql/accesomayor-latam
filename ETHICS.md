# Ethics and privacy — AccesoMayor-LatAm v1.0

- **Public pages only.** Audits target publicly reachable essential-service websites (pensions, public health, banking, ID/tax, utilities). No logins, forms, or authenticated areas.
- **No human subjects.** No recruitment, interviews, or personal data about older adults.
- **No HTML / DOM / screenshots / cookies stored or published.** The runner keeps only metrics (axe-core, Lighthouse mobile, Spanish readability on task pages) plus a SHA-256 of visible text for change detection; raw text is discarded after hashing.
- **robots.txt respected** with project UA `AccesoMayor-LatAm`; ≥5 s between requests to the same host.
- **Publishable tables:** `pages.csv`, `violations.csv`, `run_log.csv`, frames, and the data dictionary — URLs, crawl timestamps, hashes, and measurements only.
- **License:** CC BY 4.0 (see `LICENSE`) for the published dataset tables and documentation. Pipeline code in the GitHub repo may remain MIT; the DataPort deposit is CC BY 4.0.

Frozen snapshot: box files dated 2026-10-22 SV. No invented rows.
