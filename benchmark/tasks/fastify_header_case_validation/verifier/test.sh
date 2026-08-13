#!/usr/bin/env bash
# Harbor verifier for fastify_header_case_validation (required-header validation case-sensitive).
# Runs the gold test `case insensitive header validation` (added by commit 2907be7c5352). On
# base, required headers are compared case-sensitively -> a case-mismatched required header is
# reported missing -> test FAILS. After gold (lowercase the required array), it's accepted ->
# test PASSES.
#
# Anti-hardcoding: near-miss variants (map as identity / lowercase the wrong object) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/input-validation.test.js --grep 'case insensitive header validation'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/input-validation.test.js --grep 'case insensitive header validation' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
