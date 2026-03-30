#!/bin/bash
# Auto-commit and push changes to GitHub
cd "$(dirname "$0")/.."

# Check if there are any changes
if ! git diff --quiet || ! git diff --staged --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add -A
  git commit -m "auto: update $(date '+%Y-%m-%d %H:%M')"
  git push origin main
fi
