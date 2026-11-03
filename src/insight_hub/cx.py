"""Customer-experience analytics: NPS and churn drivers by touchpoint."""


def nps(reviews):
    if not reviews:
        return None
    pro = sum(r["score"] >= 9 for r in reviews); det = sum(r["score"] <= 6 for r in reviews)
    return round(100 * (pro - det) / len(reviews))


def churn_drivers(reviews, min_n=3):
    if not reviews:
        return []
    overall = sum(r["churned"] for r in reviews) / len(reviews)
    by = {}
    for r in reviews:
        by.setdefault(r["touchpoint"], []).append(r)
    res = []
    for tp, rs in by.items():
        if len(rs) < min_n:
            continue
        rate = sum(r["churned"] for r in rs) / len(rs)
        res.append({"touchpoint": tp, "n": len(rs), "avg_score": round(sum(r["score"] for r in rs) / len(rs), 1),
                    "churn_rate": round(rate, 2), "lift": round(rate / overall, 2) if overall else 0.0})
    return sorted(res, key=lambda r: -r["lift"])
