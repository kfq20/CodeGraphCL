#!/usr/bin/env bash
# Harbor verifier for fastify_error_headers_404.
# Runs the gold test block in test/404s.test.js added by commit 3c920f94 — two header-related
# subtests: 'error object with headers property' (inside 'customized 404') and
# 'custom header in notFound handler' (standalone). On base, error.headers are set AFTER the
# status-code routing (which calls notFound and returns for 404), so the not-found handler's
# response is sent without the error's custom headers -> 'error object with headers property'
# FAILS (x-foo header missing). After gold (move reply.headers before status checks), the
# headers are set before notFound sends -> PASSES.
#
# Anti-hardcoding: near-miss variants (don't move the headers call / move to wrong branch)
# re-fail the 'error object with headers property' test.
#
# Runs in cgcl-fs-box (node:20). tap on test/404s.test.js --grep 'custom'.
# This matches 'customized 404' (which contains the 'error object with headers property'
# subtest that fails on base) and 'custom header in notFound handler' (standalone, passes
# on base+gold).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/404s.test.js --grep 'custom' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
