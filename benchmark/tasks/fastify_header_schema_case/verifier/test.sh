#!/usr/bin/env bash
# Harbor verifier for fastify_header_schema_case.
# Runs the header-schema tests in test/get.test.js as updated by commit 746e307c — the schema gains
# a 'Y-Test' property and the request sends a 'Y-Test: 3' header. Node lower-cases incoming header
# names, so on base the schema's original-cased 'Y-Test' property never matches the request's
# 'y-test' key: ajv (coerceTypes) never coerces it, the echoed body has the string '3', and
# t.strictEqual(body['y-test'], 3) FAILS. After gold (lower-case the schema's property keys before
# compiling), 'y-test' matches, is coerced to the number 3 — PASSES.
#
# Anti-hardcoding: near-miss variants (lower-case only the schema's top-level keys / lower-case the
# property keys to the wrong case) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/get.test.js --grep 'headers'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/get.test.js --grep 'headers' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
