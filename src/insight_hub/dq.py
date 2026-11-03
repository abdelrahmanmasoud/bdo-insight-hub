"""Data-quality checks (bilingual findings).

Severity decides what the environment gate does:
  error   -> blocks start-up in staging and production (report-only in dev)
  warning -> reported, never blocks
  info    -> reported, never blocks
"""
from collections import Counter, defaultdict
from datetime import date

from .i18n import num

VALID_STAGES = {"lead", "proposal", "won", "lost"}
VALID_STATUS = {"open", "done"}
TOUCHPOINTS = {"Onboarding", "Delivery", "Support", "Billing", "App"}
PLACEHOLDER_COMMENTS = {"", "kommentar", "frustriert"}
BUDGET_WARN_SHARE = 0.80    # project has used >= 80% of its budget
MIN_TOUCHPOINT_REVIEWS = 6  # fewer reviews per touchpoint => unreliable churn rate
STALE_SOCIAL_DAYS = 5       # no post for this many days before the newest post in the data


class DataQualityError(Exception):
    pass


def check(data):
    issues, known = [], {r["client_id"] for r in data["crm"]}
    names = {r["client_id"]: r["client_name"] for r in data["crm"]}

    def add(sev, src, en, de, cid=None):
        issues.append({"severity": sev, "source": src, "client_id": cid, "message": en, "message_de": de})

    def who(cid):
        return names.get(cid, cid)

    # --- integrity (errors) ---------------------------------------------------------------
    seen = set()
    for r in data["crm"]:
        key = (r["client_id"], r["mandate"])
        if key in seen:
            add("error", "crm", f"duplicate mandate {key}", f"Doppeltes Mandat {key}", r["client_id"])
        seen.add(key)
        if r["stage"] not in VALID_STAGES:
            add("error", "crm", f"invalid stage {r['stage']!r} for {key}", f"Ungültige Phase {r['stage']!r} bei {key}", r["client_id"])
    for src in ("finance", "social", "cx", "compliance"):
        for r in data[src]:
            if r["client_id"] not in known:
                add("error", src, f"unknown client_id {r['client_id']}", f"Unbekannte client_id {r['client_id']}", r["client_id"])
    for r in data["compliance"]:
        if r["status"] not in VALID_STATUS:
            add("error", "compliance", f"invalid status {r['status']!r}", f"Ungültiger Status {r['status']!r}", r["client_id"])
    for r in data["social"] + data["cx"]:
        try:
            date.fromisoformat(r["date"])
        except ValueError:
            add("error", "social/cx", f"bad date {r['date']!r}", f"Ungültiges Datum {r['date']!r}")
    for r in data["cx"]:
        if not (1 <= r["score"] <= 10):
            add("error", "cx", f"score out of range: {r['score']}", f"Score außerhalb des Bereichs: {r['score']}", r["client_id"])
        if r["touchpoint"] not in TOUCHPOINTS:
            add("error", "cx", f"unknown touchpoint {r['touchpoint']!r}", f"Unbekannter Touchpoint {r['touchpoint']!r}", r["client_id"])

    # --- finance --------------------------------------------------------------------------
    for r in data["finance"]:
        cid, b, s = r["client_id"], r["budget_eur"], r["spent_eur"]
        if b < 0:
            add("error", "finance", f"negative budget {r['project']}", f"Negatives Budget {r['project']}", cid)
        elif s > b:
            add("warning", "finance", f"{r['project']} overspent: {num(s)} of {num(b)} EUR ({who(cid)})",
                f"{r['project']} überschritten: {num(s, 'de')} von {num(b, 'de')} EUR ({who(cid)})", cid)
        elif b and s / b >= BUDGET_WARN_SHARE:
            add("warning", "finance", f"{r['project']} at {s / b:.0%} of budget ({num(s)} of {num(b)} EUR, {who(cid)})",
                f"{r['project']} bei {s / b:.0%} des Budgets ({num(s, 'de')} von {num(b, 'de')} EUR, {who(cid)})", cid)

    # --- customer experience --------------------------------------------------------------
    by_client = defaultdict(list)
    for r in data["cx"]:
        by_client[r["client_id"]].append(r)
    for cid, rows in sorted(by_client.items()):
        odd = [r for r in rows if r["churned"] == 1 and r["score"] >= 8]
        if odd:
            add("warning", "cx", f"{who(cid)}: {len(odd)} review(s) flagged as churned despite a score of 8 or higher (check label quality)",
                f"{who(cid)}: {len(odd)} Bewertung(en) als abgewandert markiert trotz Score ab 8 (Label-Qualität prüfen)", cid)
        per_tp = Counter(r["touchpoint"] for r in rows)
        thin = sorted((tp, n) for tp, n in per_tp.items() if n < MIN_TOUCHPOINT_REVIEWS)
        if thin:
            txt = ", ".join(f"{tp} ({n})" for tp, n in thin)
            add("warning", "cx", f"{who(cid)}: fewer than {MIN_TOUCHPOINT_REVIEWS} reviews for {txt}: churn rates are unreliable",
                f"{who(cid)}: weniger als {MIN_TOUCHPOINT_REVIEWS} Bewertungen bei {txt}: Churn-Raten unsicher", cid)
    if data["cx"]:
        ph = sum(str(r.get("comment", "")).strip().lower() in PLACEHOLDER_COMMENTS for r in data["cx"])
        if ph / len(data["cx"]) >= 0.5:
            add("warning", "cx", f"{ph} of {len(data['cx'])} reviews contain only a placeholder comment (no free text for analysis)",
                f"{ph} von {len(data['cx'])} Bewertungen enthalten nur einen Platzhalter-Kommentar (kein Freitext für die Analyse)")

    # --- social media ---------------------------------------------------------------------
    posts = [p for p in data["social"] if p["client_id"] in known]
    dups = Counter((p["client_id"], p["date"], p["text"]) for p in posts)
    dup_by_client = Counter(k[0] for k, n in dups.items() if n > 1)
    for cid, n in sorted(dup_by_client.items()):
        add("warning", "social", f"{who(cid)}: {n} post(s) appear more than once on the same day (possible duplicates or reposts)",
            f"{who(cid)}: {n} Post(s) erscheinen am selben Tag mehrfach (mögliche Duplikate oder Reposts)", cid)
    if posts:
        distinct = len({p["text"] for p in posts})
        if distinct / len(posts) < 0.25:
            add("info", "social", f"only {distinct} distinct post texts across {len(posts)} posts (low diversity, check for templated or bot content)",
                f"nur {distinct} verschiedene Post-Texte bei {len(posts)} Posts (geringe Vielfalt, auf Vorlagen- oder Bot-Inhalte prüfen)")
        try:
            newest = max(date.fromisoformat(p["date"]) for p in posts)
            last = {}
            for p in posts:
                d = date.fromisoformat(p["date"])
                last[p["client_id"]] = max(last.get(p["client_id"], d), d)
            for cid, d in sorted(last.items()):
                if (newest - d).days >= STALE_SOCIAL_DAYS:
                    add("info", "social", f"{who(cid)}: no social post for {(newest - d).days} days (monitoring signal may be stale)",
                        f"{who(cid)}: seit {(newest - d).days} Tagen kein Social-Post (Monitoring-Signal evtl. veraltet)", cid)
        except ValueError:
            pass  # bad dates are already reported as errors above

    order = {"error": 0, "warning": 1, "info": 2}
    return sorted(issues, key=lambda i: order[i["severity"]])


def summary(issues):
    c = Counter(i["severity"] for i in issues)
    return {"errors": c["error"], "warnings": c["warning"], "info": c["info"], "total": len(issues)}


def enforce(issues, fail_on_errors):
    errors = [i for i in issues if i["severity"] == "error"]
    if fail_on_errors and errors:
        raise DataQualityError(f"{len(errors)} data-quality error(s): {errors[0]['message']}")
