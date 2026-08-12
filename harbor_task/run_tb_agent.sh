#!/usr/bin/env bash
# T_B agent phase: claude on HOST, cwd = host-side EP/work. Uses build_prompt.py (not the
# broken sed extractor) so non-reset prefixes are guaranteed non-empty, and a manifest is
# written for audit. Docker path in the prompt uses the CONTAINER path /pool/<ep>/work.
set -uo pipefail
EP="$1"; CONDITION="$2"
ROOT="/vePFS-Mindverse/user/intern/fanqi/CodeGraphCL"
STEP="$ROOT/harbor_task/steps/tB_start_tls_trio"
WORK="$EP/work"; OUT="$EP/out"; mkdir -p "$OUT"

# EP is a host path under /tmp/cgcl_box_pool/<name>. The container sees the same dir as
# /pool/<name>. Derive the container workdir for the prompt's docker hint.
EPNAME=$(basename "$EP")
CONTAINER_WORK="/pool/$EPNAME/work"

# Build prompt + manifest via the tested Python builder (fails hard on empty prefix).
python3 "$ROOT/harbor_task/build_prompt.py" \
  "$ROOT/harbor_task/tB_experience_atoms.md" \
  "$STEP/instruction.md" \
  "$CONDITION" "$CONTAINER_WORK" "$OUT" > "$OUT/manifest.stdout" 2> "$OUT/manifest.stderr"
BP_RC=$?
if [ "$BP_RC" -ne 0 ]; then
  echo "build_prompt FAILED for condition=$CONDITION (rc=$BP_RC):" >&2
  cat "$OUT/manifest.stderr" >&2
  # write a manifest-free failure marker so the episode doesn't silently proceed
  echo "reward=ERR build_prompt_failed" > "$EP/reward.txt"
  exit 2
fi
PROMPT=$(cat "$OUT/prompt.txt")

export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://mintcn.macaron.xin}"
ALLOW="--allowedTools Read,Write,Edit,Bash,Glob,Grep,LS"
START=$(date +%s)
( cd "$WORK" && timeout 600 claude -p "$PROMPT" \
    --output-format stream-json --verbose $ALLOW \
    > "$OUT/agent.jsonl" 2> "$OUT/agent.stderr" )
RC=$?
END=$(date +%s); ELAPSED=$((END-START))
echo "rc=$RC elapsed_sec=$ELAPSED condition=$CONDITION" > "$OUT/agent_meta.txt"
# real usage is in the final 'result' event (macaron per-assistant usage is all zeros)
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
