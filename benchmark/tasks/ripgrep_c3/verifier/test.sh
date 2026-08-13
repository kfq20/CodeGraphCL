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
# c3 reward (BINARY 0/1 — intervene treats any non-0/1 reward as infra_fail, so never write a
# count). reward=1 iff all 6 c3-block tests pass (4 FAIL_TO_PASS + 2 PASS_TO_PASS), i.e. RC==0.
# (Previously this wrote a partial-credit count via `printf "$PASS"`, which (a) wrote an empty
# file when PASS was empty -> reward="ERR" -> infra_fail, and (b) wrote counts >1 -> infra_fail.
# The count is still recorded in test-stdout.txt for offline partial-credit analysis.)
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
