#!/usr/bin/env bash
# Harbor verifier for ripgrep_skip_unreachable_ignore (unreachable ignore file loaded at depth boundary).
# Runs the gold test `walk::tests::max_depth_does_not_load_unreachable_ignore_files` (added by commit
# 435f59f). On base, the walker calls add_child at the depth boundary, which opens+parses the
# malformed .ignore in the unvisited leaf dir -> the entry carries a parse error -> the
# `entry.error().is_none()` assertion FAILS. After gold (add_child_with_entries(path, &[]) at the
# boundary -> empty matcher, no file loaded -> no error), the test PASSES.
#
# Anti-hardcoding: near-miss variants (load the file but pass entries / only fix one call site)
# re-fail the assertion.
#
# Runs in cgcl-rg-box (Rust env). test target is the `ignore` crate lib (the test is inline in walk.rs).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test -p ignore max_depth_does_not_load_unreachable 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
