# summarize — intervene_ripgrep_b621_to_skip_unreachable_seed7_1786644085

Source CSV: `runs/intervene_ripgrep_b621_to_skip_unreachable_seed7_1786644085/results.csv` (the authoritative raw data for this summary).
Episodes: 2  (1 conditions: reset)

| condition | solved/N | reward-series | mean turns | mean elapsed | mean out_tok |
|---|---|---|---|---|---|
| reset | 0/2 | [0,0] | 20 | 600s | 57284 |

## Reset N=2 calibration verdict: too_hard (per phase3 Gate 5)

0/2 solved, BOTH timeout_failed at 600s:
- ep0 reset: 0/timeout_failed, 10 tool_uses, 21 turns, 56k in-tok
- ep1 reset: 0/timeout_failed,  9 tool_uses, 19 turns, 50k in-tok

Failure mode is NOT intrinsic task difficulty (the patch is 31 lines). It is a CONTAINER
COMPILE-TIME constraint: each `cargo test -p ignore` recompiles the ripgrep workspace (minutes
per build), and the agent's ~9-10 tool calls each trigger a build, consuming nearly the entire
600s budget on compilation. The agent gets almost no reasoning/iteration time.

Per phase3.md §3.3: "0/2 success, both near timeout -> too_hard, stop." Marked too_hard; no
4-arm N=1. This is an infra/cost verdict, NOT a causal verdict on the edge — the task itself is
sound (4/4 Executable Gate, 2 caught near-miss, clean mechanism_audit). The intervene container
would need a persistent cargo target cache + pre-built workspace to give this edge a fair
screening. Recorded honestly.
