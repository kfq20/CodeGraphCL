#!/usr/bin/env bash
# Harbor verifier for fastify_route_404_to_handler (404 error from route renders JSON not not-found body).
# Runs the gold test block in test/404s.test.js added by commit 63fce75e — the "with error object"
# subtest under "customized 404" + "404 inside onSend". On base, a route-sent 404 falls to
# generic error serialization -> the body is JSON not the notFound handler's body -> FAILS.
# After gold (route 404 to notFound helper), the notFound handler's body is returned -> PASSES.
#
# Anti-hardcoding: near-miss variants (check only one of status/statusCode / don't reset
# re-entrancy flags) re-fail.
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
