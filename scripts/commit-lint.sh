#!/usr/bin/env bash

set -euo pipefail

ignore_file=".git-blame-ignore-revs"

if git diff --cached --quiet; then
	echo "No staged changes to commit." >&2
	exit 1
fi

if ! git diff --cached --quiet -- "$ignore_file" || ! git diff --quiet -- "$ignore_file"; then
	echo "Commit changes to $ignore_file separately before running this command." >&2
	exit 1
fi

if git ls-files --others --exclude-standard -- "$ignore_file" | grep -q .; then
	echo "Add or remove the untracked $ignore_file before running this command." >&2
	exit 1
fi

git commit -m "🎨 (style): Format code with Ruff"
lint_commit="$(git rev-parse HEAD)"

printf '%s\n' "$lint_commit" >> "$ignore_file"
git add -- "$ignore_file"
git commit -m "🎨 (git): Ignore formatting commit in blame"
