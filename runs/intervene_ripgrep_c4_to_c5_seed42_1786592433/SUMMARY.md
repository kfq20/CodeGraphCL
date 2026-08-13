# N=1 intervention summary — ripgrep c4->c5 (43e2f08) Update edge

**Run:** `intervene_ripgrep_c4_to_c5_seed42_1786592433` (seed 42, opaque ep IDs, block 0 order:
irrelevant → correct → wrong → reset). N=1 per condition.

## Results

| condition | reward | outcome | elapsed | out_tok | cache_read | turns | prefix |
|---|---|---|---|---|---|---|---|
| irrelevant | 0 | timeout_failed | 600s | 40,366 | 646,104 | 51 | 330c |
| correct    | 0 | timeout_failed | 600s | 37,958 | 1,003,642 | 50 | 716c |
| wrong       | **1** | **timeout_solved** | 600s | 63,402 | 3,163,136 | 105 | 449c |
| reset       | 0 | timeout_failed | 600s | 20,358 | 2,326,619 | 114 | 0c |

## Honest reading (N=1 — NOT conclusive)

3 of 4 arms FAILED (reward 0, timeout). Only the **wrong/stale arm (c3 pre-caching prior)**
solved the task (reward 1, timeout_solved). This is the OPPOSITE of the c4->c5 beneficial-edge
hypothesis, which predicted correct (c4 caching discipline) would help and stale (c3) would hurt.

But N=1 cannot distinguish signal from variance:
- The wrong arm's success correlates with the MOST effort (105 turns, 63k output tokens, 3.1M
  cache — the most active episode). It likely stumbled onto a working path during a long
  high-effort search, not because the stale prior *helped*.
- reset had the MOST turns (114) yet failed — turns/effort did not deterministically produce
  success.
- correct used the FEWEST output tokens (38k) — the c4 prior may have made the agent stop
  early / commit to a wrong structural guess, but at N=1 this is speculation.

## Go/No-Go verdict (per phase2 funnel)

**INCONCLUSIVE — do not escalate to N=3 yet.** The 3-failures-1-fluke-success pattern is
high-variance, not a stable beneficial/negative signal. The correct next step is NOT to run
N=3 on c5 (it would burn ~40 min for a likely-noisy 3-of-each). Instead:

1. **c5 is too hard for a clean N=1 read** — the agent cannot reliably solve the structural
   refactor in 600s even with the correct prior. This makes it a poor intervention target
   (saturated-at-failure, like the httpx tA/tC instruction-leak cases but for a different
   reason: genuine difficulty, not leakage).
2. **Retarget to an easier revision edge** where reset can solve the base task in <300s, so the
   edge measures experience *cost* not *feasibility*. Candidates: the simpler ripgrep c3->c4
   edge (c4 is `.`-dir scope, smaller refactor) or a fastify parity edge.
3. **Keep c5 as a difficulty datapoint** — it shows the structural-refactor floor where the
   agent times out regardless of prior. Documented, not promoted to N=3.

## What WAS validated (the pipeline, not the signal)

- The intervention harness worked end-to-end on a NEW edge built this session: opaque ep IDs,
  block-randomized order, 4 distinct verified prompts (prompt-preview PASS earlier), sentinel-
  poll verifier, full token/turn/cost telemetry recorded per episode, failure taxonomy applied
  (timeout_failed vs timeout_solved distinguished correctly).
- No condition-name leakage (opaque IDs; the manifest maps ep_000000..3 to conditions).
- The c4->c5 edge's atoms/instruction/separability held up under real agent use.

This run is a real datapoint: the first N=1 on a NEW (non-httpx) edge, showing the harness
produces honest, non-saturated, variance-bearing data — even when that data is inconclusive.
