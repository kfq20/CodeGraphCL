#!/usr/bin/env bash
# Harbor verifier for httpx_json_encoding_detection (encoding detection in Response.json).
# Runs the gold tests added by commit 5442006 — tests/models/test_responses.py (json encoding
# detection tests) and tests/test_utils.py (guess_json_utf unit tests). On base, .json() blindly
# decodes content as utf-8, so non-utf-8 JSON (utf-16/utf-32) raises UnicodeDecodeError -> FAILS.
# After gold (guess_json_utf detects encoding from BOM/null-byte pattern), correct decode -> PASSES.
#
# Anti-hardcoding: near-miss variants (only BOM, no null-byte; or wrong null-byte logic) re-fail.
#
# Runs in cgcl-httpx-box (python:3.11-slim).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

# Install httpx in editable mode (quiet). Override addopts to skip --cov (no pytest-cov installed).
if ! python3 -c "import http3" 2>/dev/null; then
  pip install -e . -q > "$logs_dir/verifier/pip_install.log" 2>&1
fi

OUTPUT=$(python -m pytest tests/models/test_responses.py::test_json_with_specified_encoding \
  tests/models/test_responses.py::test_json_without_specified_encoding \
  tests/models/test_responses.py::test_json_without_specified_encoding_decode_error \
  tests/test_utils.py \
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
