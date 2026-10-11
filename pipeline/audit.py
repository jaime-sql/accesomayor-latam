"""AccesoMayor-LatAm audit runner. Usage: audit.py PAGE_FRAME.csv (data/page_frame.csv) OUTDIR [--limit N] [--country SV] [--ids SV-001,SV-002]
Per URL: re-check robots.txt live, enforce >=5 s per domain, run audit_page.mjs (Lighthouse + axe-core),
compute Spanish readability in memory from visible text, hash it, discard it. Validates every row against JSON Schema."""
import argparse, re, csv, datetime, hashlib, json, os, subprocess, sys, time, urllib.parse, urllib.robotparser
import requests, textstat
from importlib.metadata import version as pv
from jsonschema import Draft202012Validator
HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_VERSION = "0.1.3"
CHROME = os.environ.get("CHROME_PATH", os.path.join(HERE, "browsers/chrome/linux-131.0.6778.204/chrome-linux64/chrome"))
UA = "AccesoMayor-LatAm"; DELAY = 5.0
VP = Draft202012Validator(json.load(open(os.path.join(HERE, "schema/pages.schema.json"))))
VV = Draft202012Validator(json.load(open(os.path.join(HERE, "schema/violations.schema.json"))))
last = {}

# strong markers: vendor interstitials, matched anywhere in title/body
CHALLENGE = re.compile(r"radware|perfdrive|just a moment|cf-challenge|challenge-platform|attention required.{0,20}cloudflare|"
    r"access denied.{0,40}reference #|incapsula|_incapsula_resource|request unsuccessful", re.I)
# weak markers (captcha / "are you a robot" / Akamai / Imperva): only on short interstitial pages or in <title>,
# so a genuine page that merely mentions CAPTCHA in a form is not discarded
CHALLENGE_WEAK = re.compile(r"captcha|are you a robot|verify you are (a )?human|verifi\w* que (eres|es|no es) (un )?(humano|robot)|"
    r"no (eres|soy) un robot|akamai|imperva|bot (detection|protection|manager)", re.I)
def clean_url(u):
    """Drop query string and fragment (may carry tokens, crawler IP)."""
    if not u: return u
    p = urllib.parse.urlsplit(u); return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path or "/", "", ""))
def gate(rec_domain, res, text):
    """v0.1.1 bot-challenge / offsite gate. Returns (status, reason) or (None, None) if the page is genuine."""
    for fu in (res.get("final_url"), (res.get("lighthouse") or {}).get("final_url")):
        sp = urllib.parse.urlsplit(fu or "")
        # Chrome's own error page (chrome-error://chromewebdata/) means navigation failed, not a redirect.
        if sp.scheme == "chrome-error" or sp.netloc == "chromewebdata": return "failed", "navigation_error:chrome_error_page"
        h = sp.netloc
        if h and reg_domain(h) != rec_domain: return "failed", f"offsite_redirect:{reg_domain(h)}"
    probe = (res.get("title") or "") + "\n" + (text or "")[:5000]
    m = CHALLENGE.search(probe)
    if not m and (len((text or "").strip()) < 1500 or CHALLENGE_WEAK.search(res.get("title") or "")):
        m = CHALLENGE_WEAK.search(probe)
    if m: return "bot_challenge", "bot_challenge:" + re.sub(r"[^a-z_-]", "_", m.group(0).lower())[:40]
    return None, None
def pace(host):
    w = last.get(host, 0) + DELAY - time.time()
    if w > 0: time.sleep(w)
    last[host] = time.time()
def reg_domain(host):
    parts = host.lower().split(".")
    if parts[0] == "www": parts = parts[1:]
    n = 3 if len(parts) >= 3 and len(parts[-1]) == 2 and parts[-2] in {"gob","gov","go","com","org","fi","sa","net","edu"} else 2
    return ".".join(parts[-n:])
def robots_ok(url):
    p = urllib.parse.urlsplit(url); pace(p.netloc)
    try:
        r = requests.get(f"{p.scheme}://{p.netloc}/robots.txt", headers={"User-Agent": UA}, timeout=20, verify=False)
    except Exception as e: return False, f"robots_fetch_error:{type(e).__name__}"
    if r.status_code in (404, 410) or "<html" in r.text[:500].lower(): return True, None
    if r.status_code != 200: return False, f"robots_status_{r.status_code}"
    rp = urllib.robotparser.RobotFileParser(); rp.parse(r.text.splitlines())
    return (True, None) if rp.can_fetch(UA, url) else (False, "robots_disallow")
def sc_from_tag(t):  # 'wcag1410' -> '1.4.10'
    d = t[4:]; return f"{d[0]}.{d[1]}.{d[2:]}"
LEGACY_CAT = {"how_to": "requirements_howto", "requirements": "requirements_howto"}
MAX_WPS = 80  # words per sentence above this = sentence segmentation failed (lists/menus without punctuation)
def readability(text):
    """Spanish readability with sanity gate. Scores are nulled (counts kept) when words/sentence > MAX_WPS
    or a score falls outside the 0-100 scale; read_flag records why."""
    w, s = textstat.lexicon_count(text), textstat.sentence_count(text)
    out = dict(read_word_count=w, read_sentence_count=s, read_fernandez_huerta=None, read_szigriszt_pazos=None)
    if s == 0 or w / s > MAX_WPS: return dict(out, read_flag="wps_gt_80")
    fh, sp = round(textstat.fernandez_huerta(text), 2), round(textstat.szigriszt_pazos(text), 2)
    if not (0 <= fh <= 100 and 0 <= sp <= 100): return dict(out, read_flag="score_out_of_range")
    return dict(out, read_fernandez_huerta=fh, read_szigriszt_pazos=sp, read_flag="ok")
def normalize_row(r):
    """Accept sampling_frame.csv (one row per site) or page_frame.csv (one row per page)."""
    r = dict(r)
    if not r.get("page_id"): r["page_id"] = r["frame_id"] + "-01"
    if not r.get("page_type"): r["page_type"] = "home"
    r["task_category"] = LEGACY_CAT.get(r.get("task_category") or "", r.get("task_category") or None)
    r["task_category_source"] = r.get("task_category_source") or None
    r["org_group"] = r.get("org_group") or r["org_name"]
    if not r.get("frame_status"):  # page_frame rows: derive from the page-level check
        r["frame_status"] = "auditable" if str(r.get("http_status")) == "200" and r.get("robots_allowed") in ("true", "no_robots") \
            else ("robots_blocked" if r.get("robots_allowed") == "false" else "http_error")
    return r
def skipped_record(r, crawl):
    """Row for a non-auditable frame entry: no network request, all metrics null."""
    u = r.get("final_url") or r["url"]
    return dict(page_id=r["page_id"], frame_id=r["frame_id"], page_type=r["page_type"], org_group=r["org_group"],
                country=r["country"], sector=r["sector"], site_type=r["site_type"], org_name=r["org_name"], url=r["url"],
                final_url=None, registrable_domain=reg_domain(urllib.parse.urlsplit(u).netloc), crawl_ts_utc=crawl,
                audit_status="skipped", failure_reason=r["frame_status"], pipeline_version=PIPELINE_VERSION,
                **({"task_category": r["task_category"], "task_category_source": r["task_category_source"]} if r["task_category"] else {}))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("frame"); ap.add_argument("out")
    ap.add_argument("--limit", type=int); ap.add_argument("--country"); ap.add_argument("--ids")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rows = [normalize_row(r) for r in csv.DictReader(open(a.frame))]
    if a.country: rows = [r for r in rows if r["country"] == a.country]
    if a.ids: ids = a.ids.split(","); rows = [r for r in rows if r["page_id"] in ids or r["frame_id"] in ids]
    if a.limit: rows = rows[:a.limit]
    textstat.set_lang("es")
    vers = dict(textstat=pv("textstat"))
    pages, viols, fails = [], [], []
    for r in rows:
        crawl = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if r["frame_status"] != "auditable":
            rec = skipped_record(r, crawl); pages.append(rec); print(rec["page_id"], "skipped", rec["failure_reason"], flush=True); continue
        url = r["url"]; host = urllib.parse.urlsplit(url).netloc
        rec = dict(page_id=r["page_id"], frame_id=r["frame_id"], page_type=r["page_type"], task_category=r["task_category"], task_category_source=r["task_category_source"], org_group=r["org_group"], country=r["country"], sector=r["sector"],
                   site_type=r["site_type"], org_name=r["org_name"], url=url, final_url=None,
                   registrable_domain=reg_domain(host), crawl_ts_utc=crawl, audit_status="ok", failure_reason=None,
                   textstat_version=vers["textstat"], pipeline_version=PIPELINE_VERSION)
        ok, why = robots_ok(url)
        if not ok:
            rec.update(audit_status="skipped_robots", failure_reason=why)
        else:
            pace(host)
            try:
                p = subprocess.run(["node", os.path.join(HERE, "audit_page.mjs"), url, CHROME], capture_output=True, text=True, timeout=300)
                res = json.loads(p.stdout)
            except Exception as e:
                res = {"errors": [f"runner:{type(e).__name__}"]}
            last[host] = time.time()
            text = res.pop("visible_text", None) or ""
            lh, ax = res.get("lighthouse"), res.get("axe")
            gst, greason = gate(rec["registrable_domain"], res, text)
            if gst:  # blocked page: metrics are missing (null), never 0
                if greason.startswith(("offsite_redirect", "navigation_error")): res["final_url"] = None  # store only the registrable domain (in reason)
                res = {"http_status": res.get("http_status"), "final_url": res.get("final_url")}
                text, lh, ax = "", None, None
            rec.update(http_status=res.get("http_status"), final_url=clean_url(res.get("final_url")), html_lang=res.get("lang"),
                       chrome_version="131.0.6778.204")
            if text.strip():
                rec["content_sha256"] = hashlib.sha256(text.encode()).hexdigest()
            if text.strip() and rec["page_type"] == "task":  # homepages are menu-dominated: readability not reported
                rec.update(readability(text))
            del text  # visible text is never persisted
            if lh:
                rec.update(lighthouse_version=lh["version"], lh_perf_score=lh["perf"], lh_a11y_score=lh["a11y"],
                           lh_fcp_ms=lh["fcp_ms"], lh_lcp_ms=lh["lcp_ms"], lh_tbt_ms=lh["tbt_ms"], lh_cls=lh["cls"],
                           lh_speed_index_ms=lh["si_ms"], lh_total_bytes=lh["total_bytes"])
            if ax:
                imp = {k: 0 for k in ("critical", "serious", "moderate", "minor")}
                for v in ax["violations"]:
                    if v["impact"] in imp: imp[v["impact"]] += v["nodes"]
                    for sc in ([sc_from_tag(t) for t in v["tags"]] or [None]):
                        viols.append(dict(page_id=rec["page_id"], axe_rule_id=v["id"], sc_id=sc, impact=v["impact"], nodes=v["nodes"]))
                rec.update(axe_version=ax["version"], axe_rules_violated=len(ax["violations"]),
                           axe_nodes_total=sum(v["nodes"] for v in ax["violations"]), axe_incomplete_rules=ax["incomplete"],
                           **{f"axe_nodes_{k}": n for k, n in imp.items()})
            errs = res.get("errors", [])
            if gst:
                rec["audit_status"], rec["failure_reason"] = gst, greason
            elif errs:
                rec["failure_reason"] = ";".join(errs)[:200]
                rec["audit_status"] = "partial" if (lh or ax) else "failed"
        rec = {k: v for k, v in rec.items() if v is not None or k in ("final_url", "failure_reason")}
        errs = [e.message for e in VP.iter_errors(rec)]
        if errs: rec["audit_status"] = "failed"; rec["failure_reason"] = ("schema:" + errs[0])[:200]
        pages.append(rec); print(rec["page_id"], rec["audit_status"], rec.get("failure_reason"), flush=True)
    bad = [e.message for v in viols for e in VV.iter_errors(v)]
    if bad: sys.exit(f"violations schema errors: {bad[:3]}")
    cols = list(json.load(open(os.path.join(HERE, "schema/pages.schema.json")))["properties"])
    with open(os.path.join(a.out, "pages.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(pages)
    with open(os.path.join(a.out, "violations.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["page_id", "axe_rule_id", "sc_id", "impact", "nodes"]); w.writeheader(); w.writerows(viols)
    with open(os.path.join(a.out, "run_log.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["page_id", "url", "crawl_ts_utc", "audit_status", "failure_reason"])
        for p in pages: w.writerow([p["page_id"], p["url"], p["crawl_ts_utc"], p["audit_status"], p.get("failure_reason")])
if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore"); main()
