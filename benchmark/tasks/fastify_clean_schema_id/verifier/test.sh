#!/usr/bin/env bash
# Harbor verifier for fastify_clean_schema_id (strip $id from shared schemas at compile time).
# Runs the gold test `The schema resolver should clean the $id key before passing it to the
# compiler` (added by commit 5ffb131e40b9). On base, the shared schema's $id leaks into the
# compiled route schema -> test FAILS. After gold (cleanId recursively strips $id from the
# schema copy used for compilation) -> test PASSES.
#
# Anti-hardcoding: near-miss variants (top-level-only strip / strip the wrong key) re-fail.
#
# Runs in cgcl-fs-box (node:20). tap on test/shared-schemas.test.js --grep 'clean the .id'.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
if [ ! -d node_modules ]; then
  npm install --no-audit --no-fund > "$logs_dir/verifier/npm_install.log" 2>&1
fi
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(./node_modules/.bin/tap test/shared-schemas.test.js --grep 'clean the .id' 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
