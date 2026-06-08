#!/usr/bin/env bash
# push-deploy.sh — push to both remotes.
#   origin  → public holo-mvp (no governor)
#   deploy  → private holo-deploy (full engine)
#
# Usage: ./push-deploy.sh
#
# The ONLY authoritative source for context_governor.py is:
#   private_materials_not_for_public_release/context_governor.py
#
# This script NEVER recovers context_governor.py from reflog, stash, cache,
# or any fallback. If the private source is missing or fails validation, the
# deploy is aborted loudly.

set -euo pipefail

PRIVATE_GOVERNOR="private_materials_not_for_public_release/context_governor.py"
MIN_LINE_COUNT=3000

abort() {
  echo ""
  echo "DEPLOY ABORTED: $1" >&2
  echo "Refusing to deploy stale or missing context_governor.py." >&2
  # Clean up temp branch if we created it
  if git rev-parse --verify _deploy-tmp >/dev/null 2>&1; then
    git checkout main 2>/dev/null || true
    git branch -D _deploy-tmp 2>/dev/null || true
  fi
  exit 1
}

# ── Guard: must be on main ──────────────────────────────────────────────────
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  abort "Must be on main branch (currently on $CURRENT_BRANCH)."
fi

# ── Validate private source ─────────────────────────────────────────────────
echo "→ Validating private context_governor.py..."

if [ ! -f "$PRIVATE_GOVERNOR" ]; then
  abort "Real private context_governor.py not found at $PRIVATE_GOVERNOR"
fi

ACTUAL_LINES=$(wc -l < "$PRIVATE_GOVERNOR")
if [ "$ACTUAL_LINES" -lt "$MIN_LINE_COUNT" ]; then
  abort "context_governor.py has only $ACTUAL_LINES lines (minimum $MIN_LINE_COUNT). Found stale stub — refusing to deploy."
fi

if ! grep -q "^class ContextGovernor:" "$PRIVATE_GOVERNOR"; then
  abort "context_governor.py does not contain 'class ContextGovernor:' — file is wrong or corrupted."
fi

echo "  ✓ Private source OK ($ACTUAL_LINES lines, class ContextGovernor found)"

# ── Push public repo first ─────────────────────────────────────────────────
echo "→ Pushing to origin (public, no governor)..."
git push origin main

# ── Build deploy branch ────────────────────────────────────────────────────
echo "→ Building deploy branch..."
git checkout -b _deploy-tmp

# Copy the authoritative private governor to the deploy root
echo "  Copying $PRIVATE_GOVERNOR → context_governor.py"
cp "$PRIVATE_GOVERNOR" context_governor.py

# Verify the copy matches the source (hash check)
SRC_HASH=$(shasum -a 256 "$PRIVATE_GOVERNOR" | awk '{print $1}')
DST_HASH=$(shasum -a 256 context_governor.py | awk '{print $1}')
if [ "$SRC_HASH" != "$DST_HASH" ]; then
  abort "context_governor.py copy hash mismatch (source: $SRC_HASH, dest: $DST_HASH)."
fi
echo "  ✓ Hash verified: $SRC_HASH"

# Force-add and commit governor
git add -f context_governor.py
if ! git diff --cached --quiet; then
  git commit -m "deploy: update context_governor.py"
else
  git reset HEAD context_governor.py
  echo "  context_governor.py unchanged — skipping governor commit"
fi

# Remove GitHub Actions workflows (token lacks workflow scope)
if [ -d .github/workflows ]; then
  git rm -r --cached .github/workflows/ --quiet 2>/dev/null || true
  if ! git diff --cached --quiet; then
    git commit -m "deploy: strip CI workflows"
  fi
fi

# ── Smoke tests ────────────────────────────────────────────────────────────
echo "→ Running smoke tests..."

PYTHON=$(command -v python3 || command -v python || abort "No python3 or python found in PATH.")

"$PYTHON" -m compileall . -q 2>&1 || abort "python -m compileall failed — syntax error in deploy tree."

"$PYTHON" -c "from context_governor import ContextGovernor; print('  ✓ ContextGovernor import ok:', ContextGovernor)" \
  || abort "from context_governor import ContextGovernor failed — deploy would crash on startup."

"$PYTHON" -c "from main import app; print('  ✓ main import ok')" \
  || abort "from main import app failed — deploy would crash on startup."

echo "  ✓ All smoke tests passed"

# ── Push to holo-deploy ────────────────────────────────────────────────────
echo "→ Pushing to deploy (private holo-deploy)..."
git push deploy _deploy-tmp:main --force

# ── Cleanup ────────────────────────────────────────────────────────────────
echo "→ Cleaning up..."
git checkout main
git branch -D _deploy-tmp

echo ""
echo "Done. Both remotes updated."
echo "  origin  → public holo-mvp (no governor)"
echo "  deploy  → private holo-deploy (with real context_governor.py)"
echo ""
echo "Manually trigger a redeploy on both Railway services if needed."
