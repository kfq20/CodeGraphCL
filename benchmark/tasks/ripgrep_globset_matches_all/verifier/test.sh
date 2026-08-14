#!/usr/bin/env bash
# Harbor verifier for ripgrep_globset_matches_all (matches_all false positives).
# Runs the gold tests `matches_all_*` (added by commit f55548b). On base, matches_all_candidate
# calls strat.is_match (any-glob-in-bucket), so a 2-literal set {abc,def} reports matches_all
# ("abc") = true -> the assertion !matches_all("abc") FAILS. After gold (per-strategy matches_all
# requiring all globs in the bucket to match), the assertion PASSES.
#
# Runs in cgcl-rg-box (Rust env). test target is the `globset` crate lib (inline tests in lib.rs).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test -p globset matches_all 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
