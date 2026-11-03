# Push to GitHub (Windows PowerShell)

## A. Create the repository on github.com (no extra tools)
1. github.com → **New repository** → name `bdo-insight-hub` → **Private** → do NOT add README/.gitignore → Create.
2. In PowerShell, inside the project folder (the one containing `src`):
```powershell
git init -b main
git add .
git commit -m "feat: initial BDO Insight Hub"
git remote add origin https://github.com/<YOUR_USER>/bdo-insight-hub.git
git push -u origin main
```
3. Create the other two long-lived branches:
```powershell
git branch staging; git push -u origin staging
git branch dev;     git push -u origin dev
```
4. GitHub → **Settings → Environments** → create `dev`, `staging`, `production`. In `production` enable **Required reviewers** (yourself).
5. GitHub → **Settings → Branches** → add protection for `main`, `staging`, `dev`: require a pull request and the status check `test`.
6. Edit `.github/CODEOWNERS` and replace `@YOUR_GITHUB_USERNAME`.

## B. Same with GitHub CLI (optional)
```powershell
winget install GitHub.cli ; gh auth login
bash scripts/setup_github.sh <YOUR_USER>/bdo-insight-hub     # needs Git Bash
```

## C. Daily workflow
```powershell
git switch dev ; git pull
git switch -c feature/my-change
# ...edit, run tests...
git add . ; git commit -m "feat: ..." ; git push -u origin feature/my-change
```
Open a pull request into `dev` → CI runs → review → merge. Then PR `dev → staging`, then `staging → main` (production, needs approval).
Each push to `dev`, `staging`, `main` triggers `deploy.yml`, which runs the pipeline with that environment's config and uploads the results as a build artifact.
