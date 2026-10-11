"""Build data/page_frame.csv (one row per page: home + task) from sampling_frame.csv + curated task_candidates.csv,
re-checking every URL's HTTP status and robots.txt with check_frame's polite functions (>=5 s per host)."""
import csv, datetime, sys, warnings, urllib.parse
from concurrent.futures import ThreadPoolExecutor
warnings.filterwarnings("ignore")
import check_frame as cf
DROP = {  # manual curation: not an older-adult citizen task page, session token in URL, app/process endpoint, or site bot-protected
 "https://www.gob.mx": "portal root, not a task page", "jsessionid": "session token in URL",
 "loader.php": "application process endpoint", "bcrcita.bancobcr.com": "CR-079 bot_protected", "bancobcr.com/wps": "CR-079 bot_protected",
 "reportedecompras": "app endpoint", "promociones/walmart": "promotion", "agenda-regulatoria": "regulatory agenda, not appointments",
 "acreditacion-de-promotor": "industry procedure", "tramites-empresariales": "business procedure", "requisitos-trimestrales-aco": "industry",
 "contratacion-bienes-servicios": "procurement", "tasa-de-interes-lider": "monetary policy", "modernizacion-del-sistema-de-pagos": "interbank",
 "quienes-pueden-ser-afiliados": "interbank", "estados-financieros": "financial statements", "sistema-de-interconexion-de-pagos": "interbank",
 "area-de-etica-en-salud": "not a citizen task", "citacion-a-notificacion": "legal notices", "adquirencia-pos": "merchant service",
 "conocenos": "about page", "grandes-clientes": "business customers", "atlantida-tap": "merchant service", "senadis": "not a citizen task"}
RECAT = {"comisiones-medicas": "service_info", "contacto/": "contact"}
def main():
    F = {r["frame_id"]: r for r in csv.DictReader(open(sys.argv[1]))}
    T = list(csv.DictReader(open(sys.argv[2])))
    pages, dropped = [], []
    for fid, f in F.items():
        if f["frame_status"] != "auditable": continue
        pages.append(dict(f, page_id=f"{fid}-01", page_type="home", task_category="", found_via="sampling frame", url=f["final_url"] or f["url"]))
        n = 1
        for t in [t for t in T if t["frame_id"] == fid]:
            why = next((v for k, v in DROP.items() if k in t["final_url"] or t["final_url"].rstrip("/") == k), None)
            if why: dropped.append((fid, t["final_url"], why)); continue
            cat = next((v for k, v in RECAT.items() if k in t["final_url"]), t["task_category"])
            n += 1
            pages.append(dict(f, page_id=f"{fid}-{n:02d}", page_type="task", task_category=cat, found_via=t["found_via"], url=t["final_url"]))
    def chk(p):
        st, final, tls, err = cf.status(p["url"]); rob, _ = cf.robots(final or p["url"]) if st else ("false", "")
        if rob in ("error",) or rob.startswith("status_"): rob = "false"
        fp = urllib.parse.urlsplit(final or "")
        return dict(page_id=p["page_id"], frame_id=p["frame_id"], page_type=p["page_type"], task_category=p["task_category"],
            country=p["country"], sector=p["sector"], site_type=p["site_type"], org_name=p["org_name"], org_group=p["org_group"],
            url=p["url"], final_url=urllib.parse.urlunsplit((fp.scheme, fp.netloc, fp.path, "", "")) if final else "",
            http_status=st, robots_allowed=rob, checked_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            found_via=p["found_via"], notes=";".join(x for x in (tls, err) if x))
    with ThreadPoolExecutor(24) as ex: out = list(ex.map(chk, pages))
    with open(sys.argv[3], "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    with open(sys.argv[3].replace(".csv", "_dropped.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["frame_id", "url", "reason"]); w.writerows(dropped)
    print("pages", len(out), "dropped", len(dropped))
if __name__ == "__main__": main()
