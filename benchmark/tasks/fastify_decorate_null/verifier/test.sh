#!/usr/bin/env bash
# Harbor verifier for fastify_decorate_null (decorating with an empty value crashes).
# Runs the gold test `should register empty values` (added by commit adde52452d94). On base,
# decorate('test', null) reads fn.getter off null -> TypeError -> test FAILS. After gold (guard
# fn before the accessor check), null registers as the decorator -> test PASSES.
#
# Anti-hardcoding: near-miss variants (guard too late / guard the wrong thing) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/decorator.test.js --grep 'should register empty'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/decorator.test.js --grep 'should register empty' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
