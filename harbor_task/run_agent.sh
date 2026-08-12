#!/usr/bin/env bash
# T_A agent phase: claude on HOST (macaron endpoint), cwd = host-side EP/work.
#
# Autonomy: runs in `claude -p` (print/non-interactive) mode with approvals disabled, so a
# batch of 4 conditions x N repetitions can run unattended. This is the same pattern the
# existing CL-research harbor tasks use for CC runs. Blast radius is bounded: each episode
# operates on its own throwaway copy under /tmp/cgcl_box_pool/<ep>/work — the source repo and
# the rest of the system are untouched.
#
# Usage: run_agent.sh <ep_host_path> <condition>
set -uo pipefail
EP="$1"; CONDITION="$2"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
STEP="$ROOT/harbor_task/steps/tA_start_tls_asyncio"
WORK="$EP/work"; OUT="$EP/out"; mkdir -p "$OUT"

INSTR=$(cat "$STEP/instruction.md")
extract() { sed -n "/^## $1/,/^## /p" "$ROOT/harbor_task/experience_atoms.md" | grep -v '^## ' | sed '/^$/d;1d'; }
case "$CONDITION" in
  reset)      PREFIX="" ;;
  correct)    PREFIX="Project context (from prior work in this codebase):"$'\n'"$(extract correct)" ;;
  irrelevant) PREFIX="Project context (from prior work in this codebase):"$'\n'"$(extract irrelevant)" ;;
  wrong)      PREFIX="Project context (from prior work in this codebase):"$'\n'"$(extract wrong)" ;;
  *) echo "unknown condition $CONDITION" >&2; exit 2 ;;
esac

PROMPT="${PREFIX}

---

${INSTR}

---
You are working in the repository at your current directory. Read the relevant source, make
your edits, and confirm the behavior is implemented. Do NOT create or modify files under
tests/ — the verifier applies its own tests after you finish. To run the project's tests
(Python 3.7 + pytest 4.6 env, not on the host), use:
  docker exec cgcl-mat-box bash -c 'cd ${EP}/work && python3 -m pytest -q -p no:cacheprovider -o addopts= tests/'
When done, output a one-line summary of what you implemented."

export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://mintcn.macaron.xin}"
# --dangerously-skip-permissions is refused under root on this host. Use --allowedTools to
# grant the coding tools the agent needs (read/edit/write + bash for `docker exec ... pytest`)
# so `claude -p` runs non-interactively without the root+skip-permissions conflict.
ALLOW="--allowedTools Read,Write,Edit,Bash,Glob,Grep,LS"
START=$(date +%s)
( cd "$WORK" && timeout 600 claude -p "$PROMPT" \
    --output-format stream-json --verbose $ALLOW \
    > "$OUT/agent.jsonl" 2> "$OUT/agent.stderr" )
RC=$?
END=$(date +%s); ELAPSED=$((END-START))
echo "rc=$RC elapsed_sec=$ELAPSED condition=$CONDITION" > "$OUT/agent_meta.txt"
python3 - "$OUT/agent.jsonl" "$OUT/agent_meta.txt" <<'PY' 2>/dev/null || true
import json,sys
in_t=out_t=tools=turns=0
for l in open(sys.argv[1]).read().splitlines():
    try: ev=json.loads(l)
    except: continue
    if ev.get("type")=="assistant":
        m=ev.get("message",{}); u=m.get("usage",{})
        in_t+=u.get("input_tokens",0); out_t+=u.get("output_tokens",0)
        for c in m.get("content",[]):
            if c.get("type")=="tool_use": tools+=1
        turns+=1
with open(sys.argv[2],"a") as f:
    f.write(f"input_tokens={in_t}\noutput_tokens={out_t}\ntool_uses={tools}\nassistant_turns={turns}\n")
PY
cat "$OUT/agent_meta.txt"
