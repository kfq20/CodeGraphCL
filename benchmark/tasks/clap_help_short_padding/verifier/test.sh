#!/usr/bin/env bash
# Harbor verifier for clap_help_short_padding (help-text padding for short-only args).
# Runs the gold test `short_with_value` (updated by commit 126440ca).
# On base the rendered help has wrong column padding (`  -z <BAZ>      Short only`) -> snapshot
# mismatch -> FAILS. After gold the padding is correct (`  -z <BAZ>  Short only`) -> PASSES.
#
# Anti-hardcoding: near-miss variants (keep old filter / wrong condition) re-fail.
#
# Runs in cgcl-rg-box (Rust env). test target is the `builder` integration binary.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test builder short_with_value 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
