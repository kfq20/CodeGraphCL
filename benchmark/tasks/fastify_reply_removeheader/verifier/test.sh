#!/usr/bin/env bash
# Harbor verifier for fastify_reply_removeheader (no way to remove a set response header).
# Runs the gold test `reply.removeHeader can remove the value` (added by commit cfa760cbd129).
# On base there is no removal method -> the test throws / the header stays -> test FAILS. After
# gold (delete the lowercased key from the header store), the header is removed -> test PASSES.
#
# Anti-hardcoding: near-miss variants (set to undefined instead of deleting / don't lowercase)
# re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/internals/reply.test.js --grep 'removeHeader can remove'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/internals/reply.test.js --grep 'removeHeader can remove' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
