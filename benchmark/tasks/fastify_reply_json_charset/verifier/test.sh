#!/usr/bin/env bash
# Harbor verifier for fastify_reply_json_charset (JSON+charset content type clobbered).
# Runs the gold test `Reply should handle JSON content type with a charset` (added by commit
# 2f4a84317885). On base, the exact-match JSON check misses the charset-suffixed form -> the
# JSON path is skipped -> test FAILS. After gold (substring match + charset guard), the JSON
# path is taken and the caller's charset is preserved -> test PASSES.
#
# Anti-hardcoding: near-miss variants (substring-match but no charset guard / keep exact match)
# re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/internals/reply.test.js --grep 'JSON content type with a charset'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/internals/reply.test.js --grep 'JSON content type with a charset' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
