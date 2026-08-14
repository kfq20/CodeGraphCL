#!/usr/bin/env bash
# Harbor verifier for ripgrep_deadlock_visitor_panic (parallel walker hangs when visitor panics).
# Runs the gold tests `panic_in_parallel` and `panic_in_parallel_builder` (added by commit
# 0d7054d). On base, a panicking visitor leaves workers stuck in their idle receive loop; the
# #[should_panic] tests HANG (the run never returns, so the expected panic never propagates).
# After gold (collect workers before spawn + Drop::drop calls quit_now on panic + is_quit_now
# check in the idle loop), the panic propagates and the #[should_panic] tests PASS.
#
# NOTE: this test is marked #[should_panic], so a passing run exits 0 (the panic is expected and
# caught by the test harness). A base run hangs -> `timeout 30` kills cargo after 30s -> rc=124
# = FAIL. After gold, the test completes quickly with rc=0.
#
# Anti-hardcoding: near-miss A (swallow the join panic so #[should_panic] fails) and near-miss B
# (revert collect-before-spawn so the builder-panic test hangs) both re-fail quickly.
#
# Runs in cgcl-rg-box (Rust env). test target is the `ignore` crate lib (the test is inline in walk.rs).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(timeout 30 cargo test -p ignore panic_in_parallel 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
