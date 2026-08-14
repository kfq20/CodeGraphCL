#!/usr/bin/env bash
# Harbor verifier for ripgrep_gitignore_skip_bom (BOM at start of gitignore breaks first rule).
# Runs the gold test `gitignore_skip_bom` (added by commit 4836284). On base, the BOM prefix
# attaches to the first-line pattern -> it doesn't match -> matched().is_ignore() is false ->
# assertion FAILS. After gold (strip UTF8_BOM on i==0 only), the first-line pattern matches -> PASSES.
#
# Runs in cgcl-rg-box (Rust). cargo test -p ignore --test gitignore_skip_bom.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test -p ignore --test gitignore_skip_bom 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
