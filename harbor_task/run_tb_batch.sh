#!/usr/bin/env bash
# Block-randomized batch runner for T_B intervention. N episodes per condition (default 3),
# order shuffled within each block (one block = one full pass of all 4 conditions) to avoid
# load/order confound. Writes one CSV row per episode to <batchdir>/results.csv.
#
# Usage: run_tb_batch.sh <batchdir> [N]
# Reads env: BATCH_SEED for reproducible ordering (default 42).
set -uo pipefail
BATCHDIR="${1:?batchdir}"; N="${2:-3}"; SEED="${BATCH_SEED:-42}"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CL-research"   # fix below
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
POOL="/tmp/cgcl_box_pool"
mkdir -p "$BATCHDIR"
RESULTS="$BATCHDIR/results.csv"
[ -f "$RESULTS" ] || echo "condition,rep,block,reward,elapsed_sec,input_tokens,output_tokens,tool_uses,assistant_turns,prompt_sha256,prefix_chars,episode" > "$RESULTS"

echo "=== block-randomized plan (seed=$SEED, N=$N per condition) ==="
python3 - "$N" "$SEED" > "$BATCHDIR/plan.tsv" <<'PY'
import random, sys
N=int(sys.argv[1]); seed=int(sys.argv[2]); random.seed(seed)
conds=["reset","correct","irrelevant","wrong"]
i=0
for b in range(N):
    order=conds[:]; random.shuffle(order)
    for c in order:
        print(f"{i}\t{c}\t{b}"); i+=1
PY
cat "$BATCHDIR/plan.tsv"

echo ""
echo "=== running episodes ==="
while IFS=$'\t' read -r idx cond block; do
  EPNAME="batch_${block}_${cond}_${idx}"
  echo "--- ep $idx: cond=$cond block=$block ($EPNAME) ---"
  rm -rf "$POOL/$EPNAME"
  timeout 700 bash "$ROOT/harbor_task/run_tb_episode.sh" agent "$EPNAME" "$cond" >/dev/null 2>&1
  EP="$POOL/$EPNAME"
  # pull metrics from manifest + agent_meta
  reward=$(cat "$EP/logs/verifier/reward.txt" 2>/dev/null || echo ERR)
  meta="$EP/out/agent_meta.txt"
  elapsed=$(grep -oP 'elapsed_sec=\K[0-9]+' "$meta" 2>/dev/null || echo NA)
  intok=$(grep -oP 'input_tokens=\K[0-9]+' "$meta" 2>/dev/null || echo NA)
  outtok=$(grep -oP 'output_tokens=\K[0-9]+' "$meta" 2>/dev/null || echo NA)
  tools=$(grep -oP 'tool_uses=\K[0-9]+' "$meta" 2>/dev/null || echo NA)
  turns=$(grep -oP 'assistant_turns=\K[0-9]+' "$meta" 2>/dev/null || echo NA)
  psha=$(python3 -c "import json;print(json.load(open('$EP/out/manifest.json'))['prompt_sha256'][:12])" 2>/dev/null || echo NA)
  pchars=$(python3 -c "import json;print(json.load(open('$EP/out/manifest.json'))['prefix_chars'])" 2>/dev/null || echo NA)
  echo "$cond,$block,$block,$reward,$elapsed,$intok,$outtok,$tools,$turns,$psha,$pchars,$EPNAME" >> "$RESULTS"
  echo "  -> reward=$reward elapsed=$elapsed in_tok=$intok tools=$turns"
done < "$BATCHDIR/plan.tsv"

echo ""
echo "=== results ==="
cat "$RESULTS"
echo ""
echo "=== per-condition summary ==="
python3 - "$RESULTS" <<'PY'
import csv,sys
rows=list(csv.DictReader(open(sys.argv[1])))
from collections import defaultdict
agg=defaultdict(lambda:{"reward":[],"elapsed":[],"intok":[],"tools":[]})
for r in rows:
    c=r["condition"]
    try:
        agg[c]["reward"].append(float(r["reward"]))
        agg[c]["elapsed"].append(float(r["elapsed_sec"]))
        agg[c]["intok"].append(float(r["input_tokens"]))
        agg[c]["tools"].append(float(r["tool_uses"]))
    except: pass
import statistics as st
print(f"{'cond':12} {'reward':>8} {'elapsed':>10} {'in_tok':>10} {'tools':>8}")
for c in ["reset","correct","irrelevant","wrong"]:
    a=agg[c]
    if not a["reward"]: print(f"{c:12} (no data)"); continue
    m=lambda x: f"{st.mean(x):.0f}±{st.stdev(x):.0f}" if len(x)>1 else f"{x[0]:.0f}"
    print(f"{c:12} {m(a['reward']):>8} {m(a['elapsed']):>10} {m(a['intok']):>10} {m(a['tools']):>8}")
PY