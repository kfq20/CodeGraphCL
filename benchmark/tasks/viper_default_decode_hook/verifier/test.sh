#!/usr/bin/env bash
# Harbor verifier for viper_default_decode_hook (WithDecodeHook sets a default decode hook).
# Runs the gold test added by commit d2458a2 — TestUnmarshalWithDefaultDecodeHook in viper_test.go.
# On base, there is no WithDecodeHook option, so a Viper constructed with a custom decode hook
# cannot apply it; the StringToSliceHookFunc (custom hook) is not registered, so a JSON string
# value is not decoded into a map[string]string -> test FAILS (compile error: WithDecodeHook undefined).
# After gold (decodeHook field + WithDecodeHook option + defaultDecoderConfig uses v.decodeHook),
# the custom hook runs -> PASSES.
#
# Anti-hardcoding: near-miss variants (add the option but don't wire it into defaultDecoderConfig;
# or wire the wrong field) re-fail the test.
#
# Runs in cgcl-viper-box (golang:1.23). go test compiles the package; deps cached at /pool/gomod.
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

export GOMODCACHE=/pool/gomod GOFLAGS=-mod=mod

OUTPUT=$(go test ./ -run '^TestUnmarshalWithDefaultDecodeHook$' -count=1 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
