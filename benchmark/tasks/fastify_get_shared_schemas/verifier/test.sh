#!/usr/bin/env bash
# Harbor verifier for fastify_get_shared_schemas (read out all shared schemas).
# Runs the gold tests `Should expose getSchemas function` + `The schemas should be accessible
# via getSchemas` (added by commit c9141a071d0f). On base, getSchemas does not exist -> the
# typeof check fails and the deepEqual throws -> test FAILS. After gold (a shallow copy of the
# store map), both pass.
#
# Anti-hardcoding: near-miss variants (return the keys, not the map; or return a named wrapper)
# re-fail the deepEqual assertion.
#
# Runs in cgcl-fs-box (node:20). tap on test/shared-schemas.test.js --grep getSchemas.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/shared-schemas.test.js --grep "getSchemas" 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
