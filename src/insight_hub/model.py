"""Unified data model: one view per client, joined across all departments."""
SOURCES = ("crm", "finance", "social", "cx", "compliance")


def unify(data):
    views = {}
    for r in data["crm"]:
        v = views.setdefault(r["client_id"], {"client_id": r["client_id"], "name": r["client_name"],
                                              "industry": r["industry"], "mandates": []})
        v["mandates"].append({"mandate": r["mandate"], "stage": r["stage"], "value_eur": r["value_eur"]})
    for v in views.values():
        v["pipeline_eur"] = sum(m["value_eur"] for m in v["mandates"] if m["stage"] in ("lead", "proposal"))
        v["won_eur"] = sum(m["value_eur"] for m in v["mandates"] if m["stage"] == "won")
        v["budget_eur"] = v["spent_eur"] = 0.0
        v["compliance_open"] = []
        v["records"] = {s: 0 for s in SOURCES}
        v["records"]["crm"] = len(v["mandates"])
    for r in data["finance"]:
        if r["client_id"] in views:
            v = views[r["client_id"]]
            v["budget_eur"] += r["budget_eur"]; v["spent_eur"] += r["spent_eur"]; v["records"]["finance"] += 1
    for src in ("social", "cx"):
        for r in data[src]:
            if r["client_id"] in views:
                views[r["client_id"]]["records"][src] += 1
    for r in data["compliance"]:
        if r["client_id"] in views:
            views[r["client_id"]]["records"]["compliance"] += 1
            if r["status"] == "open":
                views[r["client_id"]]["compliance_open"].append(r["topic"])
    return views
