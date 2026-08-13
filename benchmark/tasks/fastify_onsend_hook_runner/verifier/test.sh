#!/usr/bin/env bash
# Harbor verifier for fastify_onsend_hook_runner (hook resolving to a value breaks the request).
# Runs the gold test `onRequest, preHandler, and onResponse hooks that resolve to a value do not
# cause an error` (added by commit 86519c8b). On base, the generic hookRunner threads the resolved
# value into state -> a hook resolving to 1/true/null/'a'/{} overwrites state -> errors -> FAILS.
# After gold (generic runner ignores resolved values; onSend gets its own payload-threading runner)
# -> the hooks resolve to values without error -> test PASSES.
#
# Anti-hardcoding: near-miss variants (thread value into state / error on any promise) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/hooks.test.js --grep 'resolve to a value do not cause'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/hooks.test.js --grep 'resolve to a value do not cause' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
