"""Continuous improvement: win/loss feedback -> offer health -> backlog."""


def offer_stats(rows):
    by = {}
    for r in rows:
        by.setdefault(r["offer"], []).append(r)
    res = []
    for offer, rs in by.items():
        won = sum(r["outcome"] == "won" for r in rs)
        reasons = {}
        for r in rs:
            if r["outcome"] == "lost" and r["reason"]:
                reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
        top = max(reasons, key=reasons.get) if reasons else None
        rate = won / len(rs)
        key = "scale" if rate >= 0.6 else "improve" if rate >= 0.4 else "rework"
        action = {"scale": "scale", "improve": f"improve (top loss reason: {top})", "rework": f"rework scope/pricing (top loss reason: {top})"}[key]
        res.append({"offer": offer, "n": len(rs), "win_rate": round(rate, 2), "top_loss_reason": top, "action": action, "action_key": key})
    return sorted(res, key=lambda r: -r["win_rate"])


def backlog_markdown(stats):
    lines = ["# Improvement backlog (generated from win/loss feedback)", "", "| Offer | Win rate | Action |", "|---|---|---|"]
    lines += [f"| {s['offer']} | {s['win_rate']:.0%} | {s['action']} |" for s in stats]
    return "\n".join(lines) + "\n"
