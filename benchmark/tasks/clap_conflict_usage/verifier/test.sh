#!/usr/bin/env bash
# Harbor verifier for clap_conflict_usage (conflict-usage string lists the triggering arg).
# Runs the gold test `groups::conflict_with_group` (modified by commit 578cd43a) in tests/builder/groups.rs.
# On base, the usage line lists both args (--a --conflict); the gold test asserts only --conflict
# -> the snapshot/assertion fails on base. After gold (dedup conflict set before usage build), the
# usage line is --conflict only -> PASSES.
#
# Runs in cgcl-rg-box (Rust). cargo test --test builder conflict_with_group.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test builder conflict_with_group 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
