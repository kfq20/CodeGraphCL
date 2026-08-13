#!/usr/bin/env bash
# Harbor verifier for ripgrep c5 (parent ignore rules applied to wrong dir across multi-root).
# Runs the gold rgtest block `ignore_git_multi_root_order` (added in commit 653d7f5, exercising
# the fix in 43e2f08). On base (43e2f08^) the cached parent matcher carries the first root's
# base into the second root -> src/invalid leaks into results -> test FAILS. After the gold
# source fix each root keeps its own base -> test PASSES.
#
# Anti-hardcoding: near-miss variants (parent() wrong source + cache-hit wrong source) both
# re-leak the wrong root's context -> test re-fails.
#
# Runs in cgcl-rg-box (Rust env). test target `integration` (tests/tests.rs incl mod misc).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test integration ignore_git_multi_root_order 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
