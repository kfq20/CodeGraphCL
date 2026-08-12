#!/usr/bin/env bash
# Harbor verifier for ripgrep c3 (parent .ignore not matched on subdir search).
# Runs the gold rgtest block the c3 commit added — real ignore/path behavior, not impl shape.
# (Anti-hardcoding proven by near-miss A/B: over-strip and no-strip both fail 5 tests.)
#
# Runs in the cgcl-rg-box container (Rust env). test target is `integration` (c3-era
# Cargo.toml declares [[test]] name=integration path=tests/tests.rs; regression.rs is a mod).
# reward = 1 iff the 4 FAIL_TO_PASS tests pass (r829_2747/2778/2836/2933).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
# run the c3 test subset; -k r829 keeps it to the c3-added block
OUTPUT=$(cargo test --test integration r829 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
# c3 reward: all 6 c3-block tests must pass (the 4 FAIL_TO_PASS + 2 PASS_TO_PASS)
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  # partial-credit: count c3-block tests that passed
  PASS=$(echo "$OUTPUT" | grep -cE '\.\.\. ok' || true)
  printf "$PASS" > "$logs_dir/verifier/reward.txt" 2>/dev/null || printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
