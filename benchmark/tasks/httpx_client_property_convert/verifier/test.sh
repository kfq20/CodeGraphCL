#!/usr/bin/env bash
# Harbor verifier for httpx_client_property_convert (Client.headers/cookies coerce on assignment).
# Runs the gold tests added by commit 9e420a5:
#   tests/client/test_properties.py::test_client_headers
#   tests/client/test_properties.py::test_client_cookies
#   tests/client/test_cookies.py::test_setting_client_cookies_to_cookiejar
# On base, assigning client.headers = {...} overwrites the instance attribute with a raw dict, so
# isinstance(client.headers, Headers) is False -> tests FAIL.
# After gold (headers/cookies become @property with a setter that wraps via Headers()/Cookies()),
# assignment coerces -> isinstance True, values normalized -> PASSES.
#
# Anti-hardcoding: near-miss variants (cookies setter does not coerce; headers setter does not
# coerce) re-fail the corresponding isinstance / round-trip assertions.
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

OUTPUT=$(python -m pytest \
  tests/client/test_properties.py::test_client_headers \
  tests/client/test_properties.py::test_client_cookies \
  tests/client/test_cookies.py::test_setting_client_cookies_to_cookiejar \
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
