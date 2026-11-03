"""Social-media & product monitoring: sentiment, topics, emerging issues.

The classifier is pluggable: swap `sentiment` for an LLM/transformer call with the same signature.
"""
import re
from datetime import date, timedelta

POS = {"gut", "super", "toll", "schnell", "zufrieden", "empfehle", "great", "love", "fast", "excellent", "okay"}
NEG = {"schlecht", "langsam", "defekt", "kaputt", "verspätet", "teuer", "enttäuscht", "ärger", "slow", "broken", "late", "bad", "terrible", "refund"}
TOPICS = {"delivery": ("lieferung", "paket", "shipping", "parcel"), "price": ("preis", "teuer", "price"),
          "support": ("support", "hotline", "service"), "app": ("app", "login", "update"),
          "quality": ("qualität", "defekt", "quality")}


def sentiment(text):
    toks = re.findall(r"[a-zäöüß]+", text.lower())
    p, n = sum(t in POS for t in toks), sum(t in NEG for t in toks)
    score = (p - n) / max(1, p + n)
    return ("positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"), score


def topics(text):
    low = text.lower()
    return [k for k, ws in TOPICS.items() if any(w in low for w in ws)] or ["other"]


def analyse(posts, classifier=sentiment):
    out = []
    for p in posts:
        label, score = classifier(p["text"])
        out.append({**p, "sentiment": label, "score": score, "topics": topics(p["text"])})
    return out


def emerging_issues(classified, window_days=30, min_recent=3):
    """Topic is 'emerging' if negative mentions in the last window at least double vs. the previous window."""
    if not classified:
        return []
    end = max(date.fromisoformat(p["date"]) for p in classified)
    recent_from, prev_from = end - timedelta(days=window_days), end - timedelta(days=2 * window_days)
    counts = {}
    for p in classified:
        if p["sentiment"] != "negative":
            continue
        d = date.fromisoformat(p["date"])
        for t in p["topics"]:
            c = counts.setdefault((p["client_id"], t), [0, 0])
            if d > recent_from:
                c[0] += 1
            elif d > prev_from:
                c[1] += 1
    res = [{"client_id": k[0], "topic": k[1], "recent": c[0], "previous": c[1]}
           for k, c in counts.items() if c[0] >= min_recent and c[0] >= 2 * max(c[1], 1)]
    return sorted(res, key=lambda r: -r["recent"])
