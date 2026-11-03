"""Local web app (stdlib only): dashboard + API + browser presentations + PowerPoint downloads + data upload.

    python -m insight_hub serve        -> http://localhost:8000   (dev only; staging/production live in the GitHub pipeline)
"""
import io
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import decks, dq, feedback, i18n, ingest, marketing, monitoring, office_export, pipeline

ROOT = pipeline.ROOT
LOCAL_ENV = "dev"  # the website only ever runs the dev environment; staging and production are deployed by GitHub Actions
DEPARTMENTS = {"crm": "Sales", "finance": "Finance", "social": "Marketing", "cx": "Customer Experience", "compliance": "Compliance"}
DEFAULT_FILES = {"crm": "crm_mandates.csv", "finance": "finance_budgets.xlsx", "social": "social_posts.json",
                 "cx": "cx_reviews.csv", "compliance": "compliance_checklist.md"}


class App:
    def __init__(self, env=LOCAL_ENV, root=ROOT):
        if env != LOCAL_ENV:
            raise ValueError("the local website runs the dev environment only; staging and production run in the GitHub pipeline")
        self.root, self.env = root, env
        self.cfg = pipeline.load_json(root / "config" / "env" / f"{env}.json")
        self.lock = threading.RLock()
        self.uploads = self._load_uploads()
        self.reload()

    # ----- uploaded department files (kept in data/uploads, git-ignored) -------------------------------------------
    @property
    def upload_dir(self):
        return self.root / "data" / "uploads"

    def _load_uploads(self):
        found = {}
        for key in ingest.SCHEMA:
            f = self.upload_dir / f"{key}.json"
            if f.exists():
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                    found[key] = {"filename": d["filename"], "records": ingest.normalise(key, d["records"])}
                except (ValueError, KeyError, TypeError):
                    pass  # ignore a damaged upload and fall back to the default file
        return found

    def _overrides(self, uploads=None):
        return {k: v["records"] for k, v in (self.uploads if uploads is None else uploads).items()}

    def reload(self):
        with self.lock:
            self._build(self.uploads)

    def _build(self, uploads):
        built = pipeline.build_contexts(self.root, overrides=self._overrides(uploads))
        dq.enforce(built[4], self.cfg["fail_on_dq_errors"])
        self.ctxs, self.stats, self.offers, self.totals, self.issues, self.data = built
        self.by_id = {c["client"]["client_id"]: c for c in self.ctxs}
        self.classified = monitoring.analyse(self.data["social"])

    def upload(self, source, filename, content):
        """Parse, validate and activate an uploaded file for one department. Nothing changes if anything fails."""
        records = ingest.parse_upload(source, filename, content)
        with self.lock:
            trial = {**self.uploads, source: {"filename": Path(filename).name, "records": records}}
            try:
                self._build(trial)
            except Exception as e:
                self._build(self.uploads)  # roll back to the data that was active before
                raise ingest.UploadError("rebuild_failed", f"{type(e).__name__}: {e}") from None
            self.uploads = trial
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            (self.upload_dir / f"{source}.json").write_text(json.dumps(trial[source], ensure_ascii=False), encoding="utf-8")
        return len(records)

    def reset(self, source=None):
        with self.lock:
            keys = [source] if source else list(self.uploads)
            for k in keys:
                self.uploads.pop(k, None)
                (self.upload_dir / f"{k}.json").unlink(missing_ok=True)
            self._build(self.uploads)

    def samples(self):
        d = self.root / "data" / "upload_samples"
        return sorted(p.name for p in d.iterdir()) if d.exists() else []

    def overview(self):
        views = []
        for c in self.ctxs:
            v = c["client"]
            views.append({"client_id": v["client_id"], "name": v["name"], "industry": v["industry"], "pipeline_eur": v["pipeline_eur"], "budget_eur": v["budget_eur"],
                          "spent_eur": v["spent_eur"], "records": v["records"], "nps": c["nps"],
                          "top_use_case": c["strategy"][0]["name"] if c["strategy"] else None,
                          "top_use_case_de": c["strategy"][0]["name_de"] if c["strategy"] else None,
                          "emerging": c["emerging"], "dq": sum(i.get("client_id") == v["client_id"] for i in self.issues)})
        samples, sources = self.samples(), []
        for key, dept in DEPARTMENTS.items():
            up = self.uploads.get(key)
            sources.append({"key": key, "department": dept, "columns": list(ingest.SCHEMA[key][0]), "records": len(self.data[key]),
                            "origin": "upload" if up else "default", "file": up["filename"] if up else DEFAULT_FILES[key],
                            "samples": [n for n in samples if n.rsplit(".", 1)[0] == key]})
        offer_en = {o["offer"]: o.get("offer_en", o["offer"]) for o in self.offers}
        fb = [{**f, "offer_en": offer_en.get(f["offer"], f["offer"])} for f in feedback.offer_stats(ingest.load_feedback(self.root / "data" / "raw"))]
        return {"env": self.env, "totals": self.totals, "clients": views, "sources": sources, "dq": self.issues,
                "dq_summary": dq.summary(self.issues), "offers": self.offers, "feedback": fb, "maps": i18n.MAPS,
                "audiences": [{"key": k, **v} for k, v in decks.AUDIENCES.items()]}

    def client(self, cid):
        c = self.by_id[cid]
        posts = [p for p in self.classified if p["client_id"] == cid]
        counts = {k: sum(p["sentiment"] == k for p in posts) for k in ("positive", "neutral", "negative")}
        recent = sorted(posts, key=lambda p: p["date"], reverse=True)[:8]
        return {**c, "sentiment": counts, "recent_posts": recent, "config": pipeline.client_cfg(cid, self.root),
                "custom_config": (self.root / "config" / "clients" / f"{cid}.json").exists()}


def make_handler(app):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, body, ctype="text/html; charset=utf-8", status=200, extra=None):
            body = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(status); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body)))
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers(); self.wfile.write(body)

        def json(self, obj, status=200):
            self.send(json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8", status)

        def do_GET(self):
            url = urlparse(self.path)
            path = url.path
            lang = parse_qs(url.query).get("lang", [None])[0]
            try:
                if path == "/":
                    return self.send((Path(__file__).parent / "web" / "index.html").read_text(encoding="utf-8"))
                if path == "/healthz":
                    return self.json({"status": "ok", "env": app.env})
                if path == "/api/overview":
                    return self.json(app.overview())
                if m := re.fullmatch(r"/samples/([\w.-]+)", path):
                    f = app.root / "data" / "upload_samples" / m[1]
                    if m[1] not in app.samples():
                        return self.json({"error": "not found"}, 404)
                    return self.send(f.read_bytes(), "application/octet-stream", extra={"Content-Disposition": f'attachment; filename="{m[1]}"'})
                if path == "/api/reload":
                    app.reload(); return self.json({"reloaded": True})
                if m := re.fullmatch(r"/api/client/(\w+)", path):
                    return self.json(app.client(m[1]))
                if path == "/onepager":
                    return self.send(marketing.onepager(app.offers, app.overview()["feedback"], app.totals, lang if lang in ("en", "de") else "de"))
                if m := re.fullmatch(r"/deck/(\w+)/(\w+)", path):
                    aud, cid = m[1], m[2]
                    spec, dl = decks.AUDIENCES[aud], decks.resolve_lang(aud, lang)
                    label = spec["label_de"] if dl == "de" else spec["label"]
                    return self.send(decks.deck_html(f"{label} · {app.by_id[cid]['client']['name']}", decks.build(aud, app.by_id[cid], dl), dl))
                if m := re.fullmatch(r"/download/(\w+)/(\w+)\.pptx", path):
                    buf = io.BytesIO(); office_export.audience_deck(decks.build(m[1], app.by_id[m[2]], lang or "en"), buf)
                    return self.send(buf.getvalue(), "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                     extra={"Content-Disposition": f'attachment; filename="{m[1]}_{m[2]}.pptx"'})
                if path == "/download/analysis.xlsx":
                    buf = io.BytesIO(); office_export.workbook(app.ctxs, app.overview()["feedback"], buf)
                    return self.send(buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     extra={"Content-Disposition": 'attachment; filename="analysis.xlsx"'})
                self.json({"error": "not found"}, 404)
            except KeyError:
                self.json({"error": "unknown client or audience"}, 404)

        def do_POST(self):
            url = urlparse(self.path)
            q = parse_qs(url.query)
            try:
                if m := re.fullmatch(r"/api/upload/(\w+)", url.path):
                    n = int(self.headers.get("Content-Length") or 0)
                    if n > ingest.MAX_UPLOAD_BYTES:
                        raise ingest.UploadError("too_large")
                    count = app.upload(m[1], q.get("filename", [""])[0], self.rfile.read(n))
                    return self.json({"ok": True, "source": m[1], "records": count})
                if url.path == "/api/reset":
                    source = q.get("source", [None])[0]
                    if source is not None and source not in ingest.SCHEMA:
                        raise ingest.UploadError("unknown_source", source)
                    app.reset(source)
                    return self.json({"ok": True})
                self.json({"error": "not found"}, 404)
            except ingest.UploadError as e:
                self.json({"error": e.code, "detail": e.detail}, 400)

    return H


def create_server(env=LOCAL_ENV, port=None, root=ROOT):
    app = App(env, root)
    return ThreadingHTTPServer(("127.0.0.1", app.cfg["port"] if port is None else port), make_handler(app)), app


def serve(port=None):
    srv, _ = create_server(LOCAL_ENV, port)
    print(f"BDO Insight Hub [{LOCAL_ENV}] running at http://localhost:{srv.server_address[1]}  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
