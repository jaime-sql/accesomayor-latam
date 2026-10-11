# task_category check (Hack ML Engineer, Sat Oct 10 2026 SV)

Stratified sample: up to 8 task pages/category (≥3 SV where available, rest round-robin by country, seed 42), from auditable rows of data/page_frame.csv. Verified from URL, found_via keyword, and <title>/<h1> (fetched once, robots checked for UA AccesoMayor-LatAm, ≥5 s/host, no page text stored). Robots-disallowed/SSL-error pages judged from URL only when unambiguous, else unverifiable. Unverifiable pages excluded from denominators.

| category | n | correct | % | Wilson 95% CI | unverifiable |
|---|---|---|---|---|---|
| appointments | 8 | 6 | 75% | 41–93% | 0 |
| contact | 8 | 8 | 100% | 68–100% | 0 |
| faq | 8 | 8 | 100% | 68–100% | 0 |
| fees_rates | 8 | 5 | 62% | 31–86% | 0 |
| how_to | 6 | 1 | 17% | 3–56% | 2 |
| requirements | 7 | 3 | 43% | 16–75% | 1 |
| service_info | 7 | 6 | 86% | 49–97% | 1 |
| **overall** | 52 | 37 | 71% | 58–82% | 4 |

## Categories under 80% (relabel by hand before gold sampling)
- **appointments** (6/8): PE-115-03→none (institutional events agenda), HN-068-03→contact
- **fees_rates** (5/8): PE-116-03→service_info, CO-106-03→how_to, HN-067-02→service_info
- **how_to** (1/6): SV-024-02→service_info, SV-049-02→contact, PE-108-02→service_info, DO-141-03→service_info, SV-028-02→service_info
- **requirements** (3/7): SV-034-02→service_info, GT-062-02→service_info, CL-119-02→service_info, CR-081-02→how_to

## Other misassignments
- service_info: HN-064-03→faq

## Notes
- Keyword rules over-fire on generic words (pago, tramite, como, tasa, agenda, cedula, dui); service_info absorbs product/index pages. Suggest an `other` category for non-task pages (e.g. PE-115-03 events agenda).
- Small n per category: CIs are wide; treat as screening, not a precise estimate.
- Judgments by one checker; borderline calls noted per row.
