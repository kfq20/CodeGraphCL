#!/usr/bin/env bash
# Harbor verifier for httpx_headers_keyerror (Headers.__delitem__ raises KeyError on absent key).
# Runs the gold test added by commit 0f34f3b — tests/client/test_headers.py::test_header_does_not_exist.
# On base, deleting a non-existent header silently no-ops (no KeyError) -> test FAILS.
# After gold (Headers.__delitem__ raises KeyError(key) when no matching key found), correct -> PASSES.
#
# Anti-hardcoding: near-miss variants (raise ValueError instead of KeyError; or silently return)
# re-fail because pytest.raises(KeyError) is not satisfied.
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

OUTPUT=$(python -m pytest tests/client/test_headers.py::test_header_does_not_exist \
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
