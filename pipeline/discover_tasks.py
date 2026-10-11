"""Find 1-2 public task pages per auditable frame site by following links on the homepage (and sitemap.xml fallback).
No logins/forms. robots.txt checked per candidate path; >=5 s per host. Homepage HTML parsed in memory only; nothing stored but URLs."""
import csv, re, sys, time, threading, urllib.parse, urllib.robotparser, requests, warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
UA = "Mozilla/5.0 (X11; Linux x86_64) AccesoMayor-LatAm/0.1 accessibility-research (+https://github.com/jaime-sql/accesomayor-latam)"
locks = defaultdict(threading.Lock); last = {}
def get(url, method="GET"):
    h = urllib.parse.urlsplit(url).netloc.lower()
    with locks[h]:
        w = last.get(h, 0) + 5.0 - time.time()
        if w > 0: time.sleep(w)
        try: return requests.request(method, url, headers={"User-Agent": UA, "Accept-Language": "es"}, timeout=25, verify=False, allow_redirects=True)
        finally: last[h] = time.time()
KW = {  # keyword -> task category (matched on link text/href, lowercase, accents stripped)
 "requisito": "requirements", "tramite": "how_to", "como ": "how_to", "pasos": "how_to", "cita": "appointments",
 "agenda": "appointments", "tarifa": "fees_rates", "comision": "fees_rates", "tasa": "fees_rates", "costo": "fees_rates",
 "pension": "service_info", "jubila": "service_info", "afiliad": "service_info", "pago": "how_to", "factura": "how_to",
 "dui": "requirements", "cedula": "requirements", "pasaporte": "requirements", "declaracion": "how_to", "preguntas frecuentes": "faq",
 "faq": "faq", "contacto": "contact", "sucursal": "contact", "agencia": "contact", "atencion al cliente": "contact"}
NEWS = re.compile(r"/20\d\d/|noticia|news|blog|comunicado|prensa|/download/|evento|galeria|convocatoria|licitacion|transparencia", re.I)
BAD = re.compile(r"login|ingresar|iniciar-sesion|signin|auth|banca-en-linea|bancaenlinea|\.pdf$|\.docx?$|\.xlsx?$|mailto:|tel:|javascript:|#|whatsapp|facebook|twitter|instagram|youtube|linkedin", re.I)
def norm(s): return s.lower().translate(str.maketrans("áéíóúñ", "aeioun"))
def check(row):
    home = row["final_url"]; p = urllib.parse.urlsplit(home); host = p.netloc
    base = ".".join(host.split(".")[-3:]) if host.split(".")[-2] in ("gob","gov","go","com","org","fi","sa") else ".".join(host.split(".")[-2:])
    rp = urllib.robotparser.RobotFileParser()
    try:
        r = get(f"{p.scheme}://{host}/robots.txt"); rp.parse(r.text.splitlines() if r.status_code == 200 and "<html" not in r.text[:500].lower() else [])
    except Exception: return []
    try: html = get(home).text
    except Exception: return []
    soup = BeautifulSoup(html, "html.parser"); del html
    cands = []
    for a in soup.find_all("a", href=True):
        u = urllib.parse.urljoin(home, a["href"]).split("#")[0]; t = norm(" ".join(a.get_text(" ").split()) + " " + u)
        hu = urllib.parse.urlsplit(u)
        if NEWS.search(u) or hu.path.rstrip("/").split("/")[-1].count("-") > 6: continue
        if hu.scheme not in ("http", "https") or not hu.netloc.lower().endswith(base) or BAD.search(u): continue
        if u.rstrip("/") == home.rstrip("/") or hu.path in ("", "/"): continue
        for k, cat in KW.items():
            if re.search(r"\b" + re.escape(k.strip()), t): cands.append((list(KW).index(k), u, cat, k.strip())); break
    del soup
    cands.sort(); seen = set(); out = []; cats = set()
    for _, u, cat, k in cands:
        if u in seen or cat in cats: continue
        seen.add(u)
        if not rp.can_fetch("AccesoMayor-LatAm", u): continue
        try: r = get(u, "HEAD"); st = r.status_code
        except Exception: continue
        if st in (403, 405, 501):
            try: r = get(u); st = r.status_code
            except Exception: continue
        if st == 200 and "html" in r.headers.get("content-type", "html"):
            out.append(dict(frame_id=row["frame_id"], url=u, final_url=r.url, http_status=st, task_category=cat, found_via=f"homepage link (keyword '{k}')"))
            cats.add(cat)
        if len(out) == 2 or len(seen) > 8: break
    print(row["frame_id"], len(out), flush=True); return out
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["http_status"] == "200" and r["robots_allowed"] in ("true", "no_robots")]
with ThreadPoolExecutor(24) as ex: res = [x for l in ex.map(check, rows) for x in l]
with open(sys.argv[2], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["frame_id","url","final_url","http_status","task_category","found_via"]); w.writeheader(); w.writerows(res)
print("tasks", len(res))
