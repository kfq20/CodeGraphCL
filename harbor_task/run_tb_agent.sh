#!/usr/bin/env bash
# T_B agent phase: claude on HOST, cwd = EP/work. Runs with --allowedTools (root can't use
# --dangerously-skip-permissions on this host).
set -uo pipefail
EP="$1"; CONDITION="$2"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
STEP="$ROOT/harbor_task/steps/tB_start_tls_trio"
WORK="$EP/work"; OUT="$EP/out"; mkdir -p "$OUT"

INSTR=$(cat "$STEP/instruction.md")
extract() { sed -n "/^## $1/,/^## /p" "$ROOT/harbor_task/tB_experience_atoms.md" | grep -v '^## ' | sed '/^$/d;1d'; }
case "$CONDITION" in
  reset)      PREFIX="" ;;
  correct)    PREFIX=$(extract correct) ;;
  irrelevant) PREFIX=$(extract irrelevant) ;;
  wrong)      PREFIX=$(extract wrong) ;;
  *) echo "unknown condition $CONDITION" >&2; exit 2 ;;
esac

PROMPT="${PREFIX}

---

${INSTR}

---
You are working in the repository at your current directory. To run Python (3.7 + the
project's deps, not on the host), use:
  docker exec cgcl-mat-box bash -c 'cd ${EP}/work && python3 -c \"...\"'
When done, output a one-line summary of what you implemented."

export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://mintcn.macaron.xin}"
ALLOW="--allowedTools Read,Write,Edit,Bash,Glob,Grep,LS"
START=$(date +%s)
( cd "$WORK" && timeout 600 claude -p "$PROMPT" \
    --output-format stream-json --verbose $ALLOW \
    > "$OUT/agent.jsonl" 2> "$OUT/agent.stderr" )
RC=$?
END=$(date +%s); ELAPSED=$((END-START))
echo "rc=$RC elapsed_sec=$ELAPSED condition=$CONDITION" > "$OUT/agent_meta.txt"
# macaron stream-json: assistant events have usage=0 (endpoint quirk); the real usage is in
# the final 'result' event. Count tool_uses from assistant events, but read tokens from result.
python3 - "$OUT/agent.jsonl" "$OUT/agent_meta.txt" <<'PY' 2>/dev/null || true
import json,sys
tools=turns=in_t=out_t=cache_read=0
for l in open(sys.argv[1]).read().splitlines():
    try: ev=json.loads(l)
    except: continue
    t=ev.get("type")
    if t=="assistant":
        turns+=1
        for c in ev.get("message",{}).get("content",[]):
            if c.get("type")=="tool_use": tools+=1
    elif t=="result":
        u=ev.get("usage",{}) or {}
        in_t=u.get("input_tokens",0); out_t=u.get("output_tokens",0)
        cache_read=u.get("cache_read_input_tokens",0)
with open(sys.argv[2],"a") as f:
    f.write(f"input_tokens={in_t}\noutput_tokens={out_t}\ncache_read_tokens={cache_read}\ntool_uses={tools}\nassistant_turns={turns}\n")
PY
cat "$OUT/agent_meta.txt"
