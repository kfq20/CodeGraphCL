#!/usr/bin/env bash
# Harbor verifier for fastify_404_unsupported_method (unsupported method returns 405 not 404).
# Runs the gold tests `Not found on supported method (should return a 404)` + `Not found on
# unsupported method (should return a 404)` (added by commit fa5e591b7ab3). On base, the
# unsupported-method case returns 405 -> test FAILS. After gold (405 -> 404), both return 404 ->
# test PASSES.
#
# Anti-hardcoding: near-miss variants (keep 405 / use a different wrong code) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/404s.test.js --grep 'Not found on'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/404s.test.js --grep 'Not found on' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
