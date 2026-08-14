#!/usr/bin/env bash
# Harbor verifier for fastify_log_after_error_handler.
# Runs the gold test block in test/logger.test.js added by commit 01b09784 — two subtests
# about error logging after customErrorHandler. On base, the error is logged BEFORE
# customErrorHandler runs, so when the handler sends a 400 response, the log shows the
# error at 500 level (level=50) before the handler completes — the test expects level=30
# (info) and statusCode=400, so it FAILS. After gold (move logging after customErrorHandler),
# the error is logged only after the handler processes it — level=30, statusCode=400 — PASSES.
#
# Anti-hardcoding: near-miss variants (remove only the 500 block / remove only the 400 block)
# re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/logger.test.js --grep 'custom error handler'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/logger.test.js --grep 'custom error handler' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
