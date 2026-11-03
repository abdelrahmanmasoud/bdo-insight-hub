# Branching, environments and Codereview

```
feature/* ──PR──► dev ──PR──► staging ──PR──► main
                   │            │              │
              env: dev    env: staging   env: production (manual approval)
```
- Every PR needs green CI (ruff + tests on Python 3.11/3.12) and **one approving Codereview** (see PR template).
- `dev`: lenient data-quality gate, fast feedback. `staging`: strict gate, production-like. `main`: strict gate + approval by reviewers.
- Config differs only in `config/env/<env>.json`; code is identical in all environments.
- Set up with `scripts/setup_github.sh <owner>/bdo-insight-hub`.
- The local website runs **dev only** (`python -m insight_hub serve`); staging and production run only through the GitHub pipeline.
