#!/usr/bin/env bash
# Block-randomized batch runner for T_C intervention. N episodes per condition (default 3),
# order shuffled within each block. Episodes use OPAQUE IDs (ep_NNNNNN) — the condition word
# NEVER appears in any agent-visible path (cwd, docker hint) — so the agent cannot tell which
# arm it is in. The condition<->episode mapping lives ONLY in <batchdir>/mapping.tsv
# (agent-invisible). Runs prompt-distinctness preflight before any episode.
#
# Usage: run_tc_batch.sh <batchdir> [N]   env: BATCH_SEED (default 42)
set -uo pipefail
BATCHDIR="${1:?batchdir}"; N="${2:-3}"; SEED="${BATCH_SEED:-42}"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
POOL="/tmp/cgcl_box_pool"
mkdir -p "$BATCHDIR"
RESULTS="$BATCHDIR/results.csv"
MAPPING="$BATCHDIR/mapping.tsv"   # agent-INVISIBLE: episode_id -> condition
[ -f "$RESULTS" ] || echo "episode_id,condition,rep,block,reward,outcome,elapsed_sec,input_tokens,cache_read_tokens,cache_creation_tokens,output_tokens,tool_uses,assistant_turns,prefix_chars,prefix_sha256,instruction_sha256" > "$RESULTS"

ATOMS="$ROOT/harbor_task/tC_experience_atoms.md"
INSTR="$ROOT/harbor_task/steps/tC_start_tls_stream/instruction.md"

# ---- preflight: prompt distinctness (no batch without it) ----
echo "=== preflight: prompt distinctness ==="
if ! python3 "$ROOT/harbor_task/test_prompt_distinct.py" "$ATOMS" "$INSTR"; then
  echo "PREFLIGHT FAILED — aborting batch"; exit 1
fi

# ---- plan: opaque ep ids, condition hidden in mapping.tsv only ----
python3 - "$N" "$SEED" > "$BATCHDIR/plan.tsv" <<'PY'
import random, sys
N=int(sys.argv[1]); seed=int(sys.argv[2]); random.seed(seed)
conds=["reset","correct","irrelevant","wrong"]
i=0
for b in range(N):
    order=conds[:]; random.shuffle(order)
    for c in order:
        print(f"ep_{i:06d}\t{c}\t{b}"); i+=1
PY
# plan.tsv is also agent-invisible (has condition); copy to mapping, use ep_id only in loop
cp "$BATCHDIR/plan.tsv" "$MAPPING"
echo "=== plan (opaque ids; condition hidden from agent) ==="
cut -f1 "$BATCHDIR/plan.tsv"

echo ""
echo "=== running episodes ==="
while IFS=$'\t' read -r EPID COND BLOCK; do
  echo "--- $EPID (block $BLOCK) ---"
  rm -rf "$POOL/$EPID"
  # run_tc_episode gets the OPAQUE id + condition; it must not let condition reach the agent.
  timeout 700 bash "$ROOT/harbor_task/run_tc_episode.sh" agent "$EPID" "$COND" >/dev/null 2>&1
  EP="$POOL/$EPID"
  # outcome classification (not all failures are reward=0)
  reward=$(cat "$EP/logs/verifier/reward.txt" 2>/dev/null || echo ERR)
  rc=$(grep -oP 'rc=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  # outcome: solved / agent_fail / timeout / build_fail / infra_fail
  if [ ! -f "$EP/out/manifest.json" ]; then outcome="build_fail"
  elif [ "$rc" = "124" ]; then
    if [ "$reward" = "1" ]; then outcome="timeout_solved"; else outcome="timeout"; fi
  elif [ "$reward" = "1" ]; then outcome="solved"
  elif [ "$reward" = "0" ]; then outcome="agent_fail"
  else outcome="infra_fail"; fi
  elapsed=$(grep -oP 'elapsed_sec=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  intok=$(grep -oP 'input_tokens=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  cr=$(grep -oP 'cache_read_tokens=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  cc=$(grep -oP 'cache_creation_tokens=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  outtok=$(grep -oP 'output_tokens=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  tools=$(grep -oP 'tool_uses=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  turns=$(grep -oP 'assistant_turns=\K[0-9]+' "$EP/out/agent_meta.txt" 2>/dev/null || echo NA)
  pchars=$(python3 -c "import json;print(json.load(open('$EP/out/manifest.json'))['prefix_chars'])" 2>/dev/null || echo NA)
  psha=$(python3 -c "import json;print(json.load(open('$EP/out/manifest.json'))['prefix_sha256'])" 2>/dev/null || echo NA)
  isha=$(python3 -c "import json;print(json.load(open('$EP/out/manifest.json'))['instruction_sha256'])" 2>/dev/null || echo NA)
  echo "$EPID,$COND,$BLOCK,$BLOCK,$reward,$outcome,$elapsed,$intok,$cr,$cc,$outtok,$tools,$turns,$pchars,$psha,$isha" >> "$RESULTS"
  echo "  -> $COND reward=$reward outcome=$outcome elapsed=$elapsed"
done < "$BATCHDIR/plan.tsv"

echo ""
echo "=== results ==="
column -t -s, "$RESULTS" 2>/dev/null || cat "$RESULTS"
echo ""
echo "=== per-condition summary (mean±stdev; timeout=censored) ==="
python3 - "$RESULTS" <<'PY'
import csv,sys,statistics as st
rows=list(csv.DictReader(open(sys.argv[1])))
from collections import defaultdict
agg=defaultdict(lambda:{"reward":[],"elapsed":[],"intok":[],"tools":[],"solved":0,"n":0})
for r in rows:
    c=r["condition"]; agg[c]["n"]+=1
    if r["outcome"]=="build_fail" or r["outcome"]=="infra_fail": continue  # censor infra
    try:
        agg[c]["reward"].append(float(r["reward"]))
        agg[c]["elapsed"].append(float(r["elapsed_sec"]))
        agg[c]["intok"].append(float(r["input_tokens"])) if r["input_tokens"] not in("NA","") else None
        agg[c]["tools"].append(float(r["tool_uses"])) if r["tool_uses"] not in("NA","") else None
        if r["reward"]=="1": agg[c]["solved"]+=1
    except: pass
print(f"{'cond':12} {'solve_rate':>10} {'reward':>10} {'elapsed':>12} {'in_tok':>12} {'tools':>10}")
for c in ["reset","correct","irrelevant","wrong"]:
    a=agg[c]
    if a["n"]==0: print(f"{c:12} (no data)"); continue
    m=lambda x: f"{st.mean(x):.0f}±{st.pstdev(x):.0f}" if len(x)>1 else (f"{x[0]:.0f}" if x else "NA")
    sr=f"{a['solved']}/{a['n']}"
    print(f"{c:12} {sr:>10} {m(a['reward']):>10} {m(a['elapsed']):>12} {m(a['intok']):>12} {m(a['tools']):>10}")
PY