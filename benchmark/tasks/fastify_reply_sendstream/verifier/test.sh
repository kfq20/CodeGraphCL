#!/usr/bin/env bash
# Harbor verifier for fastify_reply_sendstream (support send: stream errors before headers).
# Runs the gold test `should support send module 200 and 404` (added by commit ed424325). On
# base, the pump-based pipe resets the connection (ECONNRESET) when the send-module stream
# errors on a non-existing file, so the client gets no 404 status -> test FAILS. After gold
# (sendStream: end-of-stream guard delegates pre-headers-sent errors to handleError), a 404-
# bearing stream yields a 404 response -> test PASSES.
#
# Anti-hardcoding: near-miss variants (no pre-headers-sent error guard / don't destroy source
# on response error) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/stream.test.js --grep 'return a 404 if the stream emits a 404 error'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/stream.test.js --grep 'return a 404 if the stream emits a 404 error' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
