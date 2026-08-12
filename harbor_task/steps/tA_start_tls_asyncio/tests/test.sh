#!/usr/bin/env bash
# Harbor verifier for T_A (start_tls on AsyncioBackend).
#
# The verifier IS the gold commit's own regression test
# (tests/test_concurrency.py::test_start_tls_on_socket_stream), which was proven
# behavioral by the near-miss gate: a stub `start_tls` that returns the plain stream
# without upgrading FAILS it (caught at the `cipher is None` assertion). So we do NOT
# hand-roll assertions — we run the real test the project itself wrote.
#
# Host-specific plumbing (fuse-overlayfs / containerized-docker host):
#   1. offline wheels at /wheels (container pip has no reliable network here)
#   2. `-o addopts=` overrides setup.cfg's --cov (pytest-cov not installed)
#   3. all output redirected to a file (docker stdout is dropped on this host)
set -uo pipefail
# Default to cwd (caller already `cd`s into the work tree). Env vars override for harbor.
workspace="${HARBOR_WORKDIR:-$PWD}"
tests_dir="${HARBOR_TESTS_DIR:-/tests}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

# 1. offline deps needed by tests/conftest.py (trustme + uvicorn + transitive).
#    Box has these pre-installed; only install if trustme missing (avoids a slow/hanging
#    pip on every episode).
if [ -d /wheels ] && ! python3 -c "import trustme" 2>/dev/null; then
  timeout 60 pip install --quiet --no-index --no-deps /wheels/*.whl >/dev/null 2>&1 || true
fi

# 2. install the agent's httpx in-place so `import httpx` resolves to edited source
cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }

# 3. run the project's own behavioral test for this task
SELECTOR="tests/test_concurrency.py::test_start_tls_on_socket_stream"
OUTPUT=$(python3 -m pytest -q -p no:cacheprovider -o addopts= "$SELECTOR" 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"

# 4. reward: this task has a single behavioral outcome -> binary.
#    (partial-credit would need multiple independent assertions; the gold test is one
#     coherent scenario, so 0/1 is the honest encoding.)
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
