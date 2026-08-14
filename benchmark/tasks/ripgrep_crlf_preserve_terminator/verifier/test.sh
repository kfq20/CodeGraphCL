#!/usr/bin/env bash
# Harbor verifier for ripgrep_crlf_preserve_terminator (line terminator lost on replace with CRLF).
# Runs the gold test `regression_crlf_preserve` (added by commit 64174b8). On base, the printer's
# replace path trims the line terminator before running the regex but never re-appends it -> the
# printed output is "hello\nworld" (no trailing \r\n) -> the assert_eq_printed! assertion FAILS.
# After gold (trim_line_terminator returns the removed slice; the Replacer re-appends it after the
# replacement), the output is "hello\nworld\r\n" -> PASSES.
#
# Anti-hardcoding: near-miss variants (append wrong terminator / append unconditionally) re-fail.
#
# Runs in cgcl-rg-box (Rust env). test target is the `grep-printer` crate lib (the test is inline
# in standard.rs).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test -p grep-printer regression_crlf_preserve 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
