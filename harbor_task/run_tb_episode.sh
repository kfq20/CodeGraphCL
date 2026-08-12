#!/usr/bin/env bash
# T_B episode runner — long-lived container `cgcl-mat-box` + host claude.
# T_B has a real edge (T_A->T_B parity). Verifier is the hermetic verify.py (no gold-test
# injection needed; verify.py stands up its own stdlib TLS server + trio.run).
#
# Usage:
#   run_tb_episode.sh oracle  <epname>
#   run_tb_episode.sh agent   <epname> <condition>   # reset|correct|irrelevant|wrong
set -uo pipefail
MODE="${1:?mode}"; EPNAME="${2:?epname}"; CONDITION="${3:-reset}"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
STEP="$ROOT/harbor_task/steps/tB_start_tls_trio"
BOX="cgcl-mat-box"
POOL_HOST="/tmp/cgcl_box_pool"
EP="$POOL_HOST/$EPNAME"
BASE_SHA="38a136833f7c7f3a17f362b1223ef7cc7e38253d^"   # T_B parent = e5d0ad2
SRC="$ROOT/repos/httpx-full"

rm -rf "$EP"; mkdir -p "$EP/work" "$EP/out" "$EP/logs" "$EP/tests"
echo "base=$(git -C "$SRC" rev-parse --short "$BASE_SHA")" > "$EP/base.txt"

# stage test.sh + verify.py + gold patch into the shared pool
cp "$STEP/tests/test.sh"        "$EP/tests/test.sh"
cp "$STEP/tests/verify.py"      "$EP/tests/verify.py"
cp "$STEP/solution/gold_source.patch" "$EP/gold_source.patch"
chmod +x "$EP/tests/test.sh"

# workrun: cwd = /pool/<name>/work, single-quoted body (host shell must not touch /pool)
workrun() {
  docker exec "$BOX" bash -c 'cd /pool/'"$EPNAME"'/work && '"$1" 2>/dev/null
}

# ---- phase 1: base snapshot
cp -a "$SRC/." "$EP/work/" 2>/dev/null
workrun "git checkout -q -f $BASE_SHA; git clean -fdxq -- tests/ 2>/dev/null; echo PREP_OK > /pool/$EPNAME/out/prep.log 2>&1"

# ---- phase 2: solver
if [ "$MODE" = "oracle" ]; then
  workrun "git apply /pool/$EPNAME/gold_source.patch && echo GOLD_APPLIED > /pool/$EPNAME/out/solve.log 2>&1 || echo APPLY_FAIL > /pool/$EPNAME/out/solve.log 2>&1"
else
  bash "$ROOT/harbor_task/run_tb_agent.sh" "$EP" "$CONDITION"
fi

# ---- phase 3: NO verifier injection (T_B uses fixed hermetic verify.py, already staged)

# ---- phase 4: score — hermetic verify.py stands up its own TLS server
workrun "HARBOR_WORKDIR=/pool/$EPNAME/work HARBOR_TESTS_DIR=/pool/$EPNAME/tests HARBOR_LOGS_DIR=/pool/$EPNAME/logs bash /pool/$EPNAME/tests/test.sh > /pool/$EPNAME/out/verify.log 2>&1"

sleep 2
REWARD=$(cat "$EP/logs/verifier/reward.txt" 2>/dev/null || echo "ERR")
echo "reward=$REWARD" | tee "$EP/reward.txt"
