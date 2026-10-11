"""Verify candidate URLs for the sampling frame.
HEAD then GET fallback (body never read beyond <title> sniff, discarded), robots.txt for root path,
>=5 s between requests to the same domain. Writes data/sampling_frame.csv. Stores no page bodies."""
import csv, re, ssl, sys, time, datetime, threading, urllib.parse, urllib.robotparser, requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (X11; Linux x86_64) AccesoMayor-LatAm/0.1 accessibility-research (+https://github.com/jaime-sql/accesomayor-latam)"
DELAY = 5.0
locks = defaultdict(threading.Lock); last = {}
def polite(url, method, **kw):
    host = urllib.parse.urlsplit(url).netloc.lower()
    with locks[host]:
        wait = last.get(host, 0) + DELAY - time.time()
        if wait > 0: time.sleep(wait)
        try:
            return requests.request(method, url, headers={"User-Agent": UA, "Accept-Language": "es"},
                                    timeout=25, allow_redirects=True, stream=True, **kw)
        finally: last[host] = time.time()
def status(url):
    tls = ""
    for verify in (True, False):
        try:
            r = polite(url, "HEAD", verify=verify)
            if r.status_code in (405, 403, 400, 501) or r.status_code >= 500:
                r.close(); r = polite(url, "GET", verify=verify)
            title = ""
            if r.request.method == "GET" or True:
                pass
            r.close()
            return r.status_code, r.url, tls, ""
        except requests.exceptions.SSLError:
            tls = "tls_cert_invalid"; continue
        except Exception as e:
            return "", "", tls, type(e).__name__
    return "", "", tls, "SSLError"
def title_match(url, org):
    """GET first 64KB, extract <title> in memory, compare tokens with org name; text discarded."""
    try:
        r = polite(url, "GET", verify=False); chunk = next(r.iter_content(65536), b""); r.close()
        m = re.search(rb"<title[^>]*>(.*?)</title>", chunk, re.I | re.S)
        t = m.group(1).decode("utf-8", "ignore").lower() if m else ""
        toks = [w for w in re.findall(r"[a-záéíóúñ]{3,}", org.lower()) if w not in {"del","las","los","para","banco","de"}]
        acr = re.findall(r"\(([A-Z]+)\)", org)
        hit = any(w in t for w in toks) or any(a.lower() in t for a in acr)
        return "yes" if hit else ("no_title" if not t else "no")
    except Exception: return "error"
def robots(url):
    p = urllib.parse.urlsplit(url); ru = f"{p.scheme}://{p.netloc}/robots.txt"
    try:
        r = polite(ru, "GET", verify=False); code = r.status_code
        body = r.content.decode("utf-8", "ignore") if code == 200 else ""; r.close()
    except Exception: return "error", ""
    if code in (404, 410) or (code == 200 and "<html" in body[:500].lower()): return "no_robots", ""
    if code != 200: return f"status_{code}", ""
    rp = urllib.robotparser.RobotFileParser(); rp.parse(body.splitlines())
    ok = rp.can_fetch("AccesoMayor-LatAm", f"{p.scheme}://{p.netloc}/") and rp.can_fetch("AccesoMayor-LatAm", url)
    return ("true" if ok else "false"), ""
GOV = re.compile(r"\.(gob|gov|go|gub|gouv|mil)\.[a-z]{2}$|\.gob$|\.fi\.cr$|\.sa\.cr$")
SITE = {"public": "government", "private": "private", "cooperative": "mixed"}
SECT = {"health": "public_health"}
def check(i_row):
    i, row = i_row
    st, final, tls, err = status(row["url"])
    host = urllib.parse.urlsplit(final or row["url"]).netloc.lower()
    tm = title_match(final, row["institution"]) if st == 200 else ""
    rob, _ = robots(final or row["url"]) if (st or final) else ("error", "")
    if GOV.search(host): src = f"government/official TLD ({host}); reachable"
    else: src = f"institution's own domain ({host}); page <title> names org: {tm or 'n/a'}"
    notes = ";".join(x for x in [tls, err, f"title_match={tm}" if tm else ""] if x)
    return dict(frame_id=f"{row['country']}-{i:03d}", country=row["country"], sector=SECT.get(row["sector"], row["sector"]),
        site_type=SITE[row["org_type"]], org_name=row["institution"], url=row["url"], source_of_url=src,
        http_status=st, final_url=final, robots_allowed=rob,
        robots_checked_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), notes=notes)
if __name__ == "__main__":
    rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
    with ThreadPoolExecutor(24) as ex: out = list(ex.map(check, enumerate(rows, 1)))
    cols = list(out[0])
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    print("done", len(out))
    