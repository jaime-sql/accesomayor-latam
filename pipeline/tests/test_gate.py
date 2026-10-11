import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import audit
from jsonschema import Draft202012Validator
V = Draft202012Validator(json.load(open(os.path.join(os.path.dirname(__file__), "../schema/pages.schema.json"))))
BASE = dict(page_id="SV-021-01", frame_id="SV-021", page_type="home", org_group="X", country="SV", sector="banking",
            site_type="private", org_name="X", url="https://www.bancoagricola.com/", registrable_domain="bancoagricola.com",
            crawl_ts_utc="2026-10-11T04:00:00Z", pipeline_version="0.1.1")
def test_offsite_redirect():
    st, r = audit.gate("bancoagricola.com", {"final_url": "https://validate.perfdrive.com/?ssa=abc&ip=1.2.3.4"}, "")
    assert st == "failed" and r == "offsite_redirect:perfdrive.com"
def test_same_org_subdomain_not_offsite():
    assert audit.gate("isss.gob.sv", {"final_url": "https://www.isss.gob.sv/x"}, "texto normal")[0] is None
    assert audit.gate("isss.gob.sv", {"final_url": "https://citas.isss.gob.sv/"}, "texto normal")[0] is None
def test_bot_challenge_same_domain():
    for title, body in [("Just a moment...", ""), ("", "Please enable cookies. cf-challenge"), ("Radware Bot Manager", ""),
                        ("", "Request unsuccessful. Incapsula incident ID"), ("", "Verifique que no es un robot: CAPTCHA")]:
        st, r = audit.gate("bancoagricola.com", {"final_url": "https://www.bancoagricola.com/", "title": title}, body)
        assert st == "bot_challenge", (title, body)
def test_captcha_mention_on_real_page_not_flagged():
    body = "Requisitos para el trámite de pensión. " * 60 + " El formulario usa CAPTCHA."
    assert audit.gate("isss.gob.sv", {"final_url": "https://www.isss.gob.sv/", "title": "ISSS"}, body)[0] is None
def test_strip_query_fragment():
    assert audit.clean_url("https://www.x.gob.sv/a/b?token=1&ip=9.9.9.9#frag") == "https://www.x.gob.sv/a/b"
    assert audit.clean_url("https://x.com") == "https://x.com/"
def test_schema_requires_nulls_when_blocked():
    ok = dict(BASE, audit_status="bot_challenge", failure_reason="bot_challenge:just_a_moment", final_url="https://www.bancoagricola.com/")
    assert not list(V.iter_errors(ok))
    assert list(V.iter_errors(dict(ok, axe_nodes_total=0)))          # 0 violations on a blocked page rejected
    assert list(V.iter_errors(dict(ok, final_url="https://x.com/?t=1")))  # query string rejected
    assert not list(V.iter_errors(dict(BASE, audit_status="ok", failure_reason=None, final_url=None, axe_nodes_total=0)))
def test_chrome_error_page_is_load_failure():
    for fu in ("chrome-error://chromewebdata/", "chrome-error://chromewebdata/#x"):
        assert audit.gate("tse.go.cr", {"final_url": fu}, "") == ("failed", "navigation_error:chrome_error_page")
    # Lighthouse-reported error page too
    assert audit.gate("tse.go.cr", {"final_url": None, "lighthouse": {"final_url": "chrome-error://chromewebdata/"}}, "")[0] == "failed"
