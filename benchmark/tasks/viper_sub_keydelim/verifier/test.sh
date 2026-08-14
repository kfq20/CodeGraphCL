#!/usr/bin/env bash
# Harbor verifier for viper_sub_keydelim (Sub() copies keyDelim from parent).
# Runs the gold test added by commit 864a85a — TestSubWithKeyDelimiter in viper_test.go.
# On base, v.Sub("emails") does not copy keyDelim, so subv.Get("steve@hacker.com::created")
# returns nil (the "::" delimiter is not honored in the sub-viper) -> test FAILS.
# After gold (Sub copies subv.keyDelim = v.keyDelim), the "::" delimiter is honored -> PASSES.
#
# Anti-hardcoding: near-miss variants (copy a wrong field; or copy keyDelim into the wrong var)
# re-fail the test.
#
# Runs in cgcl-viper-box (golang:1.23). go test compiles the package; deps cached at /pool/gomod.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

export GOMODCACHE=/pool/gomod GOFLAGS=-mod=mod

OUTPUT=$(go test ./ -run '^TestSubWithKeyDelimiter$' -count=1 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
