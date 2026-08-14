#!/usr/bin/env bash
# Harbor verifier for clap_complete_value_index (index-aware ValueCompleter).
# Runs the gold test `suggest_custom_arg_completer_at_index` (modified by the
# verifier patch in tests/testsuite/engine.rs).
# On base, the engine always calls `complete` (no index threading), so the
# completer returns ALL candidates at every position -> the index-aware test
# assertions (remotes at slot 0, branches at slot 1) FAIL.
# After gold (engine threads arg_index into complete_at), slot 0 returns
# remotes and slot 1 returns branches -> test PASSES.
#
# Anti-hardcoding: near-miss variants re-fail.
#   A = always pass arg_index 0 -> slot 1 still gets remotes -> FAIL.
#   B = inherent complete_at returns empty -> no candidates at all -> FAIL.
#
# Runs in codegraphcl-ripgrep:rust env. test target is the `testsuite` binary.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test -p clap_complete --features unstable-dynamic --test testsuite suggest_custom_arg_completer_at_index 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
