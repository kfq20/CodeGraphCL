#!/usr/bin/env bash
# Harbor verifier for viper_unmarshal_exact_merge (UnmarshalExact merges missing struct keys).
# Runs the gold test added by commit fb6eb1e — TestUnmarshalWithAutomaticEnv/Exact in viper_test.go.
# On base, UnmarshalExact decodes from AllSettings() which does not consult env vars, so env-backed
# struct fields (Name, Duration, Modes, Secret, Size) come back zero while only the explicitly
# Set "port" populates -> the deep-equal assertion FAILS.
# After gold (UnmarshalExact derives struct keys and decodes via getSettings so env vars are
# consulted), all fields populate -> PASSES.
#
# Anti-hardcoding: near-miss variants (derive struct keys but keep AllSettings source; or
# getSettings source but drop struct keys) re-fail the test.
#
# Runs in cgcl-viper-box (golang:1.23). go test compiles the package; deps cached at /pool/gomod.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

export GOMODCACHE=/pool/gomod GOFLAGS=-mod=mod

OUTPUT=$(go test ./ -run '^TestUnmarshalWithAutomaticEnv$/^Exact$' -count=1 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
