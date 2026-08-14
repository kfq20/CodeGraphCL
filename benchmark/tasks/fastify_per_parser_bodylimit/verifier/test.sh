#!/usr/bin/env bash
# Harbor verifier for fastify_per_parser_bodylimit (per-parser bodyLimit not enforced).
# Runs the gold tests 'Should allow defining the bodyLimit per parser' + 'route bodyLimit should
# take precedence over a custom parser bodyLimit' (added by commit dab20bd9). On base, the
# parser's bodyLimit is ignored (route/default limit used) -> the 413 is not returned -> FAILS.
# After gold (thread bodyLimit through ContentTypeParser/Parser; select parser.bodyLimit when
# route limit is null), the per-parser limit is enforced -> PASSES.
#
# Anti-hardcoding: near-miss variants (always use parser limit ignoring route / use default)
# re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/custom-parser.test.js --grep 'bodyLimit per parser'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/custom-parser.test.js --grep 'bodyLimit' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
