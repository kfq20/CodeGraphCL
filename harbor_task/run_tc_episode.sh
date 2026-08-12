#!/usr/bin/env bash
# T_C episode runner — long-lived container `cgcl-mat-box` + host claude.
# T_C = 644e8fc5b6 (start_tls moved onto stream; returns new stream). Contract revision.
# Verifier is the hermetic verify.py (calls stream.start_tls, checks new-stream return).
# Usage:
#   run_tc_episode.sh oracle  <epname>
#   run_tc_episode.sh agent   <epname> <condition>
set -uo pipefail
MODE="${1:?mode}"; EPNAME="${2:?epname}"; CONDITION="${3:-reset}"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
STEP="$ROOT/harbor_task/steps/tC_start_tls_stream"
BOX="cgcl-mat-box"
POOL_HOST="/tmp/cgcl_box_pool"
EP="$POOL_HOST/$EPNAME"
BASE_SHA="644e8fc5b6c5678fc1c1916293c1afab56d60bad^"
SRC="$ROOT/repos/httpx-full"

rm -rf "$EP"; mkdir -p "$EP/work" "$EP/out" "$EP/logs" "$EP/tests"
echo "base=$(git -C "$SRC" rev-parse --short "$BASE_SHA")" > "$EP/base.txt"

cp "$STEP/tests/test.sh"   "$EP/tests/test.sh"
cp "$STEP/tests/verify.py" "$EP/tests/verify.py"
cp "$STEP/solution/gold_source.patch" "$EP/gold_source.patch"
chmod +x "$EP/tests/test.sh"

workrun() { docker exec "$BOX" bash -c 'cd /pool/'"$EPNAME"'/work && '"$1" 2>/dev/null; }

# phase 1: base snapshot
cp -a "$SRC/." "$EP/work/" 2>/dev/null
sync; sleep 2
workrun "git checkout -q -f $BASE_SHA; git clean -fdxq -- tests/ 2>/dev/null; echo PREP_OK > /pool/$EPNAME/out/prep.log 2>&1"
sleep 2

# phase 2: solver
if [ "$MODE" = "oracle" ]; then
  workrun "git apply /pool/$EPNAME/gold_source.patch && echo GOLD_APPLIED > /pool/$EPNAME/out/solve.log 2>&1 || echo APPLY_FAIL > /pool/$EPNAME/out/solve.log 2>&1"
  sleep 2
else
  bash "$ROOT/harbor_task/run_tc_agent.sh" "$EP" "$CONDITION"
fi

# phase 3: NO gold-test injection (T_C uses hermetic verify.py, already staged)

# phase 4: score
workrun "HARBOR_WORKDIR=/pool/$EPNAME/work HARBOR_TESTS_DIR=/pool/$EPNAME/tests HARBOR_LOGS_DIR=/pool/$EPNAME/logs bash /pool/$EPNAME/tests/test.sh > /pool/$EPNAME/out/verify.log 2>&1"
sleep 2
REWARD=$(cat "$EP/logs/verifier/reward.txt" 2>/dev/null || echo "ERR")
echo "reward=$REWARD" | tee "$EP/reward.txt"
