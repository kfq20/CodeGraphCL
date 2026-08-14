#!/usr/bin/env bash
# Harbor verifier for fastify_404_route_handler (route 404 errors to the 404 handler).
# Runs the gold test `customized 404` (extended by commit 63fce75e with a `with error object`
# subtest). On base, a 404-status error sent from a route handler is handled as a generic
# error: status is 404 but the body is the JSON error object, NOT the custom 404 handler's
# body ('this was not found') -> the body assertion FAILS. After gold (intercept 404 errors
# in handleError and delegate to the notFound 404-context handler), the custom 404 handler
# runs and its body is sent -> test PASSES.
#
# Anti-hardcoding: near-miss variants (don't reset sent/_isError / don't actually switch the
# context to the 404 handler) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/404s.test.js --grep 'customized 404'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/404s.test.js --grep 'customized 404' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
