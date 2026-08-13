# summarize — intervene_ripgrep_b621_to_skip_unreachable_seed7_1786645694

Source CSV: `runs/intervene_ripgrep_b621_to_skip_unreachable_seed7_1786645694/results.csv` (the authoritative raw data for this summary).
Episodes: 2  (1 conditions: reset)

| condition | solved/N | reward-series | mean turns | mean elapsed | mean out_tok |
|---|---|---|---|---|---|
| reset | 1/2 | [1,0] | 61 | 600s | 54213 |

## Reset N=2 calibration (WARM cargo cache): 1/2 solved -> NON-saturated -> proceed to 4-arm

With a persistent warm cargo target cache (CGCL_CARGO_TARGET_DIR=/pool/rg_warm/target, pre-built
once), cold compile time (minutes/build) drops to ~2s warm incremental. The 0/2 too_hard verdict
was a cold-compile artifact:
- ep0 reset: 1/timeout_solved, 60 tool_uses, 102 turns (vs 10 tool_uses cold — the agent now iterates)
- ep1 reset: 0/timeout_failed, 7 tool_uses, 20 turns (this one hit the wall)

1/2 solved, NOT all at the wall -> per phase3 Gate 5, NON-saturated -> PROCEED to 4-arm N=1.
