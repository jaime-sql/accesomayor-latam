import sys, os, csv, json, subprocess
HERE = os.path.dirname(__file__); sys.path.insert(0, os.path.join(HERE, ".."))
import audit
from jsonschema import Draft202012Validator
V = Draft202012Validator(json.load(open(os.path.join(HERE, "../schema/pages.schema.json"))))
SITE = dict(frame_id="CR-079", country="CR", sector="banking", site_type="government", org_name="Banco de Costa Rica",
            url="https://www.bancobcr.com/", final_url="https://www.bancobcr.com/", http_status="200", robots_allowed="true")
def test_sampling_frame_defaults():
    r = audit.normalize_row(dict(SITE, frame_status="auditable"))
    assert r["page_id"] == "CR-079-01" and r["page_type"] == "home" and r["task_category"] is None and r["org_group"] == "Banco de Costa Rica"
def test_page_frame_kept():
    r = audit.normalize_row(dict(SITE, page_id="CR-079-02", page_type="task", task_category="faq", org_group="BCR"))
    assert r["page_id"] == "CR-079-02" and r["page_type"] == "task" and r["frame_status"] == "auditable"
def test_skipped_record_valid_and_null():
    for fs in ["bot_protected", "blocked_outside_sv", "robots_blocked", "robots_unreadable", "unreachable", "http_error"]:
        rec = audit.skipped_record(audit.normalize_row(dict(SITE, frame_status=fs)), "2026-10-11T04:00:00Z")
        assert rec["audit_status"] == "skipped" and rec["failure_reason"] == fs
        assert not list(V.iter_errors(rec)), list(V.iter_errors(rec))
        assert list(V.iter_errors(dict(rec, axe_nodes_total=0)))  # metrics must stay null
def test_end_to_end_skips_without_network(tmp_path, monkeypatch):
    """Every frame row -> exactly one output row; non-auditable rows make no request."""
    calls = []
    monkeypatch.setattr(audit, "robots_ok", lambda u: calls.append(u) or (False, "robots_disallow"))
    monkeypatch.setattr(audit.subprocess, "run", lambda *a, **k: calls.append("node") or (_ for _ in ()).throw(AssertionError("no audit")))
    frame = tmp_path / "f.csv"; statuses = ["bot_protected", "blocked_outside_sv", "robots_blocked", "robots_unreadable", "unreachable", "http_error", "auditable"]
    with open(frame, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(SITE) + ["frame_status"]); w.writeheader()
        for i, s in enumerate(statuses): w.writerow(dict(SITE, frame_id=f"CR-{100+i}", frame_status=s))
    monkeypatch.setattr(sys, "argv", ["audit.py", str(frame), str(tmp_path / "out")]); audit.main()
    out = list(csv.DictReader(open(tmp_path / "out/pages.csv")))
    assert [o["frame_id"] for o in out] == [f"CR-{100+i}" for i in range(7)]
    assert [o["audit_status"] for o in out] == ["skipped"] * 6 + ["skipped_robots"]
    assert calls == ["https://www.bancobcr.com/"]  # only the auditable row touched the network (robots check)

def test_legacy_category_mapped_and_valid():
    r = audit.normalize_row(dict(SITE, frame_status="auditable", page_id="CR-079-02", page_type="task", task_category="how_to"))
    assert r["task_category"] == "requirements_howto"
    rec = audit.skipped_record(dict(r, frame_status="bot_protected"), "2026-10-11T04:00:00Z")
    assert not list(V.iter_errors(rec))
    old = dict(rec, task_category="requirements", pipeline_version="0.1.1")   # pre-merge output still validates
    assert not list(V.iter_errors(old))
    assert list(V.iter_errors(dict(rec, task_category="other")))

def test_page_frame_nonauditable_skipped_without_network(tmp_path, monkeypatch):
    """page_frame.csv input: SV-035-02 (robots_blocked) and CR-081-0x (bot_protected) -> one skipped row each, no requests."""
    calls = []
    monkeypatch.setattr(audit, "robots_ok", lambda u: calls.append(u) or (True, None))
    monkeypatch.setattr(audit.subprocess, "run", lambda *a, **k: calls.append("node") or (_ for _ in ()).throw(AssertionError))
    cols = ["page_id", "frame_id", "page_type", "task_category", "task_category_source", "country", "sector", "site_type", "org_name",
            "org_group", "url", "final_url", "http_status", "robots_allowed", "frame_status"]
    rows = [["SV-035-02", "SV-035", "task", "requirements_howto", "keyword", "SV", "id_tax", "government", "Ministerio de Hacienda",
             "Ministerio de Hacienda", "https://www4.mh.gob.sv/portalpagosdgt/", "https://www4.mh.gob.sv/portalpagosdgt/", "200", "false", "robots_blocked"],
            ["CR-081-02", "CR-081", "task", "requirements_howto", "ml_screen", "CR", "id_tax", "government", "TSE", "TSE",
             "https://www.tse.go.cr/cedula.html", "https://www.tse.go.cr/cedula.html", "200", "true", "bot_protected"]]
    f = tmp_path / "pf.csv"
    with open(f, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(cols); w.writerows(rows)
    monkeypatch.setattr(sys, "argv", ["audit.py", str(f), str(tmp_path / "o")]); audit.main()
    out = list(csv.DictReader(open(tmp_path / "o/pages.csv")))
    assert [(o["page_id"], o["audit_status"], o["failure_reason"]) for o in out] == \
        [("SV-035-02", "skipped", "robots_blocked"), ("CR-081-02", "skipped", "bot_protected")]
    assert all(o["axe_nodes_total"] == "" and o["read_fernandez_huerta"] == "" for o in out)
    assert calls == []
