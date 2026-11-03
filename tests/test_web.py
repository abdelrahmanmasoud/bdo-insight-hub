import json
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from insight_hub import decks, server

ROOT = Path(__file__).resolve().parents[1]


class Web(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv, cls.app = server.create_server("dev", port=0, root=ROOT)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def get(self, p):
        with urllib.request.urlopen(self.base + p) as r:
            return r.read(), r.headers["Content-Type"]

    def test_pages_and_api(self):
        self.assertIn(b"Insight Hub", self.get("/")[0])
        self.assertEqual(json.loads(self.get("/healthz")[0])["status"], "ok")
        o = json.loads(self.get("/api/overview")[0])
        self.assertEqual(o["env"], "dev")
        self.assertNotIn("envs", o); self.assertNotIn("requirements", o)
        self.assertEqual(len(o["sources"]), 5)
        self.assertTrue(all(s["samples"] and s["columns"] and s["origin"] == "default" for s in o["sources"]))
        c = json.loads(self.get("/api/client/C001")[0])
        self.assertEqual(c["emerging"][0]["topic"], "delivery")
        self.assertIn(b"Wochen", self.get("/onepager")[0])

    def test_four_audience_presentations(self):
        pages = {a: self.get(f"/deck/{a}/C001")[0] for a in decks.AUDIENCES}
        self.assertEqual(len(set(pages.values())), 4)
        for a in decks.AUDIENCES:
            data, ctype = self.get(f"/download/{a}/C001.pptx")
            self.assertTrue(data.startswith(b"PK"), a)
        self.assertNotIn(b"EUR", pages["pitch_de"])

    def test_homepage_label_and_removed_items(self):
        html = self.get("/")[0].decode("utf-8")
        self.assertIn('["overview",()=>"Homepage"]', html)
        self.assertNotIn(">Overview<", html)
        self.assertNotIn("Kundenspezifisch", html)
        self.assertNotIn("<h3>Flow</h3>", html)
        self.assertNotIn("synthetic", html.lower())
        self.assertIn('data-l="en"', html); self.assertIn('data-l="de"', html)

    def test_no_synthetic_sentence_anywhere_in_served_content(self):
        for p in ("/onepager", "/onepager?lang=en", "/deck/pitch_de/C001", "/deck/executive/C001?lang=de"):
            self.assertNotIn("synthet", self.get(p)[0].decode("utf-8").lower(), p)

    def test_languages(self):
        en, de = self.get("/deck/executive/C001?lang=en")[0], self.get("/deck/executive/C001?lang=de")[0]
        self.assertNotEqual(en, de)
        self.assertIn(b"Entscheidung erforderlich", de); self.assertIn(b"Decision needed", en)
        self.assertIn(b'lang="de"', de); self.assertIn(b'lang="en"', en)
        self.assertIn(b"Wochen", self.get("/onepager")[0])            # default stays German
        self.assertIn(b"weeks", self.get("/onepager?lang=en")[0])
        self.assertIn(b"Datenqualit", self.get("/deck/technical/C001?lang=de")[0])
        self.assertIn(b"Von Daten zur KI-Strategie", self.get("/deck/pitch_de/C001?lang=en")[0])  # pitch is always German
        o = json.loads(self.get("/api/overview")[0])
        self.assertGreaterEqual(o["dq_summary"]["total"], 10)
        self.assertEqual([c["name"] for c in o["clients"]][0], "CEWE Stiftung & Co. KGaA")

    def test_local_site_is_dev_only(self):
        for env in ("staging", "production"):
            with self.assertRaises(ValueError):
                server.create_server(env, port=0, root=ROOT)
        # staging/production configs stay in place for the GitHub pipeline and keep the strict gate
        for env in ("staging", "production"):
            self.assertTrue(json.loads((ROOT / "config" / "env" / f"{env}.json").read_text())["fail_on_dq_errors"])

    def test_removed_tabs_and_texts(self):
        html = self.get("/")[0].decode("utf-8")
        for gone in ('"delivery"', '"requirements"', "Environments &amp; GitHub", "Environments & GitHub", "Job-ad map", "Stellenanzeigen-Map",
                     "Open one-pager", "to see one", "Nordlicht", 'id="env"'):
            self.assertNotIn(gone, html, gone)
        self.assertIn("No emerging issue for this client.", html)
        self.assertNotIn("source-card", html)
        self.assertIn('type="file"', html)

    def test_workflows_keep_the_three_stage_pipeline(self):
        deploy = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("branches: [dev, staging, main]", deploy)
        self.assertIn("branches: [dev, staging, main]", ci)


class Upload(unittest.TestCase):
    """Uploads write to data/uploads, so these tests run against a temporary copy of the project."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        root = Path(cls.tmp)
        for d in ("config", "data"):
            shutil.copytree(ROOT / d, root / d, ignore=shutil.ignore_patterns("uploads"))
        cls.root = root
        cls.srv, cls.app = server.create_server("dev", port=0, root=root)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close(); shutil.rmtree(cls.tmp, ignore_errors=True)

    def post(self, path, body=b""):
        req = urllib.request.Request(self.base + path, data=body, method="POST")
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def overview(self):
        with urllib.request.urlopen(self.base + "/api/overview") as r:
            return json.loads(r.read())

    def sample(self, name):
        return (ROOT / "data" / "upload_samples" / name).read_bytes()

    def tearDown(self):
        self.post("/api/reset")

    def test_every_sample_file_uploads_and_reproduces_default_view(self):
        base = self.overview()["clients"]
        for src in ("crm", "finance", "social", "cx", "compliance"):
            for f in sorted(p.name for p in (ROOT / "data" / "upload_samples").glob(f"{src}.*")):
                code, res = self.post(f"/api/upload/{src}?filename={f}", self.sample(f))
                self.assertEqual(code, 200, (f, res))
                o = self.overview()
                self.assertEqual(next(s for s in o["sources"] if s["key"] == src)["origin"], "upload")
                self.assertEqual(o["clients"], base, f)

    def test_changed_upload_changes_the_site_and_reset_restores_it(self):
        csv_text = self.sample("crm.csv").decode("utf-8").replace("C001,CEWE Stiftung & Co. KGaA", "C001,Neue Firma GmbH")
        self.assertEqual(self.post("/api/upload/crm?filename=crm.csv", csv_text.encode("utf-8"))[0], 200)
        self.assertEqual(self.overview()["clients"][0]["name"], "Neue Firma GmbH")
        self.assertTrue((self.root / "data" / "uploads" / "crm.json").exists())
        self.post("/api/reset?source=crm")
        self.assertEqual(self.overview()["clients"][0]["name"], "CEWE Stiftung & Co. KGaA")
        self.assertFalse((self.root / "data" / "uploads" / "crm.json").exists())

    def test_bad_uploads_are_rejected_and_change_nothing(self):
        before = self.overview()
        cases = [("crm", "crm.csv", b"client_id,client_name\nC001,x\n", "missing_columns"),
                 ("finance", "f.csv", b"client_id,project,budget_eur,spent_eur\nC001,P,abc,1\n", "bad_value"),
                 ("cx", "cx.pdf", b"%PDF", "bad_format"),
                 ("social", "s.json", b'{"a": 1}', "bad_json"),
                 ("social", "s.json", b"not json", "unreadable"),
                 ("finance", "f.xlsx", b"not an xlsx", "unreadable"),
                 ("crm", "crm.csv", b"", "empty"),
                 ("nope", "x.csv", b"a\n1\n", "unknown_source")]
        for src, name, body, code in cases:
            status, res = self.post(f"/api/upload/{src}?filename={name}", body)
            self.assertEqual((status, res["error"]), (400, code), (src, name))
        self.assertEqual(self.overview()["clients"], before["clients"])

    def test_sample_downloads_are_whitelisted(self):
        with urllib.request.urlopen(self.base + "/samples/crm.xlsx") as r:
            self.assertTrue(r.read().startswith(b"PK"))
        for bad in ("/samples/..%2Fconfig%2Foffers.json", "/samples/missing.csv"):
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(self.base + bad)
            self.assertEqual(cm.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
