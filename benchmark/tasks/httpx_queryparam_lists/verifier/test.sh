#!/usr/bin/env bash
# Harbor verifier for httpx_queryparam_lists (allow lists in query params).
# Runs the gold test added by commit 57ae7ea — tests/models/test_queryparams.py::test_queryparams
# (parametrized with list/tuple sources). On base, passing a dict with list values like
# {"a": ["123", "456"], "b": 789} raises TypeError (cannot convert list to str) -> FAILS.
# After gold (flatten_queryparams flattens list values into multiple key-value pairs), PASSES.
#
# Anti-hardcoding: near-miss variants (flatten lists but don't handle tuples; or flatten but
# corrupt the key) re-fail.
#
# Runs in cgcl-httpx-box (python:3.11-slim).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

if ! python3 -c "import httpx" 2>/dev/null; then
  pip install -e . -q > "$logs_dir/verifier/pip_install.log" 2>&1
fi

OUTPUT=$(python -m pytest tests/models/test_queryparams.py::test_queryparams \
  -x -p no:cacheprovider -o addopts="" 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
