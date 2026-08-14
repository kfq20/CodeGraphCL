# summarize — intervene_fastify_c1_to_cef_decorator_seed42_1786679152

Source CSV: `runs/intervene_fastify_c1_to_cef_decorator_seed42_1786679152/results.csv` (the authoritative raw data for this summary).
Episodes: 15  (5 conditions: correct_long, correct_short, irrelevant_long, irrelevant_short, reset)

| condition | solved/N | reward-series | mean turns | mean elapsed | mean out_tok |
|---|---|---|---|---|---|
| reset | 3/3 | [1,1,1] | 81 | 292s | 9976 |
| correct_long | 3/3 | [1,1,1] | 65 | 163s | 7686 |
| correct_short | 3/3 | [1,1,1] | 80 | 183s | 9735 |
| irrelevant_long | 3/3 | [1,1,1] | 57 | 186s | 6486 |
| irrelevant_short | 2/3 | [ERR,1,1] | 58 | 119s | 5584 |

**infra_fail episodes: 1** (ep_000002:irrelevant_short) — reward not written; exclude from pass-rate stats or treat as failure per study design.
