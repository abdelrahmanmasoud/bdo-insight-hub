## What & why
<!-- one paragraph; link the user story from docs/BACKLOG.md -->

## Codereview checklist
- [ ] Tests added or updated, `make test` is green
- [ ] No real client data or secrets in the diff (sample data only)
- [ ] New behaviour is configurable per client/environment, not hard-coded
- [ ] Readable: names, small functions, docstring where logic is not obvious
- [ ] Data-quality impact considered (dev/staging lenient, production strict)
- [ ] Docs updated (README / docs/)

## Target branch
`feature/*` → `dev` → `staging` → `main` (production)
