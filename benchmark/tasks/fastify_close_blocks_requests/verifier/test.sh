#!/usr/bin/env bash
# Harbor verifier for fastify_close_blocks_requests (after close(), new requests get 503).
# Runs the gold test block in test/close.test.js added by commit cbd08afd — the "Should return
# 503 while closing - injection" subtest. On base, after close() is called, new requests still
# go through the full request lifecycle (the server hasn't fully closed yet) -> the second
# injected request gets 200, not 503 -> FAILS. After gold (set a `closing` flag in the onClose
# hook wrapped in preReady, check it at the top of routeHandler to respond 503 and destroy the
# request), the second request (sent 100ms after close, while the 150ms onClose hook is still
# running) gets a 503 -> PASSES.
#
# Anti-hardcoding: near-miss variants (set closing but don't check it / check closing but send
# 500 instead of 503) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/close.test.js --grep 'Should return 503 while closing - injection'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/close.test.js --grep 'Should return 503 while closing - injection' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
