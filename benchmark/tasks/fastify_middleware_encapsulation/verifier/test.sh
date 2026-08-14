#!/usr/bin/env bash
# Harbor verifier for fastify_middleware_encapsulation.
# Runs the gold test block in test/middleware.test.js added by commit ef221571 — the
# "middlewares should support non-encapsulated plugins" subtest. On base, middleware is stored
# in a single live shared _middie instance, so middleware registered AFTER a route (via a
# non-encapsulated fastify-plugin) still runs for that route — the test's second plugin's
# middleware fires t.fail -> FAILS. After gold (per-context buildMiddie snapshots the
# _middlewares array at context-creation time; _middlewares inherited via .slice()), the later
# middleware does NOT leak into the already-built route context -> PASSES.
#
# Anti-hardcoding: near-miss variants (re-add this._middie.use in use() / buildMiddie returns
# an empty Middie without registering middleware) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/middleware.test.js --grep 'non-encapsulated'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund --ignore-scripts > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/middleware.test.js --grep 'non-encapsulated' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
