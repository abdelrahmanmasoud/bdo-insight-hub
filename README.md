# BDO Insight Hub

From fragmented departmental data to a client-ready **KI- & Customer-Experience-Strategie** – and the sales/marketing material to sell it.
Interview project for the Management Advisory team.

```
raw data (5 Fachbereiche) → ingest → data-quality gate → unified client view
   → AI analytics (monitoring · CX · strategy canvas) → 4 audience versions · pitch deck · one-pager · backlog
```

## Run the website (localhost, dev only)
```powershell
pip install -r requirements.txt
$env:PYTHONPATH = "src"                       # once per PowerShell window
python -m insight_hub serve                   # → http://localhost:8000
```
The local site always runs the **dev** environment. Staging and production exist only in the GitHub pipeline (see below). Use the **EN / DE switch** and the client selector at the top, then the tabs: Homepage, data integration, monitoring, CX, strategy examples, **4 audience presentations**, sales & marketing. The site, the one-pager and the CEO/CFO/IT decks follow the chosen language; the prospect pitch is always German.

### Data integration: upload your own files
The **Data integration** tab has one upload field per department (Sales, Finance, Marketing, Customer Experience, Compliance). Accepted: **CSV, TSV, JSON, XLSX** (and Markdown for compliance). Every page, presentation and the Excel analysis recompute immediately; invalid files are rejected with a message and nothing changes. Uploads are stored in `data/uploads/` (git-ignored); "Use default data" removes them.
Ready-made example files for all departments are in **`data/upload_samples/`** (also downloadable in the tab); regenerate them with `python scripts/make_upload_samples.py`.

| Department | Required columns |
|---|---|
| Sales (`crm`) | `client_id, client_name, industry, mandate, stage, value_eur, owner` |
| Finance (`finance`) | `client_id, project, budget_eur, spent_eur` |
| Marketing (`social`) | `id, client_id, date, channel, text` |
| Customer Experience (`cx`) | `client_id, date, touchpoint, score, churned, comment` |
| Compliance (`compliance`) | `client_id, topic, status` (Markdown: `- C001 \| topic \| open`) |

## Delivery pipeline on GitHub (dev → staging → production)
```
feature/* ──PR──► dev ──PR──► staging ──PR──► main
                   │            │              │
              env: dev    env: staging   env: production (manual approval)
```
| Environment | Branch | Data-quality gate | Where it runs |
|---|---|---|---|
| dev | `dev` | lenient (errors reported) | GitHub Actions + local website |
| staging | `staging` | strict (errors block) | GitHub Actions only |
| production | `main` | strict + manual approval | GitHub Actions only |

Every pull request runs ruff and the tests (`ci.yml`); every push to `dev`, `staging` or `main` runs `deploy.yml` with that environment's config from `config/env/` and uploads the results as a build artifact. Setup: **docs/GITHUB_STEPS.md**, branching rules: **docs/BRANCHING.md**.

## Other commands
```powershell
python -m unittest discover -s tests -v        # run the tests
python -m insight_hub run                      # writes files to output/dev (decks, Word, Excel, one-pager)
python scripts/make_sample_data.py             # regenerate the sample data and the upload examples
```

## Layout
| Path | Purpose |
|---|---|
| `server.py`, `web/index.html`, `decks.py` | Local web app, API, 4 audience presentations |
| `src/insight_hub/ingest.py`, `model.py`, `dq.py` | Datenintegration, unified model, quality gate |
| `monitoring.py`, `cx.py`, `strategy.py` | Social/product monitoring, CX churn drivers, KI-Strategie canvas |
| `i18n.py` | English/German labels shared by decks, reports and the API |
| `reports.py`, `marketing.py`, `office_export.py` | 4 audience versions, Marketingunterlagen, Word/PowerPoint/Excel |
| `feedback.py` | Win/loss loop → continuous improvement of offers |
| `config/` | Per-client strategy config, offers, per-environment settings (used by the GitHub pipeline) |
| `.github/`, `scripts/setup_github.sh` | CI, deploy dev/staging/production, PR template, repo setup |
| `data/raw/`, `data/upload_samples/` | Default department data; example files to upload (CSV, JSON, XLSX) |
| `docs/` | Branching, agile backlog, requirement-to-code map |

## Job-ad map: Aufgaben
| Aufgabe laut Anzeige | Code |
|---|---|
| KI-/Datenstrategien, Integration von Daten aus Fachbereichen/Quellen | `strategy.py`, `ingest.py`, `model.py` |
| Artefakte im agilen Prozess, Codereviews, Staging | `docs/BACKLOG.md`, `PULL_REQUEST_TEMPLATE.md`, `deploy.yml` |
| Projektmanagement | Backlog mit User Stories, Status und DoD |
| Adressatengerechte Präsentationen | `reports.py` |
| Verkaufspräsentationen, Marketingunterlagen, Verbesserung der Angebote | `office_export.py`, `marketing.py`, `feedback.py` |

The full requirement-to-code map is in **docs/REQUIREMENTS_MAP.md** (English) and **docs/REQUIREMENTS_MAP.de.md** (Deutsch).

**Data-quality severities:** `error` stops staging/production from starting (dev only reports it); `warning` and `info` never block. Fix errors in the source data instead of disabling the gate.
