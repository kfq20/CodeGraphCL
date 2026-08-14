#!/usr/bin/env bash
# Harbor verifier for httpx_multipart_header_encoding (HTML5-form-encoded header params).
# Runs the gold tests added by commit fb17459 — tests/test_multipart.py::TestHeaderParamHTML5Formatting.
# On base, multipart header params use urllib quote() which encodes differently from HTML5 form
# encoding (e.g. backslash is not escaped, control chars not percent-encoded) -> FAILS.
# After gold (_format_param with HTML5 regex), correct encoding -> PASSES.
#
# Anti-hardcoding: near-miss variants (only quote, not HTML5; or missing control-char encoding) re-fail.
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

OUTPUT=$(python -m pytest tests/test_multipart.py::TestHeaderParamHTML5Formatting \
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
