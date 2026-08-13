#!/usr/bin/env bash
# Harbor verifier for clap_derive_type_alias (user type aliases break derive codegen).
# Runs the gold derive test `type_alias_regressions` (added by commit 1285c0f8). On base the
# derive-generated code refers to unqualified Result/Option, which the test's aliases shadow,
# so the derive test binary fails to COMPILE (cargo rc != 0). After the gold source fix the
# generated code uses fully-qualified stdlib paths and the test compiles + passes.
#
# Anti-hardcoding: near-miss variants re-introduce an unqualified reference (or qualify only
# one of the two call sites) so the test binary again fails to compile.
#
# Runs in the cgcl-rg-box container (Rust env). clap 3.0.0-rc.4 workspace; derive feature.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test --test derive --features derive type_alias_regressions 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
