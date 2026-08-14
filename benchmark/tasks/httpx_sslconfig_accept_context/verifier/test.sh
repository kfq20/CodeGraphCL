#!/usr/bin/env bash
# Harbor verifier for httpx_sslconfig_accept_context (accept SSLContext into SSLConfig(verify=...)).
# Runs the gold test added by commit df8874b — tests/test_config.py::test_load_ssl_context.
# On base, passing an SSLContext as verify= raises (only str/bool accepted) -> FAILS.
# After gold (SSLConfig detects SSLContext type, stashes it, sets verify=True), correct -> PASSES.
#
# Anti-hardcoding: near-miss variants (accept SSLContext but don't load client certs; or don't
# set verify=True) re-fail.
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

OUTPUT=$(python -m pytest tests/test_config.py::test_load_ssl_context \
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
