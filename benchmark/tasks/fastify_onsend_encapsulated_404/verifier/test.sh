#!/usr/bin/env bash
# Harbor verifier for fastify_onsend_encapsulated_404.
# Runs the gold test added by commit cc2f9c9c in test/404s.test.js — 'onSend hooks run when an
# encapsulated route invokes the notFound handler'. A plugin registers an onSend hook and a route
# that sends a NotFound error. On base, the route context stores the SHARED root 404 context, whose
# onSend is the root instance's (empty) hook list — the plugin's onSend hook never runs, so the
# test's t.plan(3) sees only 2 assertions and FAILS. After gold (per-route copy of the 404 context
# carrying the encapsulated onSend hooks), the hook runs — 3 assertions — PASSES.
#
# Anti-hardcoding: near-miss variants (copy the context but never assign the hooks / assign the
# hooks to the wrong hook slot) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/404s.test.js --grep 'onSend hooks run when an encapsulated'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/404s.test.js --grep 'onSend hooks run when an encapsulated' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
