"""Generate deterministic sample data (no real client data)."""
import csv, json, random
from datetime import date, timedelta
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
random.seed(42)
CLIENTS = [("C001", "CEWE Stiftung & Co. KGaA", "Photo & Retail"), ("C002", "Delticom AG", "E-Commerce"),
           ("C003", "Masterflex SE", "Industrial Manufacturing"), ("C004", "hGears AG", "Automotive Supplier"),
           ("C005", "Kölner Pensionskasse VVaG", "Insurance & Pensions"), ("C006", "Encavis AG", "Renewable Energy")]
STAGES = ["lead", "proposal", "won", "lost"]
END = date(2026, 10, 25)


def write_csv(name, header, rows):
    with open(RAW / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


# CRM (Sales)
crm = []
for i, (cid, name, ind) in enumerate(CLIENTS):
    for j, m in enumerate(["KI-Strategie", "CX-Diagnose"][: 1 + i % 2]):
        crm.append([cid, name, ind, m, STAGES[(i + j) % 4], random.choice([45, 80, 120, 150, 220]) * 1000, f"Partner {chr(65 + i)}"])
write_csv("crm_mandates.csv", ["client_id", "client_name", "industry", "mandate", "stage", "value_eur", "owner"], crm)

# Finance (Excel + CSV fallback)
fin = []
for cid, _, _ in CLIENTS:
    b = random.choice([60, 90, 140, 200]) * 1000
    fin.append([cid, f"{cid}-P1", b, int(b * random.uniform(0.4, 0.95))])
fin[2][3] = int(fin[2][2] * 1.2)  # deliberate overspend -> data-quality warning
write_csv("finance_budgets.csv", ["client_id", "project", "budget_eur", "spent_eur"], fin)
from openpyxl import Workbook
wb = Workbook(); ws = wb.active; ws.title = "budgets"
ws.append(["client_id", "project", "budget_eur", "spent_eur"])
for r in fin:
    ws.append(r)
wb.save(RAW / "finance_budgets.xlsx")

# Social media (Marketing)
TPL = {"delivery": ["Lieferung super schnell, toll!", "Paket kam verspätet, richtig Ärger", "Shipping was slow and the parcel arrived broken"],
       "price": ["Preis ist okay, gute Qualität", "Viel zu teuer geworden, enttäuscht"],
       "support": ["Support hat sofort geholfen, empfehle ich", "Hotline schlecht erreichbar, bad service"],
       "app": ["Neue App ist great, love the update", "App Login kaputt seit dem Update"]}
posts = []
for n in range(160):
    d = END - timedelta(days=random.randint(0, 85))
    posts.append({"id": f"p{n}", "client_id": random.choice(CLIENTS)[0], "date": d.isoformat(),
                  "channel": random.choice(["x", "linkedin", "instagram"]), "text": random.choice(TPL[random.choice(list(TPL))])})
for n in range(14):  # emerging delivery issue for C001
    d = END - timedelta(days=random.randint(0, 20))
    posts.append({"id": f"s{n}", "client_id": "C001", "date": d.isoformat(), "channel": "x",
                  "text": random.choice(["Lieferung wieder verspätet, Ärger!", "Paket kaputt und Lieferung langsam, bad"])})
(RAW / "social_posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding="utf-8")

# Customer Experience
cx = []
for n in range(240):
    tp = random.choice(["Onboarding", "Delivery", "Support", "Billing", "App"])
    s = max(1, min(10, round(random.gauss({"Support": 5.5, "Delivery": 6.5}.get(tp, 8), 1.8))))
    churn = 1 if (s <= 5 and random.random() < 0.7) or random.random() < 0.04 else 0
    cx.append([random.choice(CLIENTS)[0], (END - timedelta(days=random.randint(0, 85))).isoformat(), tp, s, churn, "Kommentar" if s > 3 else "Frustriert"])
write_csv("cx_reviews.csv", ["client_id", "date", "touchpoint", "score", "churned", "comment"], cx)

# Compliance
(RAW / "compliance_checklist.md").write_text("""# Regulatory checklist
- C001 | CSRD reporting | open
- C002 | EU AI Act inventory | open
- C003 | CSRD reporting | done
- C004 | EU AI Act inventory | done
- C005 | DORA ICT risk | open
- C006 | CSRD reporting | open
""", encoding="utf-8")

# Offer feedback (continuous improvement)
OFFERS = ["KI-Strategie Workshop", "Social-Media- & Produktmonitoring", "CX Diagnostics", "Data Platform Assessment"]
REASONS = ["price", "timing", "scope unclear", "no data access", "competitor"]
fb = []
for o, p in zip(OFFERS, [0.7, 0.55, 0.4, 0.3]):
    for _ in range(14):
        won = random.random() < p
        fb.append([o, "won" if won else "lost", "" if won else random.choice(REASONS[:3] if p > 0.5 else REASONS[2:]), random.choice(["Mittelstand", "Konzern"])])
write_csv("offer_feedback.csv", ["offer", "outcome", "reason", "segment"], fb)
print("sample data written to", RAW)

import subprocess
import sys

subprocess.run([sys.executable, str(Path(__file__).with_name("make_upload_samples.py"))], check=True)
