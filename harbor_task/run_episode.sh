#!/usr/bin/env bash
# T_A episode runner — long-lived container `cgcl-mat-box` + host claude.
#
# /pool (host: /tmp/cgcl_box_pool) is the bidirectional shared dir. Each episode = /pool/<name>:
#   /pool/<name>/work  = repo tree (base snapshot, solver edits here)
#   /pool/<name>/tests/test.sh  = the verifier script
#   /pool/<name>/{gold_source,verifier_inject}.patch = staged patches
#   /pool/<name>/{out,logs} = output
#
# All git operations run INSIDE work/ (the repo). docker exec stdout is unreliable here, so
# every phase writes to /pool/<name>/out/*.log INSIDE the box (host reads it after ~1s sync).
#
# Usage:
#   run_episode.sh oracle  <epname>
#   run_episode.sh agent   <epname> <condition>   # reset|correct|irrelevant|wrong
set -uo pipefail
MODE="${1:?mode}"; EPNAME="${2:?epname}"; CONDITION="${3:-reset}"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
STEP="$ROOT/harbor_task/steps/tA_start_tls_asyncio"
BOX="cgcl-mat-box"
POOL_HOST="/tmp/cgcl_box_pool"
EP="$POOL_HOST/$EPNAME"
BASE_SHA="1872ae873bcf3dd168089902c6809e433e4bd89d^"
SRC="$ROOT/repos/httpx-full"

rm -rf "$EP"; mkdir -p "$EP/work" "$EP/out" "$EP/logs" "$EP/tests"
echo "base=$(git -C "$SRC" rev-parse --short "$BASE_SHA")" > "$EP/base.txt"

# stage patches + test.sh into the shared pool (box has no /harbor mount)
cp "$STEP/solution/gold_source.patch"      "$EP/gold_source.patch"
cp "$STEP/solution/verifier_inject.patch"  "$EP/verifier_inject.patch"
cp "$STEP/tests/test.sh"                   "$EP/tests/test.sh"
chmod +x "$EP/tests/test.sh"

# run a bash snippet inside the box, cwd = /pool/<name>/work. single-quoted body avoids
# host shell pre-redirecting /pool paths (host has no /pool).
workrun() {
  docker exec "$BOX" bash -c 'cd /pool/'"$EPNAME"'/work && '"$1" 2>/dev/null
}

# ---- phase 1: copy base tree (host) + checkout to base (box, inside work)
cp -a "$SRC/." "$EP/work/" 2>/dev/null
workrun "git checkout -q -f $BASE_SHA; git clean -fdxq -- tests/ 2>/dev/null; echo PREP_OK > /pool/$EPNAME/out/prep.log 2>&1"

# ---- phase 2: solver
if [ "$MODE" = "oracle" ]; then
  workrun "git apply /pool/$EPNAME/gold_source.patch && echo GOLD_APPLIED > /pool/$EPNAME/out/solve.log 2>&1 || echo APPLY_FAIL > /pool/$EPNAME/out/solve.log 2>&1"
else
  bash "$ROOT/harbor_task/run_agent.sh" "$EP" "$CONDITION"
fi

# ---- phase 3: inject verifier (tests) AFTER solver
workrun "git apply /pool/$EPNAME/verifier_inject.patch && echo VERIFIER_INJECTED > /pool/$EPNAME/out/inject.log 2>&1 || echo INJECT_FAIL > /pool/$EPNAME/out/inject.log 2>&1"

# ---- phase 4: score — test.sh runs in work/, writes reward to logs/verifier/
workrun "HARBOR_WORKDIR=/pool/$EPNAME/work HARBOR_TESTS_DIR=/pool/$EPNAME/tests HARBOR_LOGS_DIR=/pool/$EPNAME/logs bash /pool/$EPNAME/tests/test.sh > /pool/$EPNAME/out/verify.log 2>&1"

sleep 2
REWARD=$(cat "$EP/logs/verifier/reward.txt" 2>/dev/null || echo "ERR")
echo "reward=$REWARD" | tee "$EP/reward.txt"
