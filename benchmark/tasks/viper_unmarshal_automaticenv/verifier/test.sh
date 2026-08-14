#!/usr/bin/env bash
# Harbor verifier for viper_unmarshal_automaticenv (Unmarshal reads env vars via struct-key path).
# Runs the gold test added by commit 73dfb94 — TestUnmarshalWithAutomaticEnv in viper_test.go.
# On base, Unmarshal only consults AllSettings() which does NOT surface env vars mapped to struct
# fields, so the OK subtest gets zero values -> test FAILS.
# After gold (Unmarshal derives struct keys and reads via getSettings so AutomaticEnv is honored),
# the env-backed fields populate -> PASSES.
#
# Anti-hardcoding: near-miss variants (derive struct keys but don't feed them to getSettings; or
# read the wrong settings source) re-fail the test.
#
# Runs in cgcl-viper-box (golang:1.23). go test compiles the package; deps cached at /pool/gomod.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

export GOMODCACHE=/pool/gomod GOFLAGS=-mod=mod

OUTPUT=$(go test ./ -run '^TestUnmarshalWithAutomaticEnv$' -count=1 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
