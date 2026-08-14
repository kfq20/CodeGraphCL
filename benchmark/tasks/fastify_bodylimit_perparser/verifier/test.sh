#!/usr/bin/env bash
# Harbor verifier for fastify_bodylimit_perparser (per-parser body limits + route precedence).
# Runs the gold tests `Should allow defining the bodyLimit per parser` and `route bodyLimit
# should take precedence over a custom parser bodyLimit` (added by commit dab20bd9). On base,
# addContentTypeParser accepts no bodyLimit option and the route limit is ignored when parsing,
# so a 10-byte body against a parser limit of 5 is NOT rejected (413) -> tests FAIL. After gold
# (thread per-parser bodyLimit; select route-limit > parser-limit > global at read time), the
# over-limit body is rejected with 413 -> tests PASS.
#
# Anti-hardcoding: near-miss variants (ignore the parser limit / always use the parser limit)
# re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/custom-parser.test.js --grep 'bodyLimit per parser|take precedence over a custom parser bodyLimit'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/custom-parser.test.js --grep 'bodyLimit per parser|take precedence over a custom parser bodyLimit' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
