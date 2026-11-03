# Anforderung → Code (Stellenanzeige „Aufgaben“ und „Das bringst du mit“)

## Deine 14 Fragen
| # | Frage | Wo es steckt | So zeigst du es |
|---|---|---|---|
| 1 | Adressatengerechte Präsentation | `decks.py` (4 Präsentationen: CEO, CFO, IT, Interessenten DE), `reports.py`; Web-Tab *Präsentationen* (DE/EN) | je Kunde öffnen / herunterladen; Test `test_four_audience_presentations` |
| 2 | Marketingunterlagen | `marketing.py` → `output/<env>/marketing_onepager.html` | im Browser öffnen, Strg+P → PDF |
| 3 | Kontinuierliche Verbesserung der Angebote | `feedback.py`, `data/raw/offer_feedback.csv` → `improvement_backlog.md`; `reports.recommend_offers` | Win-Rate + Maßnahme je Angebot |
| 4 | Verkaufspräsentation | `office_export.sales_deck` → `C00x/sales_deck.pptx`; deutsches `pitch_de.md` | .pptx öffnen |
| 5 | GitHub + dev/staging/production | lokale Seite = nur dev; Staging/Production über GitHub Actions, `docs/GITHUB_STEPS.md`, `.github/workflows/ci.yml`, `deploy.yml`, `config/env/*.json`, `docs/BRANCHING.md`, `scripts/setup_github.sh` | Repo → Actions → Environments |
| 6 | Datenintegration aus Fachbereichen | `ingest.py`, `model.py`, `dq.py`; `data/raw/` (CSV, XLSX, JSON, Markdown), Upload im Tab *Datenintegration*, Beispiele in `data/upload_samples/` | Tabelle zur Quellenabdeckung in `output/dev/C001/technical.md` |
| 7 | Strategien, Konzepte, technische Lösungen | Web-Tab *KI-Strategie & Lösungen* (3 Live-Beispiele), `strategy.py` (KI-Strategie), `monitoring.py` (Social/Produkt), `cx.py` (CX), je Kunde konfigurierbar in `config/clients/` | `executive.md` von C001 |
| 8 | Überzeugende Persönlichkeit | die Präsentation (Story), Live-Demo, `README`-Pitch; du präsentierst Problem → Idee → Umsetzung → Ergebnis | 5-Minuten-Demo proben |
| 9 | MS-Office-Kenntnisse | `office_export.py`: PowerPoint, Word, Excel (und der Excel-*Input* in `ingest.load_finance`) | `analysis.xlsx`, `sales_deck.pptx`, `technical_appendix.docx` |
| 10 | Analytisch | Scoring-Modell (`strategy.py`), NPS und Churn-Lift (`cx.py`), Regel für aufkommende Themen (`monitoring.py`) | Formel in `technical.md` erklären |
| 11 | KI / neue Technologien | austauschbarer Klassifikator (`analyse(posts, classifier=...)`), KI-Use-Case-Scoring, GenAI/LLM als nächster Schritt US-8 | Backlog US-8 |
| 12 | Selbständig & strukturiert | Tests, CI, Backlog, DoD, Doku, Trennung von Konfiguration | `docs/BACKLOG.md` |
| 13 | Wie es alle Punkte abdeckt | diese Tabelle | |
| 14 | Relevanz für BDO | KI + CX + Social Monitoring + CSRD/AI-Act-Radar für Management-Advisory-Kunden | `pitch_de.md` |

## Aufgaben
| Aufgabe laut Anzeige | Code |
|---|---|
| KI-/Datenstrategien, Integration von Daten aus Fachbereichen/Quellen | `strategy.py`, `ingest.py`, `model.py` |
| Artefakte im agilen Prozess, Codereviews, Staging | `docs/BACKLOG.md`, `PULL_REQUEST_TEMPLATE.md`, `deploy.yml` |
| Projektmanagement | Backlog mit User Stories, Status und DoD |
| Adressatengerechte Präsentationen | `reports.py` |
| Verkaufspräsentationen, Marketingunterlagen, Verbesserung der Angebote | `office_export.py`, `marketing.py`, `feedback.py` |

## Das bringst du mit
| Anforderung | Code |
|---|---|
| Python, IDEs (VS Code/PyCharm), Grundlagen des Software Engineering | gesamtes `src/` (Python 3.11+, Tests, ruff, pre-commit) |
| Begeisterung für KI | `monitoring.py`, `strategy.py`, US-8 |
| Selbständig, strukturiert, analytisch | Tests, Doku, Scoring |
| Deutsch & Englisch | gesamte Website, interne Präsentationen und One-Pager auf Deutsch und Englisch (DE/EN-Umschalter im Header); Interessenten-Pitch immer deutsch |
| Sehr gute MS-Office-Kenntnisse | `office_export.py` |
