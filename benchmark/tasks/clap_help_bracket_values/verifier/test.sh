#!/usr/bin/env bash
# Harbor verifier for clap_help_bracket_values (value names past minimum rendered as required).
# Runs the gold test `partially_optional_value_names` (modified by commit 1ca55413) in
# tests/builder/help.rs. On base, the help renders `--example <FOO> <BAR>` but the gold test
# expects `--example <FOO> [BAR]` -> snapshot mismatch -> FAILS. After gold (bracket values
# past the minimum), the help renders `--example <FOO> [BAR]` -> match -> PASSES.
#
# Anti-hardcoding: near-miss variants (bracket the FIRST value instead / bracket all values)
# re-fail the snapshot.
#
# Runs in cgcl-rg-box (Rust env). test target is the `builder` integration binary.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test builder partially_optional_value_names 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
