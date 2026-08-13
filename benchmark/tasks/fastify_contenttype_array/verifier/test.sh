#!/usr/bin/env bash
# Harbor verifier for fastify_contenttype_array (register one parser for multiple content types).
# Runs the gold test `contentTypeParser should handle an array of custom contentTypes` (added by
# commit 7f378355). On base, addContentTypeParser(['jsoff','ffosj'], ...) registers only one type
# (or the array is passed where a string is expected) -> the second POST (ffosj) fails to parse ->
# test FAILS. After the gold source fix (iterate the array), both types parse -> test PASSES.
#
# Anti-hardcoding: near-miss variants (register only the first / last element, or treat the array
# as a single string) re-fail the second-type assertion.
#
# Runs in cgcl-fs-box (node:20). tap on custom-parser.test.js --grep 'array'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/custom-parser.test.js --grep "array" 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
