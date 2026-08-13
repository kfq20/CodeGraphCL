#!/usr/bin/env bash
# Harbor verifier for fastify_reply_headerssent (send stream after manual writeHead crashes).
# Runs the gold test `stream using reply.res.writeHead should return customize headers` (added
# by commit fd8fb5e55aa7). On base, send() sets headers again after writeHead -> throws -> test
# FAILS. After gold (guard the header loop with !res.headersSent, warn otherwise), the stream
# sends without re-setting headers -> test PASSES.
#
# Anti-hardcoding: near-miss variants (invert the guard / add the warn but still set headers)
# re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/internals/reply.test.js --grep 'reply.res.writeHead'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/internals/reply.test.js --grep 'reply.res.writeHead' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
