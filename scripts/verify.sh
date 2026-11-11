#!/usr/bin/env bash
#
# Stable entry point. Everyone — humans, agents, CI, git hooks — runs this:
#
#   bash scripts/verify.sh
#
# It delegates to framework/craft.py. The command never changes, so nothing in
# AGENTS.md, CI, the skills or a git hook has to change when the framework is
# upgraded.
#
# This file is bash rather than Python for one reason: if Python is missing,
# a Python script cannot tell you so.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PY=""
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
      PY="$candidate"
      break
    fi
  fi
done

if [ -z "$PY" ]; then
  printf '\033[31m✗ verify cannot run\033[0m\n'
  printf '  Python 3.8 or newer is required and was not found on PATH.\n'
  printf '  Install it, then run this again. See framework/tooling.md.\n'
  exit 1
fi

exec "$PY" -I "$ROOT/framework/craft.py" verify "$@"
