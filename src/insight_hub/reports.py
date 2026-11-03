"""Four audience-specific versions of the SAME insights (Adressatengerechte Präsentation)."""
from .i18n import INDUSTRY


def recommend_offers(ctx, offers, stats):
    """Map detected signals to BDO offers; attach win-rate evidence from the feedback loop."""
    from .i18n import TOPIC, TOUCH
    wins = {s["offer"]: s for s in stats}
    triggers = []
    if ctx["emerging"]:
        t = ctx["emerging"][0]["topic"]
        triggers.append(("Social-Media- & Produktmonitoring", f"emerging issue: {t}", f"aufkommendes Thema: {TOPIC.get(t, t)}"))
    if ctx["drivers"] and ctx["drivers"][0]["lift"] >= 1.5:
        d = ctx["drivers"][0]
        triggers.append(("CX Diagnostics", f"{d['touchpoint']} churn lift {d['lift']}x", f"{TOUCH.get(d['touchpoint'], d['touchpoint'])}: Churn-Lift {d['lift']}x"))
    if ctx["strategy"]:
        u = ctx["strategy"][0]
        triggers.append(("KI-Strategie Workshop", f"top use case: {u['name']}", f"wichtigster Use Case: {u.get('name_de', u['name'])}"))
    if ctx["dq"] or ctx["strategy"] and ctx["strategy"][0]["readiness"] < 4:
        triggers.append(("Data Platform Assessment", "data silos / readiness gaps", "Datensilos / Lücken bei der Datenreife"))
    by = {o["offer"]: o for o in offers}
    return [{**by[o], "why": why, "why_de": why_de, "win_rate": wins.get(o, {}).get("win_rate")} for o, why, why_de in triggers if o in by]


def executive(c):
    v, top = c["client"], c["strategy"][:3]
    lines = [f"# {v['name']} – Executive summary (CEO)", "",
             "**Decision needed:** approve Wave-1 AI initiatives and the data-integration budget.", "",
             "## Three key messages",
             f"1. Highest-value AI use case: **{top[0]['name']}** (score {top[0]['score']}/100)." if top else "1. No use case scored.",
             f"2. Customer experience: NPS {c['nps']}; biggest churn driver is **{c['drivers'][0]['touchpoint']}** ({c['drivers'][0]['lift']}x average churn)." if c["drivers"] else "2. Not enough CX data.",
             (f"3. Early warning: negative **{c['emerging'][0]['topic']}** mentions rose from {c['emerging'][0]['previous']} to {c['emerging'][0]['recent']} in 30 days." if c["emerging"] else "3. No emerging social issues detected."),
             "", "## Roadmap (Wave 1-2)"]
    lines += [f"- {u['name']} – {u['wave']}" for u in c["strategy"] if not u["wave"].startswith("Wave 3")]
    return "\n".join(lines) + "\n"


def finance(c):
    v = c["client"]
    util = v["spent_eur"] / v["budget_eur"] if v["budget_eur"] else 0
    lines = [f"# {v['name']} – Finance view (CFO)", "", "| Metric | Value |", "|---|---|",
             f"| Open pipeline (lead + proposal) | {v['pipeline_eur']:,.0f} EUR |", f"| Won mandates | {v['won_eur']:,.0f} EUR |",
             f"| Project budget | {v['budget_eur']:,.0f} EUR |", f"| Spent | {v['spent_eur']:,.0f} EUR ({util:.0%}) |", "",
             "## Ranking of AI initiatives by score (value vs. data readiness vs. risk)", "| Use case | Score | Risk (1-5) |", "|---|---|---|"]
    lines += [f"| {u['name']} | {u['score']} | {u['risk']} |" for u in c["strategy"]]
    warn = [i["message"] for i in c["dq"] if i["source"] == "finance" and i.get("client_id") in (None, v["client_id"])]
    if warn:
        lines += ["", "## Budget alerts"] + [f"- {w}" for w in warn]
    return "\n".join(lines) + "\n"


def technical(c):
    v = c["client"]
    lines = [f"# {v['name']} – Technical appendix (IT / data teams)", "", "## Source coverage (records per integrated source)",
             "| Source | Department | Records |", "|---|---|---|"]
    dept = {"crm": "Sales", "finance": "Finance", "social": "Marketing", "cx": "Customer Experience", "compliance": "Compliance"}
    lines += [f"| {s} | {dept[s]} | {n} |" for s, n in v["records"].items()]
    lines += ["", "## Scoring method", "score = 20 · (w_value·value + w_readiness·readiness + w_risk·(6 − risk)) / Σw; readiness = 1 + 4·(sources with data / sources required).",
              "", "## Data quality"] + ([f"- [{i['severity']}] {i['source']}: {i['message']}" for i in c["dq"] if i.get("client_id") in (None, v["client_id"])] or ["- no issues"]) + ["", "## Use-case details",
              "| Use case | Score | Readiness | Wave |", "|---|---|---|---|"]
    lines += [f"| {u['name']} | {u['score']} | {u['readiness']} | {u['wave']} |" for u in c["strategy"]]
    lines += ["", "## Next engineering steps", "- Replace lexicon sentiment by an LLM classifier (same interface `classifier(text)`).",
              "- Schedule ingestion; add lineage and PII scan.", "- Deploy per environment dev → staging → production."]
    return "\n".join(lines) + "\n"


def pitch_de(c):
    """Prospect-facing (no client financials, benefit language, German)."""
    lines = ["# So machen wir aus Ihren Daten eine KI-Strategie", "",
             f"*Beispielanalyse für ein Unternehmen der Branche {INDUSTRY.get(c['client']['industry'], c['client']['industry'])}*", "",
             "## Was wir gefunden haben"]
    if c["strategy"]:
        lines.append(f"- Der Use Case mit dem größten Hebel: **{c['strategy'][0]['name_de']}**.")
    if c["drivers"]:
        lines.append(f"- Kundenabwanderung konzentriert sich auf den Touchpoint **{c['drivers'][0]['touchpoint']}**.")
    if c["emerging"]:
        lines.append(f"- Frühwarnsignal in Social Media: Thema **{c['emerging'][0]['topic']}** nimmt zu.")
    lines += ["", "## Unser Angebot für Sie"]
    for o in c["offers"]:
        lines.append(f"- **{o['offer']}** – {o['benefit']}.")
    lines += ["", "## Nächster Schritt", "30-minütiger Austausch mit unserem Management-Advisory-Team."]
    return "\n".join(lines) + "\n"


AUDIENCES = {"executive": executive, "finance": finance, "technical": technical, "pitch_de": pitch_de}
