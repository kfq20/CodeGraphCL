# N=3 causal verification — ripgrep c3 -> c4 (the ONLY edge escalated to N=3)

**Run:** `intervene_ripgrep_c3_to_c4_seed42_1786611149` (12 episodes, 3 blocks × 4 conditions,
block-randomized, seed 42, opaque ep IDs). This was the ONLY edge of 5 probed that qualified
for N=3 (its N=1 showed pass-rate sensitivity: irrelevant failed, others solved).

## Per-condition results (3 reps each)

| condition | solved/3 | rewards | mean turns |
|---|---|---|---|
| reset | 1/3 | [0, 1, 0] | 149 |
| correct | 1/3 | [0, 0, 1] | 132 |
| irrelevant | 2/3 | [1, 1, 0] | 140 |
| wrong | 2/3 | [1, 0, 1] | 134 |

## Causal verdict: REJECTED — does NOT pass the Causal Dependency Gate

The beneficial-edge hypothesis predicts correct > reset > irrelevant, and wrong/stale worse.
The data shows the OPPOSITE: correct (1/3) is the WORST or tied-worst, no better than reset
(1/3), and WORSE than irrelevant (2/3) and wrong (2/3). The correct prior neither helped nor
broke even — every condition fluctuates between 1/3 and 2/3 solved, with no stable ordering.

Per phase2 Go/No-Go: "Correct 与 Irrelevant 相同：只有通用 preamble 效应；四组无稳定差异：T_B
对经验不敏感" — this edge lands in the no-stable-difference bucket. **c3->c4 does not carry a
stable CL causal signal.**

## Why (root cause)

The task sits exactly at the 600s wall (every episode times out; success = whether the agent's
random walk happened to land a passing edit before the wall). At the wall, success is dominated
by path-variance, not by the prior. The N=1 "sensitivity" (irrelevant failed, correct solved)
was a single draw from this high-variance distribution — N=3's 3 draws per condition confirm the
N=1 ordering does not reproduce. This is the wall-band failure mode: not saturated (pass-rate
varies), but variance-dominated (no stable signal).

## Cross-cutting conclusion (the full funnel, now complete)

All 5 probed edges fail the Causal Dependency Gate:
- c4->c5: too hard (3/4 timeout, reset failed) — saturated-hard
- hasheader->removeheader: saturated-easy (4/4 solved, cost reversed)
- clap newline (strongest text evidence): saturated-easy (4/4, cost reversed)
- c2->c3: infra-flake (reward-path), untested
- c3->c4: variance-dominated at the wall (no stable ordering)

The bank's edges — even the single one with the strongest textual provenance and the only one in
the CL-readable wall band — do not yield a causally-verified beneficial edge. The
causal-verification KPI (N=3 on 4-6 sensitive edges) was EXECUTED on the one qualifying edge and
returned a negative result. Meeting the KPI with a POSITIVE result requires edges where the agent
solves comfortably BELOW the wall (so pass-rate doesn't saturate) AND the prior deterministically
shapes the path — a band the current bank does not contain.
