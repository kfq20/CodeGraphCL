#!/usr/bin/env bash
# Harbor verifier for clap_default_values_if (no conditional multi-value defaults).
# Runs the gold tests matching `default_values_if_arg_present_with_value_no_default`
# (added by commit c2ced1ae). The filter is a substring match, so it selects the
# no_default / _fail / _user_override variants of that test.
#
# On base the test source calls a builder method that does not exist yet -> the
# `builder` integration target fails to COMPILE -> cargo exits non-zero -> FAILS.
# After gold (conditional multi-value defaults supported end-to-end) it compiles and PASSES.
#
# Anti-hardcoding: near-miss variants (only the first conditional default applied /
# conditional-default storage widened without updating the single-value entry point) re-fail.
#
# Runs in cgcl-rg-box (Rust env). test target is the `builder` integration binary.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test builder default_values_if_arg_present_with_value_no_default 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
