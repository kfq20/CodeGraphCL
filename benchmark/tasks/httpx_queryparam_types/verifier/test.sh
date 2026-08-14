#!/usr/bin/env bash
# Harbor verifier for httpx_queryparam_types (primitive type coercion for query params).
# Runs the gold test added by commit 66754ad — tests/models/test_queryparams.py::test_queryparam_types.
# On base, QueryParams({"a": True}) -> str(q) == "a=True" (Python str(True)), not "a=true" -> FAILS.
# After gold (str_query_param coerces bool->"true"/"false", None->""), correct -> PASSES.
#
# Anti-hardcoding: near-miss variants (only handle bool, not None; or wrong None handling) re-fail.
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

OUTPUT=$(python -m pytest tests/models/test_queryparams.py::test_queryparam_types \
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
