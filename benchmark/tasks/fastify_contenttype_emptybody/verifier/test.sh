#!/usr/bin/env bash
# Harbor verifier for fastify_contenttype_emptybody (custom parser rejects empty bodies).
# Runs the gold tests `Should parse empty bodies as a string` + `... as a buffer` (added by
# commit 8c5e732f2e9b). On base, the zero-length-body early-reject fires -> test FAILS. After
# gold (remove the early-reject), the custom parser receives empty input -> test PASSES.
#
# Anti-hardcoding: near-miss variants (keep the reject but for a different reason / reject only
# some empty bodies) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/custom-parser.test.js --grep 'parse empty bodies as a string'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/custom-parser.test.js --grep 'parse empty bodies as a string' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
