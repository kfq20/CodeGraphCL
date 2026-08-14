#!/usr/bin/env bash
# Harbor verifier for viper_config_notfound_error (ReadInConfig returns ConfigFileNotFoundError).
# Runs the gold test added by commit 0afb045 — TestWrongConfigWithSetConfigFileNotFound in viper_test.go.
# On base, ReadInConfig calls afero.ReadFile on a nonexistent file and returns the afero/path error
# (NOT a ConfigFileNotFoundError), so assert.IsType(ConfigFileNotFoundError{...}, err) FAILS.
# After gold (ReadInConfig checks afero.Exists first and returns ConfigFileNotFoundError when absent),
# the error type matches -> PASSES.
#
# Anti-hardcoding: near-miss variants (return the wrong error type; or check existence but return the
# raw read error anyway) re-fail the test.
#
# Runs in cgcl-viper-box (golang:1.23). go test compiles the package; deps cached at /pool/gomod.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

export GOMODCACHE=/pool/gomod GOFLAGS=-mod=mod

OUTPUT=$(go test ./ -run '^TestWrongConfigWithSetConfigFileNotFound$' -count=1 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
