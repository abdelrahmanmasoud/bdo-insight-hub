# Agile artefacts

## Definition of Done
Tests green · reviewed by one person · configurable (no hard-coded client values) · docs updated · deployed to dev.

## Sprint 1 – user stories
| ID | As a… | I want… | Acceptance criteria | Status |
|---|---|---|---|---|
| US-1 | Consultant | one unified view per client across 5 departments | every client has records from all sources; test `test_five_sources_join…` | done |
| US-2 | Partner | an early warning for rising negative topics | emerging issue detected for C001/delivery | done |
| US-3 | Consultant | a scored, prioritised AI roadmap | score, wave, measured data readiness | done |
| US-4 | CEO / CFO / IT / prospect | the same insight in my language | 4 distinct versions; prospect version has no financials | done |
| US-5 | Marketing | a printable one-pager from live stats | `marketing_onepager.html` | done |
| US-6 | Sales lead | to learn which offers win | win rate + action per offer → backlog file | done |
| US-7 | Platform owner | staging before production | CI/CD with 3 environments + approval | done |
| US-8 | Data scientist | an LLM-based classifier | same interface as `monitoring.sentiment` | next |
| US-9 | Security | PII scan during ingestion | no PII leaves ingest layer | next |
