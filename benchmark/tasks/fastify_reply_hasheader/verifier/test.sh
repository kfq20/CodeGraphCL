#!/usr/bin/env bash
# Harbor verifier for fastify_reply_hasheader (no way to check if a header is set).
# Runs the gold test `reply.hasHeader returns correct values` (added by commit 31c5f7e259d1).
# On base there is no hasHeader -> test FAILS. After gold (return _headers[lower] !== undefined),
# set returns true and unset returns false -> test PASSES.
#
# Anti-hardcoding: near-miss variants (invert the check / delegate to res) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/internals/reply.test.js --grep 'hasHeader returns correct'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/internals/reply.test.js --grep 'hasHeader returns correct' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
