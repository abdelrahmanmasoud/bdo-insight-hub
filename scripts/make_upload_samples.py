"""Write ready-to-upload example files (CSV, JSON, XLSX; plus Markdown for compliance) for the 5 departments.

They contain the same records as data/raw, so uploading any of them in the web app reproduces the default view.
Output: data/upload_samples/<source>.<csv|json|xlsx|md>
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from insight_hub import ingest

OUT = ROOT / "data" / "upload_samples"


def main():
    from openpyxl import Workbook
    OUT.mkdir(parents=True, exist_ok=True)
    for key, rows in ingest.load_all(ROOT / "data" / "raw").items():
        cols = ingest.SCHEMA[key][0]
        with open(OUT / f"{key}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
        (OUT / f"{key}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        wb = Workbook(); ws = wb.active; ws.title = key
        ws.append(list(cols))
        for r in rows:
            ws.append([r[c] for c in cols])
        wb.save(OUT / f"{key}.xlsx")
    md = ["# Regulatory checklist"] + [f"- {r['client_id']} | {r['topic']} | {r['status']}" for r in ingest.load_compliance(ROOT / "data" / "raw")]
    (OUT / "compliance.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("upload samples written to", OUT)


if __name__ == "__main__":
    main()
