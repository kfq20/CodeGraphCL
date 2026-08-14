#!/usr/bin/env bash
# Harbor verifier for fastify_delete_body_check.
# Runs the gold test block in test/delete.test.js added by commit ef873bf0 — the subtest
# 'shorthand - delete with application/json Content-Type header and without body'. On base,
# a DELETE with Content-Type: application/json but no body triggers the content-type parser,
# which fails (415 or parse error) because there is no body to parse. After gold (check for
# body indicators before parsing), the parser is skipped and the handler is called directly.
#
# Anti-hardcoding: near-miss variants (negate the body-indicator check / revert to original
# contentType === undefined check) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/delete.test.js --grep 'shorthand - delete'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/delete.test.js --grep 'shorthand - delete with application/json Content-Type header and without body' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
