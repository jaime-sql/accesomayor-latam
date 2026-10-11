# Sampling frame summary (v0.2, Sat Oct 10, 2026 SV)

Files: `sampling_frame.csv` (1 row per site, 148 rows), `page_frame.csv` (1 row per page, 226 rows: home + task),
`page_frame_dropped.csv` (26 discovered links removed by curation, with reason).
Re-checked Sat Oct 10, ~10:10 PM SV with `check_frame.py` (HEAD → GET, project UA, ≥5 s/host, robots for root + URL, no bodies stored).
Countries: SV + GT, HN, CR, MX, CO, PE, CL, AR, DO. SV-002 and SV-012 (guessed ISSS sub-paths, 404) were dropped.

## Sites in frame
| country | pensions | public_health | banking | id_tax | utilities | total |
|---|---|---|---|---|---|---|
| SV | 9 | 9 | 13 | 10 | 10 | 51 |
| GT | 2 | 1 | 3 | 2 | 2 | 10 |
| HN | 2 | 1 | 3 | 2 | 2 | 10 |
| CR | 2 | 2 | 3 | 2 | 2 | 11 |
| MX | 3 | 2 | 4 | 2 | 1 | 12 |
| CO | 2 | 2 | 3 | 2 | 2 | 11 |
| PE | 2 | 2 | 3 | 2 | 2 | 11 |
| CL | 2 | 2 | 3 | 2 | 2 | 11 |
| AR | 2 | 1 | 3 | 2 | 2 | 10 |
| DO | 2 | 2 | 3 | 2 | 2 | 11 |
| **all** | 28 | 24 | 41 | 28 | 27 | 148 |

## Auditable sites (frame_status = auditable)
| country | pensions | public_health | banking | id_tax | utilities | total |
|---|---|---|---|---|---|---|
| SV | 4 | 4 | 12 | 9 | 8 | 37 |
| GT | 2 | 0 | 3 | 1 | 1 | 7 |
| HN | 2 | 1 | 3 | 2 | 1 | 9 |
| CR | 1 | 1 | 1 | 1 | 2 | 6 |
| MX | 3 | 2 | 3 | 1 | 0 | 9 |
| CO | 1 | 1 | 3 | 1 | 1 | 7 |
| PE | 2 | 2 | 3 | 2 | 0 | 9 |
| CL | 2 | 1 | 2 | 2 | 0 | 7 |
| AR | 0 | 1 | 3 | 2 | 2 | 8 |
| DO | 2 | 2 | 3 | 2 | 2 | 11 |
| **all** | 19 | 15 | 36 | 23 | 17 | 110 |

frame_status: {'auditable': 110, 'blocked_outside_sv': 9, 'unreachable': 7, 'robots_blocked': 12, 'robots_unreadable': 1, 'http_error': 1, 'bot_protected': 8}

## Task pages (page_type = task, HTTP 200 + robots allowed)
| country | pensions | public_health | banking | id_tax | utilities | total |
|---|---|---|---|---|---|---|
| SV | 6 | 4 | 14 | 9 | 10 | 43 |
| GT | 3 | 0 | 0 | 2 | 1 | 6 |
| HN | 4 | 1 | 3 | 2 | 0 | 10 |
| CR | 1 | 0 | 0 | 0 | 2 | 3 |
| MX | 0 | 0 | 2 | 0 | 0 | 2 |
| CO | 0 | 1 | 2 | 2 | 2 | 7 |
| PE | 4 | 4 | 2 | 3 | 0 | 13 |
| CL | 2 | 1 | 0 | 0 | 0 | 3 |
| AR | 0 | 0 | 4 | 2 | 3 | 9 |
| DO | 3 | 2 | 3 | 2 | 4 | 14 |
| **all** | 23 | 13 | 30 | 22 | 22 | 110 |

Task categories (v0.1.2, 6 values; keyword-assigned, hand-screened on a stratified sample by ML: 71% keyword accuracy before correction; not gold-standard), auditable: {'requirements_howto': 36, 'service_info': 19, 'fees_rates': 12, 'faq': 26, 'appointments': 7, 'contact': 10}.
Not auditable task pages: CR-081-02 (bot_protected), CR-081-03 (bot_protected), MX-088-02 (unreachable), SV-035-02 (robots_blocked).
Auditable home pages: 110. Pages in page_frame.csv: 225.

## org_group (cross-country/parent brands; others = org_name)
BAC, Banco Atlántida, Banco Industrial (Corporación BI), CCSS, Claro (América Móvil), Davivienda, Enel, IMSS, ISSS, Movistar (Telefónica), Promerica, Tigo (Millicom).

## Limitations
### Blocked / excluded sites (kept in frame, never audited; runner writes `skipped` rows)
- **blocked_outside_sv** (9): SV-003 Instituto Salvadoreño de Previsión Social de la FAES (IPSFA); SV-004 INPEP; SV-010 Bienestar Magisterial; SV-013 Hospital Rosales; SV-014 Hospital Nacional de Niños Benjamín Bloom; SV-015 Dirección Nacional de Medicamentos (DNM); SV-016 Doctor SV (telemedicina); SV-018 Hospital Militar Central; SV-053 CEPA
- **bot_protected** (8): SV-050 Tigo El Salvador; GT-063 Tigo Guatemala; HN-073 Tigo Honduras; CR-079 Banco de Costa Rica; CR-081 Tribunal Supremo de Elecciones; CO-107 Enel Colombia; CL-122 MINSAL Chile; CL-128 Enel Chile
- **http_error** (1): SV-036 Portal de servicios Hacienda
- **robots_blocked** (12): SV-007 Instituto Salvadoreño de Pensiones (ISP); GT-056 MSPAS; GT-061 SAT Guatemala; MX-094 SAT; MX-096 CFE; CO-098 Porvenir; CO-100 Nueva EPS; CO-104 Registraduría Nacional; PE-117 Sedapal; PE-118 Luz del Sur; CL-129 Aguas Andinas; AR-130 ANSES
- **robots_unreadable** (1): SV-030 Banco Central de Reserva
- **unreachable** (7): SV-005 AFP Crecer; CR-074 CCSS; CR-077 EDUS (CCSS); CR-078 Banco Nacional de Costa Rica; MX-091 Banorte; CL-125 Banco Central de Chile; AR-131 PAMI

CR-081 TSE Costa Rica: whole site behind Radware Bot Manager (perfdrive script on home and cédula page; contactenos redirects to validate.perfdrive.com; pilot CR-081-02 → offsite_redirect:perfdrive.com). Site row and all 3 pages marked bot_protected.

`blocked_outside_sv`: these .gob.sv sites reset the TLS handshake from the (non-SV) audit box — likely geo/IP filtering. Not bypassed; re-check from an El Salvador network.

### Empty cells — no auditable site
GT public_health, MX utilities, PE utilities, CL utilities, AR pensions

### Empty cells — no task page
GT public_health, GT banking, HN utilities, CR public_health, CR banking, CR id_tax, MX pensions, MX public_health, MX id_tax, MX utilities, CO pensions, PE utilities, CL banking, CL id_tax, CL utilities, AR pensions, AR public_health

### Auditable sites with no task page found (42)
AR-132, AR-134, AR-137, CL-120, CL-123, CL-124, CL-126, CL-127, CO-097, CO-102, CO-103, CR-076, CR-080, CR-082, CR-084, DO-142, DO-144, DO-147, GT-057, GT-058, GT-059, HN-069, HN-070, HN-072, MX-085, MX-086, MX-087, MX-088, MX-089, MX-092, MX-093, MX-095, PE-113, PE-114, SV-019, SV-022, SV-023, SV-033, SV-039, SV-040, SV-043, SV-046. Typical causes: JS-rendered menus (links not in initial HTML), all candidate links were news/PDF/login/off-domain, or curation dropped them. Left empty, not padded.

### Other caveats
- Task pages are only those linked from the homepage HTML; categories are keyword heuristics and need a human pass before gold annotation.
- 22 homepages had empty/brand-only `<title>`; official status rests on domain knowledge (flagged in `notes`).
- Readability is reported for task pages only (homepages are menu-dominated).
- MX is thin on task pages (gob.mx is JS-rendered; IMSS trámite page timed out on re-check).
