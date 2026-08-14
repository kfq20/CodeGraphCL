#!/usr/bin/env bash
# Harbor verifier for ripgrep_min_depth_option (min_depth filter on the walker).
# Runs the gold test `min_depth` (added by commit 2924d0c). On base, there is no min_depth option
# at all -> the test fails to compile (no method `min_depth`) -> cargo test FAILS. After gold (the
# min_depth field + setter + depth gate in the Worker + WalkParallel plumbing), the test compiles
# and passes.
#
# Anti-hardcoding: near-miss variants (filter on the wrong depth comparison / skip descending)
# re-fail the assertion.
#
# Runs in cgcl-rg-box (Rust env). test target is the `ignore` crate lib (the test is inline in walk.rs).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test -p ignore min_depth 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
