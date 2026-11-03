# Requirement → code map (job ad "Aufgaben" and "Das bringst du mit")

## Your 14 questions
| # | Question | Where it lives | Show it with |
|---|---|---|---|
| 1 | Adressatengerechte Präsentation | `decks.py` (4 decks: CEO, CFO, IT, prospects DE), `reports.py`; web tab *Presentations* (EN/DE) | open / download per client; test `test_four_audience_presentations` |
| 2 | Marketingunterlagen | `marketing.py` → `output/<env>/marketing_onepager.html` | open in browser, Ctrl+P → PDF |
| 3 | Kontinuierliche Verbesserung der Angebote | `feedback.py`, `data/raw/offer_feedback.csv` → `improvement_backlog.md`; `reports.recommend_offers` | win rate + action per offer |
| 4 | Verkaufspräsentation | `office_export.sales_deck` → `C00x/sales_deck.pptx`; German `pitch_de.md` | open the .pptx |
| 5 | GitHub + dev/staging/production | local site = dev only; staging/production via GitHub Actions, `docs/GITHUB_STEPS.md`, `.github/workflows/ci.yml`, `deploy.yml`, `config/env/*.json`, `docs/BRANCHING.md`, `scripts/setup_github.sh` | repo → Actions → Environments |
| 6 | Datenintegration aus Fachbereichen | `ingest.py`, `model.py`, `dq.py`; `data/raw/` (CSV, XLSX, JSON, Markdown), upload in the *Data integration* tab, examples in `data/upload_samples/` | `output/dev/C001/technical.md` source coverage table |
| 7 | Strategien, Konzepte, technische Lösungen | web tab *KI strategy & solutions* (3 live examples), `strategy.py` (KI-Strategie), `monitoring.py` (Social/Produkt), `cx.py` (CX), configurable per client in `config/clients/` | `executive.md` of C001 |
| 8 | Überzeugende Persönlichkeit | the deck (story), live demo, `README` pitch; you present problem → idea → build → result | rehearse a 5-min demo |
| 9 | MS-Office-Kenntnisse | `office_export.py`: PowerPoint, Word, Excel (and the Excel *input* in `ingest.load_finance`) | `analysis.xlsx`, `sales_deck.pptx`, `technical_appendix.docx` |
| 10 | Analytisch | scoring model (`strategy.py`), NPS and churn lift (`cx.py`), emerging-issue rule (`monitoring.py`) | explain the formula in `technical.md` |
| 11 | KI / neue Technologien | pluggable classifier (`analyse(posts, classifier=...)`), AI use-case scoring, GenAI/LLM next step US-8 | backlog US-8 |
| 12 | Selbständig & strukturiert | tests, CI, backlog, DoD, docs, config separation | `docs/BACKLOG.md` |
| 13 | How it represents all points | this table | |
| 14 | Relevant for BDO | KI + CX + social monitoring + CSRD/AI-Act radar for Management Advisory clients | `pitch_de.md` |

## Aufgaben
| Task from the ad | Code |
|---|---|
| KI-/Datenstrategien, Integration von Daten aus Fachbereichen/Quellen | `strategy.py`, `ingest.py`, `model.py` |
| Artefakte im agilen Prozess, Codereviews, Staging | `docs/BACKLOG.md`, `PULL_REQUEST_TEMPLATE.md`, `deploy.yml` |
| Projektmanagement | backlog with user stories, status and DoD |
| Adressatengerechte Präsentationen | `reports.py` |
| Verkaufspräsentationen, Marketingunterlagen, Verbesserung der Angebote | `office_export.py`, `marketing.py`, `feedback.py` |

## Das bringst du mit
| Requirement | Code |
|---|---|
| Python, IDEs (VS Code/PyCharm), Software-Engineering-Grundlagen | whole `src/` (Python 3.11+, tests, ruff, pre-commit) |
| Begeisterung für KI | `monitoring.py`, `strategy.py`, US-8 |
| Selbständig, strukturiert, analytisch | tests, docs, scoring |
| Deutsch & Englisch | whole website, internal decks and one-pager in English and German (EN / DE switch in the header); prospect pitch always German |
| Sehr gute MS-Office-Kenntnisse | `office_export.py` |
