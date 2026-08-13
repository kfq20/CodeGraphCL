#!/usr/bin/env bash
# Harbor verifier for clap_derive_default_value_os (default_value_os treated as required).
# Runs the gold derive test `detect_os_variant` (added by commit 7c10b5a9b4). On base it panics
# (debug_assert fails because the OS-string-defaulted arg is still required); after the gold
# source fix it passes. Anti-hardcoding: near-miss variants (value-only override / wrong field)
# make the test re-fail.
#
# Runs in the cgcl-rg-box container (Rust env). clap 3.0.0-rc.4 workspace: clap_derive is a
# path dep enabled by the `derive` feature. test target is the `derive` integration binary.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
# run just the detect_os_variant test the gold commit added
OUTPUT=$(cargo test --test derive --features derive detect_os_variant 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
