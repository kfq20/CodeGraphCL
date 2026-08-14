#!/usr/bin/env bash
# Harbor verifier for fastify_prefix_trailing_slash (plugin prefix ending in '/' produces
# double-slash route URLs). Runs the gold test block in test/route-prefix.test.js added by
# commit 14a1e9d1 — the "Prefix with trailing /" subtest. On base, a plugin registered with
# prefix '/v1/' and a route '/route' produces path '/v1//route' (double slash), which doesn't
# match incoming '/v1/route' -> the route is not found -> FAILS. After gold (strip leading
# '/' from the route path when the prefix ends with '/'), the URL is '/v1/route' and the
# nested '/v1/inner/route2' is correct -> PASSES.
#
# Anti-hardcoding: near-miss variants (fix only buildRoutePrefix / fix only afterRouteAdded)
# re-fail on different sub-assertions.
#
# Runs in cgcl-fs-box (node:20). tap on test/route-prefix.test.js --grep 'Prefix with trailing'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -f ./node_modules/.bin/tap ]; then
  npm install --no-audit --no-fund --ignore-scripts > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/route-prefix.test.js --grep 'Prefix with trailing' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
