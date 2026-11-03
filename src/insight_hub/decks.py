"""One presentation per audience (Adressatengerechte Präsentation), available in English and German.

Each builder returns a list of slide specs: {"title", "bullets" | "table", "notes"} (first slide has "subtitle").
The same specs render to a browser slideshow and to PowerPoint, so both stay in sync.
The prospect pitch (pitch_de) is always German; the three internal decks follow the site language.
"""
from .i18n import DEPT, TOPIC, TOUCH, eur, finding_text, pick, uc_name, wave

AUDIENCES = {
    "executive": {"label": "CEO / Management", "label_de": "CEO / Geschäftsführung", "goal": "Decide on priorities in 5 minutes",
                  "goal_de": "In 5 Minuten Prioritäten entscheiden", "fixed": None},
    "finance": {"label": "CFO / Controlling", "label_de": "CFO / Controlling", "goal": "Understand budget, ranking and risk",
                "goal_de": "Budget, Ranking und Risiko verstehen", "fixed": None},
    "technical": {"label": "IT & Data Teams", "label_de": "IT- & Daten-Teams", "goal": "See architecture, data quality and method",
                  "goal_de": "Architektur, Datenqualität und Methodik sehen", "fixed": None},
    "pitch_de": {"label": "Prospects / new clients (German)", "label_de": "Interessenten / Neukunden (DE)", "goal": "Show value and the next step",
                 "goal_de": "Nutzen und nächsten Schritt zeigen", "fixed": "de"},
}


def resolve_lang(audience, lang):
    """Language a deck is rendered in: the pitch is fixed to German, the others follow the site language."""
    return AUDIENCES[audience]["fixed"] or (lang if lang in ("en", "de") else "en")


def _top(c, n=3):
    return c["strategy"][:n]


def _findings(c, limit=6, lang="en"):
    """Data-quality findings relevant to this client (plus global ones), capped for slides."""
    cid = c["client"]["client_id"]
    rel = [i for i in c["dq"] if i.get("client_id") in (None, cid)]
    out = [f"[{pick(lang, i['severity'], {'error': 'Fehler', 'warning': 'Warnung', 'info': 'Hinweis'}[i['severity']])}] {finding_text(i, lang)}" for i in rel[:limit]]
    if len(rel) > limit:
        out.append(pick(lang, f"+ {len(rel) - limit} more finding(s) in the dashboard", f"+ {len(rel) - limit} weitere Befunde im Dashboard"))
    return out


def executive(c, lang="en"):
    t = lambda en, de: pick(lang, en, de)
    v, top, d, e = c["client"], _top(c), (c["drivers"] or [None])[0], (c["emerging"] or [None])[0]
    tp = lambda x: TOUCH.get(x, x) if lang == "de" else x
    tc = lambda x: TOPIC.get(x, x) if lang == "de" else x
    return [
        {"title": t(f"{v['name']}: AI & CX strategy", f"{v['name']}: KI- & CX-Strategie"),
         "subtitle": t("Executive briefing · decision in 5 minutes", "Management-Briefing · Entscheidung in 5 Minuten"),
         "notes": t("One decision today: approve Wave-1.", "Eine Entscheidung heute: Welle 1 freigeben.")},
        {"title": t("Where we stand", "Ausgangslage"), "bullets": [t(f"Customer NPS: {c['nps']}", f"Kunden-NPS: {c['nps']}"),
            t(f"Biggest churn driver: {tp(d['touchpoint'])} ({d['lift']}x average churn)", f"Größter Churn-Treiber: {tp(d['touchpoint'])} ({d['lift']}x der durchschnittlichen Abwanderung)") if d else t("Not enough CX data", "Zu wenig CX-Daten"),
            t(f"Early warning: negative '{tc(e['topic'])}' mentions {e['previous']} → {e['recent']} in 30 days", f"Frühwarnung: negative Erwähnungen zu '{tc(e['topic'])}' {e['previous']} → {e['recent']} in 30 Tagen") if e else t("No emerging social issue detected", "Kein aufkommendes Social-Media-Thema erkannt")],
         "notes": t("Three facts from five integrated departments.", "Drei Fakten aus fünf integrierten Fachbereichen.")},
        {"title": t("Top AI priorities", "Wichtigste KI-Prioritäten"),
         "table": [[t("Use case", "Use Case"), t("Score", "Score"), t("Wave", "Welle")]] + [[uc_name(u, lang), str(u["score"]), wave(u, lang)] for u in top],
         "notes": t("Score = value, measured data readiness, risk.", "Score = Nutzen, gemessene Datenreife, Risiko.")},
        {"title": t("Roadmap", "Roadmap"), "bullets": [f"{wave(u, lang)}: {uc_name(u, lang)}" for u in c["strategy"]]},
        {"title": t("Decision needed", "Entscheidung erforderlich"),
         "bullets": [t("Approve Wave-1 initiatives", "Initiativen der Welle 1 freigeben"), t("Name a business owner per initiative", "Je Initiative eine fachliche Verantwortung benennen"),
                     t("Release data access for the pilot", "Datenzugang für den Piloten freigeben")],
         "notes": t("Close by asking for exactly these three yeses.", "Zum Abschluss genau diese drei Zusagen einholen.")},
    ]


def finance(c, lang="en"):
    t = lambda en, de: pick(lang, en, de)
    v = c["client"]
    util = v["spent_eur"] / v["budget_eur"] if v["budget_eur"] else 0
    alerts = [finding_text(i, lang) for i in c["dq"] if i["source"] == "finance" and i.get("client_id") in (None, v["client_id"])]
    return [
        {"title": t(f"{v['name']}: financial view", f"{v['name']}: Finanzsicht"), "subtitle": t("Pipeline, budget and initiative ranking", "Pipeline, Budget und Initiativen-Ranking")},
        {"title": t("Numbers today", "Zahlen heute"), "table": [[t("Metric", "Kennzahl"), t("Value", "Wert")], [t("Open pipeline", "Offene Pipeline"), eur(v["pipeline_eur"], lang)],
            [t("Won mandates", "Gewonnene Mandate"), eur(v["won_eur"], lang)], [t("Project budget", "Projektbudget"), eur(v["budget_eur"], lang)],
            [t("Spent", "Ausgegeben"), f"{eur(v['spent_eur'], lang)} ({util:.0%})"]]},
        {"title": t("Budget alerts", "Budget-Hinweise"), "bullets": alerts or [t("No budget alerts", "Keine Budget-Hinweise")],
         "notes": t("Alerts come from the automated data-quality gate.", "Die Hinweise stammen aus dem automatischen Datenqualitäts-Gate.")},
        {"title": t("Initiative ranking", "Initiativen-Ranking"), "table": [[t("Use case", "Use Case"), "Score", t("Risk (1-5)", "Risiko (1-5)"), t("Data readiness", "Datenreife")]]
            + [[uc_name(u, lang), str(u["score"]), str(u["risk"]), str(u["readiness"])] for u in c["strategy"]]},
        {"title": t("Investment logic", "Investitionslogik"), "bullets": [t("Fund Wave 1 first: highest score, lowest risk", "Welle 1 zuerst finanzieren: höchster Score, geringstes Risiko"),
            t("Gate Wave 2 on measured results of Wave 1", "Welle 2 an gemessene Ergebnisse aus Welle 1 koppeln"), t("Re-score quarterly with fresh data", "Quartalsweise mit frischen Daten neu bewerten")]},
    ]


def technical(c, lang="en"):
    t = lambda en, de: pick(lang, en, de)
    v = c["client"]
    return [
        {"title": t(f"{v['name']}: technical deep dive", f"{v['name']}: Technischer Deep Dive"), "subtitle": t("Architecture, data quality, method", "Architektur, Datenqualität, Methodik")},
        {"title": t("Architecture", "Architektur"), "bullets": [t("ingest (CSV, XLSX, JSON, Markdown) → data-quality gate", "Ingest (CSV, XLSX, JSON, Markdown) → Datenqualitäts-Gate"),
            t("unified client view → analytics modules", "einheitliche Kundensicht → Analyse-Module"),
            t("outputs: 4 audience decks, one-pager, Office files", "Ergebnisse: 4 Zielgruppen-Präsentationen, One-Pager, Office-Dateien"),
            t("environments: dev → staging → production (same code, different config)", "Umgebungen: dev → staging → production (gleicher Code, andere Konfiguration)")]},
        {"title": t("Source coverage", "Abdeckung der Quellen"), "table": [[t("Source", "Quelle"), t("Department", "Fachbereich"), t("Records", "Datensätze")]]
            + [[s, pick(lang, *DEPT[s]), str(n)] for s, n in v["records"].items()]},
        {"title": t("Data quality", "Datenqualität"), "bullets": _findings(c, 6, lang) or [t("No issues", "Keine Befunde")],
         "notes": t("Staging and production stop on errors; dev reports only. Warnings never block.", "Staging und Production stoppen bei Fehlern; dev berichtet nur. Warnungen blockieren nie.")},
        {"title": t("Method", "Methodik"), "bullets": [t("Strategy score = weighted value + readiness + (6 - risk), scaled 0-100", "Strategie-Score = gewichteter Nutzen + Datenreife + (6 - Risiko), skaliert auf 0-100"),
            t("Readiness = share of required sources that hold data for this client", "Datenreife = Anteil der benötigten Quellen mit Daten für diesen Kunden"),
            t("Emerging issue = negative topic mentions at least 2x vs previous 30 days", "Aufkommendes Thema = negative Erwähnungen mindestens 2x gegenüber den vorherigen 30 Tagen"),
            t("Churn lift = touchpoint churn rate / overall churn rate", "Churn-Lift = Churn-Rate des Touchpoints / Gesamt-Churn-Rate")]},
        {"title": t("Next engineering steps", "Nächste Engineering-Schritte"), "bullets": [t("Swap lexicon sentiment for an LLM classifier (same interface)", "Lexikon-Sentiment durch LLM-Klassifikator ersetzen (gleiche Schnittstelle)"),
            t("Scheduled ingestion, lineage, PII scan", "Geplante Ingestion, Lineage, PII-Scan"), t("Monitoring and alerting per environment", "Monitoring und Alerting je Umgebung")]},
    ]


def pitch_de(c, lang="de"):
    d, e, top = (c["drivers"] or [None])[0], (c["emerging"] or [None])[0], _top(c, 1)
    from .i18n import INDUSTRY
    return [
        {"title": "Von Daten zur KI-Strategie", "subtitle": f"Beispielanalyse · Branche {INDUSTRY.get(c['client']['industry'], c['client']['industry'])}"},
        {"title": "Ihre Herausforderung", "bullets": ["Daten liegen in Silos: Vertrieb, Finanzen, Marketing, CX, Compliance", "Entscheidungen zu KI brauchen eine belastbare Priorisierung",
            "Probleme im Kundenerlebnis werden zu spät sichtbar"]},
        {"title": "Was wir gefunden haben", "bullets": [f"Größter Hebel: {top[0]['name_de']}" if top else "–",
            f"Abwanderung konzentriert sich auf: {TOUCH.get(d['touchpoint'], d['touchpoint'])}" if d else "–", f"Frühwarnsignal in Social Media: {TOPIC.get(e['topic'], e['topic'])}" if e else "Keine akuten Social-Themen"]},
        {"title": "Unser Vorgehen", "bullets": ["1  Daten integrieren und prüfen", "2  Use Cases bewerten: Nutzen, Datenreife, Risiko", "3  Roadmap in Wellen festlegen", "4  Umsetzen und laufend verbessern"]},
        {"title": "Unsere Angebote", "table": [["Angebot", "Nutzen"]] + [[o["offer"], o["benefit"]] for o in c["offers"]]},
        {"title": "Nächster Schritt", "bullets": ["30 Minuten Austausch mit unserem Management-Advisory-Team", "Gemeinsam Ihren wichtigsten Use Case festlegen"]},
    ]


BUILDERS = {"executive": executive, "finance": finance, "technical": technical, "pitch_de": pitch_de}


def build(audience, ctx, lang="en"):
    return BUILDERS[audience](ctx, resolve_lang(audience, lang))


def deck_html(title, slides, lang="en"):
    import html
    out = []
    for i, s in enumerate(slides):
        body = ""
        if "subtitle" in s:
            body = f"<p class='sub'>{html.escape(s['subtitle'])}</p>"
        if "bullets" in s:
            body = "<ul>" + "".join(f"<li>{html.escape(b)}</li>" for b in s["bullets"]) + "</ul>"
        if "table" in s:
            h, *rows = s["table"]
            body = "<table><tr>" + "".join(f"<th>{html.escape(x)}</th>" for x in h) + "</tr>" + "".join(
                "<tr>" + "".join(f"<td>{html.escape(x)}</td>" for x in r) + "</tr>" for r in rows) + "</table>"
        notes = f"<p class='notes'>{html.escape(s['notes'])}</p>" if s.get("notes") else ""
        cls = "slide cover" if i == 0 else "slide"
        out.append(f"<section class='{cls}'><h1>{html.escape(s['title'])}</h1>{body}{notes}</section>")
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>
:root{{--bg:#f5f3ee;--fg:#12202f;--ac:#d3123a;--mu:#5b6672;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#12202f;--fg:#f5f3ee;--mu:#9aa6b2;--card:#1d3247}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font-family:Inter,Arial,sans-serif}}
.slide{{display:none;min-height:100vh;padding:8vh 8vw;flex-direction:column;justify-content:center;gap:3vh}}.slide.on{{display:flex}}
h1{{font-size:clamp(28px,4.5vw,60px);margin:0}}.cover h1{{font-size:clamp(34px,6vw,84px);color:var(--ac)}}.sub{{font-size:clamp(18px,2.4vw,32px);color:var(--mu)}}
ul{{font-size:clamp(18px,2.6vw,34px);line-height:1.5;padding-left:1.2em}}li{{margin:.4em 0}}
table{{border-collapse:collapse;font-size:clamp(16px,2vw,28px);width:100%;background:var(--card)}}th,td{{padding:.6em 1em;text-align:left;border-bottom:1px solid var(--mu)}}th{{color:var(--ac)}}
.notes{{display:none;font-size:16px;color:var(--mu)}}body.n .notes{{display:block}}
nav{{position:fixed;bottom:12px;left:0;right:0;display:flex;justify-content:center;gap:12px;font-size:14px;color:var(--mu)}}
button{{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:6px 14px;cursor:pointer}}</style></head><body>
{''.join(out)}<nav><button onclick="go(-1)">←</button><span id="p"></span><button onclick="go(1)">→</button><span>{'N = Sprechernotizen · F = Vollbild' if lang == 'de' else 'N = speaker notes · F = fullscreen'}</span></nav>
<script>const S=[...document.querySelectorAll('.slide')];let i=0;function show(){{S.forEach((s,k)=>s.classList.toggle('on',k===i));document.getElementById('p').textContent=(i+1)+' / '+S.length}}
function go(d){{i=Math.max(0,Math.min(S.length-1,i+d));show()}}
addEventListener('keydown',e=>{{if(e.key==='ArrowRight'||e.key===' ')go(1);if(e.key==='ArrowLeft')go(-1);if(e.key==='n')document.body.classList.toggle('n');if(e.key==='f')document.documentElement.requestFullscreen()}});show()</script></body></html>"""
