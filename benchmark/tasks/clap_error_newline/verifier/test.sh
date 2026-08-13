#!/usr/bin/env bash
# Harbor verifier for clap_error_newline (argument-not-found error has no trailing newline).
# Runs the gold test `error::argument_not_found_auto_has_newline` (added by commit a72e5726f872).
# On base the error string doesn't end with a newline -> test panics (assertion) -> FAILS.
# After gold (append \n to the message), the string ends with \n -> test PASSES.
#
# Anti-hardcoding: near-miss variants (no newline / newline at the wrong end) re-fail.
#
# Runs in cgcl-rg-box (Rust env). test target is the `builder` integration binary.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test builder argument_not_found_auto_has_newline 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
