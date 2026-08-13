# N=1 intervention — fastify hasheader -> removeheader edge

**Run:** `intervene_fastify_hasheader_to_removeheader_seed42_1786603532` (full 4-arm, seed 42,
opaque ep IDs). Reset-only feasibility probe first (seed 11): reward=1 solved 177s 25 turns —
good feasibility (well under 600s wall, room for a cost-metric read).

## Results (N=1 each)

| condition | reward | outcome | elapsed | turns | out_tok | prefix |
|---|---|---|---|---|---|---|
| irrelevant | 1 | solved | 186s | 41 | 14.9k | 225c |
| correct    | 1 | solved | 311s | 110 | 11.1k | 580c |
| wrong       | 1 | solved | 372s | 96  | 18.0k | 413c |
| reset       | 1 | solved | 442s | 110 | 20.7k | 0c |

## Honest reading

**Pass-rate saturated at 1.0 across all 4 arms** — the wrong/stale atom (case-sensitive storage,
no chaining) did NOT cause failure: the agent solved removeHeader under it too. This task is too
easy for a pass-rate CL signal (consistent with the reset probe: 177s/25 turns).

**Cost-metric shows asymmetry but the DIRECTION does not match the beneficial-edge hypothesis.**
The hypothesis predicts correct < reset < wrong (correct prior cuts cost; stale prior raises it).
The data shows irrelevant (41 turns) << wrong (96) ≈ correct (110) ≈ reset (110). correct is NOT
cheaper than reset — if anything correct took the MOST turns (tied with reset). wrong did not
cost more than correct.

This is high-variance N=1 noise: correct's 110 turns likely reflects that the 580c preamble sent
the agent on a longer exploration, not that the correct prior HURT. With N=1 this is unverifiable.

## Go/No-Go (per phase2 funnel)

**No-go for N=3 on this edge.** The N=1 sensitivity is MUD: pass-rate saturated, and the cost
asymmetry's direction contradicts the hypothesis (or is noise). phase2.md says "只有 N=1 出现合理
敏感性，才运行 N=3" — the sensitivity here is not in the predicted direction, so escalating
would burn ~40 min for likely-noisy 3-of-each. Recorded as a saturated-easy edge (cost-metric-
inconclusive), same shape as the httpx_tB beneficial-not-required finding but at the EASY end
(saturated-success) rather than the hard end (c5 saturated-failure).

## Lesson reinforced

The reset-only feasibility probe correctly predicted this: reset solved in 177s/25 turns, far
from the wall — that ease foretold pass-rate saturation. The probe is a reliable gate: it tells
you whether an edge can show a COST signal (reset near the wall, like c3->c4) vs will saturate
(reset easy, like here). This edge sat in the "easy → saturate" bucket. The good CL targets are
in the narrow band where reset solves AT the wall but doesn't time out — there, cost has room to
move. This task wasn't in that band.
