#!/usr/bin/env bash
# Harbor verifier for httpx_url_copywith_authority (authority copy feature in URL.copy_with).
# Runs the gold test added by commit e6da325 — tests/models/test_url.py::test_url_copywith_for_authority.
# On base, calling copy_with(username=..., password=..., port=..., host=...) does not build the
# authority component, so the resulting URL is missing the userinfo/host/port -> assertions FAIL.
# After gold (copy_with detects component kwargs, builds authority string, delegates), PASSES.
#
# Anti-hardcoding: near-miss variants (build authority but forget userpass; or wrong port format) re-fail.
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

OUTPUT=$(python -m pytest tests/models/test_url.py::test_url_copywith_for_authority \
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
