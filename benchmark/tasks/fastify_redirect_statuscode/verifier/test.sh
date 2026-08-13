#!/usr/bin/env bash
# Harbor verifier for fastify_redirect_statuscode (redirect clobbers preset status code).
# Runs the gold tests `redirect-code-before-call` + `redirect-code-before-call-overwrite` (added
# by commit 92f474ea8c98). On base, redirect() always forces 302 -> the 307-preset test fails.
# After gold (track whether code was set, reuse it when redirect has no explicit code) -> 307
# preserved; explicit-code redirect overrides -> both pass.
#
# Anti-hardcoding: near-miss variants (always use 302 / always use the preset even when an
# explicit code was given) re-fail one of the two assertions.
#
# Runs in cgcl-fs-box (node:20). tap on internals/reply.test.js --grep "within an instance".
# NOTE: the gold commit's new cases are named `redirect to `/` - 6..9` (the strings
# `redirect-code-before-call` are ROUTE paths, not test names — grepping those skipped all 26
# tests and produced a false rc=0, which the base-fail gate correctly rejected).
# "within an instance" is the parent test; its subtests include `redirect to `/` - 1..9`
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/internals/reply.test.js --grep "within an instance" 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
