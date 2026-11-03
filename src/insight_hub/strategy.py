"""KI-Strategie Canvas: scores AI use cases by value, data readiness (measured!) and risk.

Data readiness is derived from the integrated data: share of required sources that actually
hold records for the client. Weights and use cases are configured per client (config/clients/*.json).
"""


def readiness(view, requires):
    return 1 + 4 * sum(view["records"].get(s, 0) > 0 for s in requires) / len(requires)


def score_use_cases(view, cfg):
    w = cfg["weights"]
    out = []
    for uc in cfg["use_cases"]:
        rd = readiness(view, uc["requires"])
        raw = w["value"] * uc["value"] + w["readiness"] * rd + w["risk"] * (6 - uc["risk"])
        s = round(20 * raw / (w["value"] + w["readiness"] + w["risk"]), 1)
        n = 1 if s >= 75 else 2 if s >= 60 else 3
        wave = {1: "Wave 1 (0-3 months)", 2: "Wave 2 (3-6 months)", 3: "Wave 3 (6-12 months)"}[n]
        out.append({"name": uc["name"], "name_de": uc.get("name_de", uc["name"]), "score": s, "readiness": round(rd, 1),
                    "value": uc["value"], "risk": uc["risk"], "wave": wave, "wave_n": n})
    return sorted(out, key=lambda r: -r["score"])
