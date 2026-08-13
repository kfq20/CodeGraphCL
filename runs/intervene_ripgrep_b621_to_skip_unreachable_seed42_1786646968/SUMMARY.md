# summarize — intervene_ripgrep_b621_to_skip_unreachable_seed42_1786646968

Source CSV: `runs/intervene_ripgrep_b621_to_skip_unreachable_seed42_1786646968/results.csv` (the authoritative raw data for this summary).
Episodes: 4  (4 conditions: correct, irrelevant, reset, wrong)

| condition | solved/N | reward-series | mean turns | mean elapsed | mean out_tok |
|---|---|---|---|---|---|
| reset | 0/1 | [0] | 113 | 600s | 37896 |
| correct | 0/1 | [0] | 67 | 600s | 0 |
| irrelevant | 1/1 | [1] | 84 | 600s | 53780 |
| wrong | 0/1 | [0] | 22 | 600s | 0 |

## 4-arm N=1 result (warm cache, seed 42): 1/4 solved — REVERSED, no-go for N=3

| condition | reward | outcome | tool_uses |
|---|---|---|---|
| irrelevant | 1 | timeout_solved | 42 |
| correct    | 0 | timeout_failed | 36 |
| wrong      | 0 | timeout_failed | 11 |
| reset      | 0 | timeout_failed | 63 |

Only 1/4 solved (irrelevant), and the direction is REVERSED vs the beneficial hypothesis: the
arm with NO relevant prior (irrelevant) solved, while correct FAILED. None of phase3 Gate 6's
escalation triggers fire (trigger 1 requires correct-succeed-while-reset/irrelevant-fail; here
it is the opposite). No-go for N=3.

This is the SAME reversed pattern seen across all Phase 2 edges (hasheader, clap-newline,
getschemas, c1->cef) and now this Phase 3 edge. The cross-bank finding (NOT a per-edge verdict,
n=1 screening only): a longer "correct" preamble tends to LENGTHEN the agent's exploration
without improving success, while a pithy "irrelevant" preamble solves. The priors act as
effort-length shapers, not as knowledge that reduces work — consistent across the bench.
