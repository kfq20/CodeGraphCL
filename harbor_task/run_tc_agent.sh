#!/usr/bin/env bash
# T_C agent phase: claude on HOST, cwd = EP/work. Uses build_prompt.py with tC atoms.
set -uo pipefail
EP="$1"; CONDITION="$2"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
STEP="$ROOT/harbor_task/steps/tC_start_tls_stream"
WORK="$EP/work"; OUT="$EP/out"; mkdir -p "$OUT"
EPNAME=$(basename "$EP")
CONTAINER_WORK="/pool/$EPNAME/work"

python3 "$ROOT/harbor_task/build_prompt.py" \
  "$ROOT/harbor_task/tC_experience_atoms.md" \
  "$STEP/instruction.md" \
  "$CONDITION" "$CONTAINER_WORK" "$OUT" > "$OUT/manifest.stdout" 2> "$OUT/manifest.stderr"
BP_RC=$?
if [ "$BP_RC" -ne 0 ]; then
  echo "build_prompt FAILED for condition=$CONDITION (rc=$BP_RC)" >&2; cat "$OUT/manifest.stderr" >&2
  echo "reward=ERR build_prompt_failed" > "$EP/reward.txt"; exit 2
fi
PROMPT=$(cat "$OUT/prompt.txt")

export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://mintcn.macaron.xin}"
CGCL_MODEL="${CGCL_MODEL:-}"; MODEL_FLAG=""
[ -n "$CGCL_MODEL" ] && MODEL_FLAG="--model $CGCL_MODEL"
claude --version > "$OUT/cli_version.txt" 2>&1
ALLOW="--allowedTools Read,Write,Edit,Bash,Glob,Grep,LS"
START=$(date +%s)
( cd "$WORK" && timeout 600 claude -p "$PROMPT" \
    --output-format stream-json --verbose $ALLOW $MODEL_FLAG \
    > "$OUT/agent.jsonl" 2> "$OUT/agent.stderr" )
RC=$?
END=$(date +%s); ELAPSED=$((END-START))
echo "rc=$RC elapsed_sec=$ELAPSED condition=$CONDITION" > "$OUT/agent_meta.txt"
python3 - "$OUT/agent.jsonl" "$OUT/agent_meta.txt" <<'PY' 2>/dev/null || true
import json,sys
tools=turns=in_t=out_t=cache_read=cache_create=0
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
        cache_read=u.get("cache_read_input_tokens",0); cache_create=u.get("cache_creation_input_tokens",0)
with open(sys.argv[2],"a") as f:
    f.write(f"input_tokens={in_t}\noutput_tokens={out_t}\ncache_read_tokens={cache_read}\n"
            f"cache_creation_tokens={cache_create}\ntool_uses={tools}\nassistant_turns={turns}\n")
PY
cat "$OUT/agent_meta.txt"
