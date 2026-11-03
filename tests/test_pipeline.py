import json
import tempfile
import unittest
from pathlib import Path

from insight_hub import cx, dq, feedback, ingest, model, monitoring, pipeline, reports, strategy

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


class Integration(unittest.TestCase):
    def test_five_sources_join_into_unified_view(self):
        views = model.unify(ingest.load_all(RAW))
        self.assertEqual(len(views), 6)
        for v in views.values():
            self.assertTrue(all(v["records"][s] > 0 for s in model.SOURCES), v["client_id"])

    def test_quality_gate_blocks_bad_data_in_production_only(self):
        data = ingest.load_all(RAW)
        data["cx"].append({"client_id": "C099", "date": "2026-10-01", "touchpoint": "App", "score": 5, "churned": 0, "comment": "x"})
        issues = dq.check(data)
        dq.enforce(issues, fail_on_errors=False)  # dev/staging-lenient
        with self.assertRaises(dq.DataQualityError):
            dq.enforce(issues, fail_on_errors=True)


    def test_six_target_clients(self):
        views = model.unify(ingest.load_all(RAW))
        self.assertEqual([v["name"] for _, v in sorted(views.items())],
                         ["CEWE Stiftung & Co. KGaA", "Delticom AG", "Masterflex SE", "hGears AG", "Kölner Pensionskasse VVaG", "Encavis AG"])

    def test_more_data_quality_findings_but_no_errors(self):
        issues = dq.check(ingest.load_all(RAW))
        s = dq.summary(issues)
        self.assertGreaterEqual(s["total"], 10)
        self.assertEqual(s["errors"], 0)  # staging/production gates must still start
        self.assertTrue(all(i["message"] and i["message_de"] for i in issues))
        self.assertEqual(issues[0]["severity"], "warning")


class Analytics(unittest.TestCase):
    def test_sentiment_and_topics(self):
        self.assertEqual(monitoring.sentiment("Lieferung super schnell, toll!")[0], "positive")
        self.assertEqual(monitoring.sentiment("Paket kam verspätet, richtig Ärger")[0], "negative")
        self.assertIn("delivery", monitoring.topics("Lieferung verspätet"))

    def test_emerging_issue_detected_for_c001(self):
        c = monitoring.analyse(ingest.load_social(RAW))
        top = monitoring.emerging_issues(c)[0]
        self.assertEqual((top["client_id"], top["topic"]), ("C001", "delivery"))

    def test_churn_driver_ranking_and_nps_range(self):
        r = ingest.load_cx(RAW)
        self.assertEqual(cx.churn_drivers(r)[0]["touchpoint"], "Support")
        self.assertTrue(-100 <= cx.nps(r) <= 100)

    def test_readiness_is_measured_from_data(self):
        view = {"records": {"crm": 3, "cx": 0, "social": 2}}
        self.assertEqual(strategy.readiness(view, ["crm", "social"]), 5.0)
        self.assertEqual(strategy.readiness(view, ["crm", "cx"]), 3.0)

    def test_win_loss_feedback_creates_actions(self):
        stats = feedback.offer_stats(ingest.load_feedback(RAW))
        self.assertTrue(all("action" in s for s in stats))
        self.assertIn("| Offer |", feedback.backlog_markdown(stats))


class Outputs(unittest.TestCase):
    def test_four_distinct_audience_versions(self):
        ctxs, *_ = pipeline.build_contexts(ROOT)
        texts = {n: fn(ctxs[0]) for n, fn in reports.AUDIENCES.items()}
        self.assertEqual(set(texts), {"executive", "finance", "technical", "pitch_de"})
        self.assertEqual(len(set(texts.values())), 4)
        self.assertNotIn("EUR", texts["pitch_de"])  # prospects never see client financials

    def test_run_writes_all_deliverables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("config", "data"):
                (root / d).mkdir()
            import shutil
            shutil.copytree(ROOT / "config", root / "config", dirs_exist_ok=True)
            shutil.copytree(RAW, root / "data" / "raw")
            res = pipeline.run("staging", root=root)
            out = Path(res["output_dir"])
            for f in ("marketing_onepager.html", "improvement_backlog.md", "analysis.xlsx", "C001/executive.md", "C001/sales_deck.pptx", "C001/technical_appendix.docx"):
                self.assertTrue((out / f).exists(), f)
            self.assertEqual(json.loads((out / "data_quality.json").read_text())[0]["severity"], "warning")


if __name__ == "__main__":
    unittest.main()
