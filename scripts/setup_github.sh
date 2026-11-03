#!/usr/bin/env bash
# Creates the GitHub repo, the three long-lived branches, branch protection and environments.
# Requires: gh CLI logged in (gh auth login). Usage: ./scripts/setup_github.sh <owner>/bdo-insight-hub
set -euo pipefail
REPO="${1:?usage: setup_github.sh <owner>/<repo>}"
git init -b main 2>/dev/null || true
git add . && git commit -m "feat: initial BDO Insight Hub" || true
gh repo create "$REPO" --private --source=. --push
for b in staging dev; do git branch -f "$b" main && git push -u origin "$b"; done
for b in main staging dev; do
  gh api -X PUT "repos/$REPO/branches/$b/protection" --input - <<JSON
{"required_status_checks":{"strict":true,"contexts":["test (3.12)"]},"enforce_admins":false,
 "required_pull_request_reviews":{"required_approving_review_count":1},"restrictions":null}
JSON
done
for e in dev staging production; do gh api -X PUT "repos/$REPO/environments/$e" >/dev/null; done
echo "Done. Add required reviewers to the 'production' environment in Settings > Environments."
