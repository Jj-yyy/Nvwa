#!/usr/bin/env bash
# upload_to_nvwa.sh
# Interactive helper to init, commit and push this project to git@github.com:tan829/Nvwa.git or HTTPS

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Uploading project in: $ROOT_DIR"

read -p "Include static folder? (Y/n) " include_static
if [[ "$include_static" =~ ^([nN])$ ]]; then
  ADD_CMD="git add main.py README.md .gitignore"
else
  ADD_CMD="git add ."
fi

read -p "Choose remote type: [1] SSH (recommended)  [2] HTTPS : " choice
if [[ "$choice" == "1" ]]; then
  REPO_URL="git@github.com:tan829/Nvwa.git"
elif [[ "$choice" == "2" ]]; then
  REPO_URL="https://github.com/tan829/Nvwa.git"
else
  echo "Invalid choice"; exit 1
fi

# Init repo if not already
if [ ! -d .git ]; then
  echo "Initializing git repository..."
  git init
else
  echo "Git repository already initialized."
fi

# Switch/create main branch
git checkout -B main

# Ensure user config
git config user.name "tan829"
if ! git config user.email >/dev/null; then
  git config user.email "you@example.com"
fi

# Add and commit
echo "Running: $ADD_CMD"
eval $ADD_CMD
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "Add main.py, static assets, README and .gitignore"
fi

# Set remote and push
git remote remove origin 2>/dev/null || true
git remote add origin $REPO_URL

echo "Pushing to $REPO_URL ..."
if [[ "$choice" == "2" ]]; then
  echo "If using HTTPS you'll be prompted for username and PAT as password."
fi

git push -u origin main

echo "Push complete."

exit 0
