"""Orchestration: ingest -> quality gate -> unify -> analyse -> score -> render outputs per environment."""
import json
import os
from pathlib import Path

from . import cx, decks, dq, feedback, ingest, marketing, model, monitoring, office_export, reports, strategy

ROOT = Path(__file__).resolve().parents[2]


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def client_cfg(cid, root=ROOT):
    p = root / "config" / "clients" / f"{cid}.json"
    return load_json(p if p.exists() else root / "config" / "clients" / "default.json")


def build_contexts(root=ROOT, raw=None, overrides=None):
    """`overrides` replaces whole department sources (e.g. files uploaded in the web app); the pipeline run never uses it."""
    raw = raw or root / "data" / "raw"
    data = {**ingest.load_all(raw), **(overrides or {})}
    issues = dq.check(data)
    views = model.unify(data)
    classified = monitoring.analyse(data["social"])
    emerging = monitoring.emerging_issues(classified)
    stats = feedback.offer_stats(ingest.load_feedback(raw))
    offers = load_json(root / "config" / "offers.json")
    ctxs = []
    for cid, v in sorted(views.items()):
        revs = [r for r in data["cx"] if r["client_id"] == cid]
        c = {"client": v, "nps": cx.nps(revs), "drivers": cx.churn_drivers(revs),
             "emerging": [e for e in emerging if e["client_id"] == cid],
             "strategy": strategy.score_use_cases(v, client_cfg(cid, root)), "dq": issues}
        c["offers"] = reports.recommend_offers(c, offers, stats)
        ctxs.append(c)
    totals = {"sources": len(model.SOURCES), "posts": len(data["social"]), "reviews": len(data["cx"])}
    return ctxs, stats, offers, totals, issues, data


def run(env=None, root=ROOT, raw=None):
    env = env or os.environ.get("INSIGHT_HUB_ENV", "dev")
    cfg = load_json(root / "config" / "env" / f"{env}.json")
    ctxs, stats, offers, totals, issues, _ = build_contexts(root, raw)
    dq.enforce(issues, cfg["fail_on_dq_errors"])
    out = root / cfg["output_dir"]; out.mkdir(parents=True, exist_ok=True)
    for c in ctxs:
        d = out / c["client"]["client_id"]; d.mkdir(exist_ok=True)
        for name, fn in reports.AUDIENCES.items():
            (d / f"{name}.md").write_text(fn(c), encoding="utf-8")
        if cfg["office_exports"]:
            office_export.sales_deck(c, d / "sales_deck.pptx"); office_export.technical_doc(c, d / "technical_appendix.docx")
            for aud in decks.AUDIENCES:  # one tailored PowerPoint per audience
                office_export.audience_deck(decks.build(aud, c), d / f"presentation_{aud}.pptx")
    if cfg["office_exports"]:
        office_export.workbook(ctxs, stats, out / "analysis.xlsx")
    (out / "marketing_onepager.html").write_text(marketing.onepager(offers, stats, totals), encoding="utf-8")
    (out / "improvement_backlog.md").write_text(feedback.backlog_markdown(stats), encoding="utf-8")
    (out / "data_quality.json").write_text(json.dumps(issues, indent=1), encoding="utf-8")
    return {"env": env, "clients": len(ctxs), "output_dir": str(out), "dq_issues": len(issues)}
