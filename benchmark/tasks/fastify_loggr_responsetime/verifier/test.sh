#!/usr/bin/env bash
# Harbor verifier for fastify_loggr_responsetime (fix responseTime regression).
# Runs the gold test `The logger should add a timestamp if logging to stdout` (added by commit
# 288903a3). On base, the hasLogger flag is inverted (false when a logger is present), so the
# response-completion callback is a no-op and the "request completed" log line carries no
# responseTime field -> the `t.ok(line.responseTime)` assertion FAILS. After gold (invert
# hasLogger + select the real callback when logging), responseTime is computed and present ->
# test PASSES.
#
# Anti-hardcoding: near-miss variants (don't guard _startTime / swap the callback selection back)
# re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/internals/logger.test.js --grep 'should add a timestamp'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/internals/logger.test.js --grep 'should add a timestamp' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
