"""Integration layer: read five sources from five departments into plain Python records.

Every department source can arrive as CSV, TSV, JSON, XLSX or (compliance only) Markdown. `parse_upload` turns
any of these into validated records, so the same data can come from the default files in data/raw or from a
file uploaded in the web app.
"""
import csv
import io
import json
from datetime import date, datetime
from pathlib import Path

# source key -> (required columns, type coercions)
SCHEMA = {
    "crm": (("client_id", "client_name", "industry", "mandate", "stage", "value_eur", "owner"), {"value_eur": float}),
    "finance": (("client_id", "project", "budget_eur", "spent_eur"), {"budget_eur": float, "spent_eur": float}),
    "social": (("id", "client_id", "date", "channel", "text"), {}),
    "cx": (("client_id", "date", "touchpoint", "score", "churned", "comment"), {"score": int, "churned": int}),
    "compliance": (("client_id", "topic", "status"), {}),
}
UPLOAD_FORMATS = (".csv", ".tsv", ".json", ".xlsx", ".md")
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


class UploadError(ValueError):
    """Raised for unreadable or invalid uploads. `code` and `detail` let the UI show a translated message."""

    def __init__(self, code, detail=""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code, self.detail = code, detail


def _csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _cell(v):
    if isinstance(v, (datetime, date)):
        return v.date().isoformat() if isinstance(v, datetime) else v.isoformat()
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return "" if v is None else v


def normalise(source, rows):
    """Check required columns, coerce numbers, return clean records. Raises UploadError."""
    required, casts = SCHEMA[source]
    out = []
    for n, raw in enumerate(rows, start=2):
        row = {str(k).strip().lower(): _cell(v) for k, v in raw.items() if k is not None}
        if not any(str(v).strip() for v in row.values()):
            continue  # skip blank lines
        missing = [c for c in required if c not in row]
        if missing:
            raise UploadError("missing_columns", ", ".join(missing))
        for col, cast in casts.items():
            try:
                row[col] = cast(float(row[col])) if cast is int else cast(row[col])
            except (TypeError, ValueError):
                raise UploadError("bad_value", f"{col} (row {n}): {row[col]!r}") from None
        out.append({c: (row[c].strip() if isinstance(row[c], str) else row[c]) for c in required})
    if not out:
        raise UploadError("empty")
    return out


def _markdown_rows(text):
    """Compliance Markdown: lines like '- C001 | topic | status'."""
    rows = []
    for line in text.splitlines():
        if line.startswith("- ") and line.count("|") == 2:
            cid, topic, status = [p.strip() for p in line[2:].split("|")]
            rows.append({"client_id": cid, "topic": topic, "status": status})
    return rows


def parse_upload(source, filename, content):
    """Parse an uploaded file (bytes) for one department source and return validated records."""
    if source not in SCHEMA:
        raise UploadError("unknown_source", source)
    if len(content) > MAX_UPLOAD_BYTES:
        raise UploadError("too_large")
    ext = Path(filename or "").suffix.lower()
    if ext not in UPLOAD_FORMATS:
        raise UploadError("bad_format", ext or "?")
    try:
        if ext == ".xlsx":
            from openpyxl import load_workbook
            wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            it = wb.active.iter_rows(values_only=True)
            head = [str(h).strip() if h is not None else "" for h in next(it, [])]
            rows = [dict(zip(head, r)) for r in it]
            wb.close()
        else:
            text = content.decode("utf-8-sig")
            if ext == ".json":
                data = json.loads(text)
                rows = data.get("records", data.get("data")) if isinstance(data, dict) else data
                if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                    raise UploadError("bad_json")
            elif ext == ".md":
                rows = _markdown_rows(text)
            else:
                rows = list(csv.DictReader(io.StringIO(text), delimiter="\t" if ext == ".tsv" else _sniff(text)))
    except UploadError:
        raise
    except Exception as e:  # corrupt xlsx, invalid JSON/UTF-8, ...
        raise UploadError("unreadable", type(e).__name__) from None
    return normalise(source, rows)


def _sniff(text):
    head = text.splitlines()[0] if text.strip() else ""
    return ";" if head.count(";") > head.count(",") else ","


def load_crm(raw):  # Sales
    return normalise("crm", _csv(Path(raw) / "crm_mandates.csv"))


def load_finance(raw):  # Finance: Excel first, CSV fallback
    raw, rows = Path(raw), []
    xlsx = raw / "finance_budgets.xlsx"
    if xlsx.exists():
        try:
            rows = parse_upload("finance", xlsx.name, xlsx.read_bytes())
        except (UploadError, ImportError):
            rows = []
    return rows or normalise("finance", _csv(raw / "finance_budgets.csv"))


def load_social(raw):  # Marketing
    return normalise("social", json.loads((Path(raw) / "social_posts.json").read_text(encoding="utf-8")))


def load_cx(raw):  # Customer Experience
    return normalise("cx", _csv(Path(raw) / "cx_reviews.csv"))


def load_compliance(raw):  # Compliance: Markdown list "- C001 | topic | status"
    return normalise("compliance", _markdown_rows((Path(raw) / "compliance_checklist.md").read_text(encoding="utf-8")))


def load_feedback(raw):
    return _csv(Path(raw) / "offer_feedback.csv")


def load_all(raw):
    return {"crm": load_crm(raw), "finance": load_finance(raw), "social": load_social(raw),
            "cx": load_cx(raw), "compliance": load_compliance(raw)}
