#!/usr/bin/env bash
# Harbor verifier for ripgrep_look_around_panic (panic in replacements on look-around).
# Runs the gold test `r3180_look_around_panic` (added by commit de2567a). On base, multiline +
# replace on the look-around pattern panics (slice index out of bounds: end < last_match) -> the
# rgtest FAILS (the test process panics, cargo reports test FAILED). After gold (clamp end to
# bytes.len() when last_match > range.end), the search completes and prints "xbxbx\n" -> PASSES.
#
# Runs in cgcl-rg-box (Rust env). test target is the top-level `integration` test target
# (tests/tests.rs includes regression.rs as a mod).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test integration r3180_look_around_panic 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
