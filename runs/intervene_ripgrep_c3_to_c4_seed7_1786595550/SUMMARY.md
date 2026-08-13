# Reset-only feasibility probe — ripgrep c3->c4 edge

**Run:** `intervene_ripgrep_c3_to_c4_seed7_1786595550` (seed 7, reset condition only, N=1).

Motivation: after the c4->c5 N=1 came back INCONCLUSIVE (3/4 arms timed out — c5 too hard to
read), the lesson recorded was: **sanity-check that a reset agent can solve the base task
before spending a full 4-arm N=1 on an edge.** This probe applies that check to c3->c4.

## Result

| condition | reward | outcome | elapsed | tool_uses | turns | prefix |
|---|---|---|---|---|---|---|
| reset | **1** | timeout_solved | 600s | 125 | 208 | 0c |

## Reading

**c4 IS solvable by a reset agent** — unlike c5, where reset failed (reward 0, timeout_failed).
This confirms c4 is the better intervention target of the two: the `.`-dir/hidden-file scope
refinement (57-line gold patch) is within the agent's reach, while c5's structural refactor
(249-line patch moving a field between structs + rewiring 3 sites) is not.

But two caveats bound what the c3->c4 edge can measure:

1. **`timeout_solved`, not a comfortable solve.** The agent used the full 600s budget and 208
   turns / 125 tool calls. It solved it right at the wall. So c4 sits near the feasibility
   ceiling, not comfortably below it.
2. **Correctness will saturate.** With reset already at reward 1.0, a correct prior cannot
   improve the pass rate — the edge can only show up as a **cost** difference (elapsed, turns,
   tool calls, tokens). This is the same shape as the httpx_tB finding: beneficial-not-required.

## Implication for the funnel

c3->c4 is worth a full 4-arm N=1 **if** the metric of record is cost, not pass rate. The
pre-registered prediction would be: correct (c3's precise-strip rule) reduces turns/tool-calls
vs reset; stale (c2's naive strip) increases them or flips reward to 0.

Given the 600s-at-the-wall reset, a 4-arm N=1 costs ~40 min and the correctness dimension is
already known to be saturated. Recorded here so the next session can run it with the right
expectation (cost-metric read) rather than re-discovering the saturation.

## Note on the aborted full run

An earlier full 4-arm N=1 on c3->c4 (`intervene_ripgrep_c3_to_c4_seed42_1786595042`) was killed
mid-flight by a host disk-full (ENOSPC) condition — the accumulated intervention worktrees and
multi-MB agent.jsonl files filled /tmp. No results were written. Cleanup freed 7.7G. Future
runs should prune `/tmp/cgcl_box_pool/ep_*` between batches.
