# N=1 intervention — ripgrep c3 -> c4 (the wall-band edge)

**Run:** `intervene_ripgrep_c3_to_c4_seed42_1786608700` (full 4-arm, seed 42). This was the ONLY
edge in the funnel whose reset-feasibility probe landed in the wall band (reset probe seed7:
reward=1 timeout_solved 600s 208 turns — solves AT the wall, not below it).

## Results (N=1 each)

| condition | reward | outcome | elapsed | turns | prefix |
|---|---|---|---|---|---|
| irrelevant | **0** | timeout_failed | 600s | 101 | 330c |
| correct    | 1 | timeout_solved | 600s | 154 | 556c |
| wrong       | 1 | timeout_solved | 600s | 198 | 473c |
| reset       | 1 | timeout_solved | 600s | 144 | 0c |

## Honest reading — FIRST edge with pass-rate sensitivity

This is the ONLY N=1 in the funnel where pass-rate did NOT saturate. 3 of 4 arms solved;
**irrelevant FAILED (reward 0)**. The direction is partially correct: correct (c3's
precise-strip rule) solved while irrelevant (CLI/printer facts) failed — consistent with the
beneficial-edge hypothesis (the correct prior helped; the irrelevant prior didn't).

But two caveats:
1. **wrong/stale also solved** — no negative transfer from the stale c2 prior. The signal is
   "any preamble > empty for feasibility" rather than "correct > irrelevant specifically".
2. **reset also solved** — so empty preamble is enough here (the agent CAN derive it from
   scratch). The correct prior's edge over reset is only visible in that irrelevant (a
   non-empty but unhelpful preamble) FAILED while reset (empty) solved — i.e. an unhelpful
   preamble can be WORSE than no preamble. That's a placebo/inertia effect, not pure benefit.

**Per phase2 funnel rule: "only run N=3 if N=1 shows reasonable sensitivity."** This N=1 DOES
show pass-rate sensitivity (3 vs 1, in a partially-correct direction) — the ONLY one of 5
probed edges to do so. So this edge is the single N=3 candidate.

## Go/No-Go: GO for N=3 (the only edge that qualifies)

This is the edge to escalate. N=3 (12 episodes, block-randomized) would test whether the
irrelevant-fails / others-solve pattern is stable (correct ≥ irrelevant in pass-rate) or was
N=1 noise (the irrelevant episode happened to walk a bad path). If stable, this is the bank's
first causally-verified beneficial edge (beneficial-not-required, like httpx_tB's shape but at
the feasibility margin rather than saturated).

NOTE on budget: N=3 = 12 × ~600s ≈ 2h. Run in background; the result lands the
causal-verification standard phase2.md requires.
