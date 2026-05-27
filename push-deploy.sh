#!/usr/bin/env bash
# push-deploy.sh — push to both remotes.
#   origin  → public holo-mvp (no governor)
#   deploy  → private holo-deploy (full engine)
#
# Usage: ./push-deploy.sh [commit message for governor update]
#        If no changes to context_governor.py, governor commit is skipped.

set -e

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Error: must be on main branch (currently on $CURRENT_BRANCH)" >&2
  exit 1
fi

# Push public repo first
echo "→ Pushing to origin (public)..."
git push origin main

# Build deploy branch with governor included
echo "→ Building deploy branch..."
git checkout -b _deploy-tmp

# Recover context_governor.py from reflog if it was wiped by a branch switch
if [ ! -f context_governor.py ]; then
  RECOVERY_SHA=$(git reflog --all | grep -E "governor|proprietary" | head -1 | awk '{print $1}')
  if [ -n "$RECOVERY_SHA" ]; then
    echo "  Recovering context_governor.py from reflog ($RECOVERY_SHA)..."
    git show "$RECOVERY_SHA:context_governor.py" > context_governor.py
  else
    echo "  Error: context_governor.py not found and cannot recover from reflog" >&2
    git checkout main
    exit 1
  fi
fi

# Force-add governor if it exists and has changes relative to deploy/main
if [ -f context_governor.py ]; then
  git add -f context_governor.py
  if ! git diff --cached --quiet; then
    git commit -m "deploy: update context_governor.py"
  else
    git reset HEAD context_governor.py
    echo "  context_governor.py unchanged — skipping governor commit"
  fi
else
  echo "  Warning: context_governor.py not found on disk" >&2
fi

# Remove GitHub Actions workflows (token lacks workflow scope)
if [ -d .github/workflows ]; then
  git rm -r --cached .github/workflows/ --quiet 2>/dev/null || true
  if ! git diff --cached --quiet; then
    git commit -m "deploy: strip CI workflows"
  fi
fi

echo "→ Pushing to deploy (private)..."
git push deploy _deploy-tmp:main --force

echo "→ Cleaning up..."
git checkout main
git branch -D _deploy-tmp

echo "Done. Both remotes updated."
