import sys, os, json
HERE = os.path.dirname(__file__); sys.path.insert(0, os.path.join(HERE, ".."))
import audit, textstat
from jsonschema import Draft202012Validator
textstat.set_lang("es")
V = Draft202012Validator(json.load(open(os.path.join(HERE, "../schema/pages.schema.json"))))
BASE = dict(page_id="SV-049-02", frame_id="SV-049", page_type="task", org_group="Claro (América Móvil)", country="SV", sector="utilities",
            site_type="private", org_name="Claro El Salvador", url="https://www.claro.com.sv/x", registrable_domain="claro.com.sv",
            crawl_ts_utc="2026-10-11T04:00:00Z", audit_status="ok", failure_reason=None, final_url=None, pipeline_version="0.1.3")
def test_run_on_sentence_nulled():
    text = " ".join(["Agencia Centro Comercial Metrocentro San Salvador lunes a viernes"] * 150)  # ~1350 words, no punctuation
    r = audit.readability(text)
    assert r["read_flag"] == "wps_gt_80" and r["read_fernandez_huerta"] is None and r["read_szigriszt_pazos"] is None
    assert r["read_word_count"] > 1000
    assert not list(V.iter_errors(dict(BASE, **r)))
def test_normal_text_ok():
    text = "Para pedir su cita, llame al número de atención. Lleve su DUI vigente. La cita es gratuita. " * 5
    r = audit.readability(text)
    assert r["read_flag"] == "ok" and 0 <= r["read_fernandez_huerta"] <= 100
    assert not list(V.iter_errors(dict(BASE, **r)))
def test_schema_rejects_absurd_scores():
    assert list(V.iter_errors(dict(BASE, read_fernandez_huerta=-1171.0, read_flag="ok")))
    assert list(V.iter_errors(dict(BASE, read_fernandez_huerta=50.0, read_flag="wps_gt_80")))
def test_out_of_range_flag(monkeypatch):
    monkeypatch.setattr(textstat, "fernandez_huerta", lambda t: -5.0)
    r = audit.readability("Uno dos tres. Cuatro cinco seis.")
    assert r["read_flag"] == "score_out_of_range" and r["read_fernandez_huerta"] is None
