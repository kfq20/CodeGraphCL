#!/usr/bin/env bash
# Harbor verifier for clap_error_help_newline (help/subcommand error has no trailing newline).
# Runs the gold test `help::disabled_help_flag_and_subcommand` (extended by commit 2eb69def4ecb).
# On base the error string doesn't end with a newline -> test panics -> FAILS. After gold
# (add the else { c.none("\n") } branch), the string ends with \n -> test PASSES.
#
# Anti-hardcoding: near-miss variants (skip the else branch / newline in the wrong branch) re-fail.
#
# Runs in cgcl-rg-box (Rust env). test target is the `builder` integration binary.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test builder disabled_help_flag_and_subcommand 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
