#!/usr/bin/env bash
# Harbor verifier for T_B (TrioBackend.start_tls) — hermetic, no upstream fixtures.
# Drives the agent's code with trio.run + a stdlib TLS server (see verify.py).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

if [ -d /wheels ] && ! python3 -c "import trustme" 2>/dev/null; then
  timeout 60 pip install --quiet --no-index --no-deps /wheels/*.whl >/dev/null 2>&1 || true
fi

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
TESTS_DIR="${HARBOR_TESTS_DIR:-/tests}"
OUTPUT=$(CGCL_WORKDIR="$PWD" python3 "$TESTS_DIR/verify.py" 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
