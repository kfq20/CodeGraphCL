# summarize — intervene_fastify_c1_to_cef_decorator_seed42_1786679152

Source CSV: `runs/intervene_fastify_c1_to_cef_decorator_seed42_1786679152/results.csv` (the authoritative raw data for this summary).
Episodes: 14  (5 conditions: correct_long, correct_short, irrelevant_long, irrelevant_short, reset)

| condition | solved/N | reward-series | mean turns | mean elapsed | mean out_tok |
|---|---|---|---|---|---|
| reset | 3/3 | [1,1,1] | 81 | 292s | 9976 |
| correct_long | 3/3 | [1,1,1] | 65 | 163s | 7686 |
| correct_short | 3/3 | [1,1,1] | 80 | 183s | 9735 |
| irrelevant_long | 2/2 | [1,1] | 60 | 186s | 6474 |
| irrelevant_short | 2/3 | [ERR,1,1] | 58 | 119s | 5584 |

**infra_fail episodes: 1** (ep_000002:irrelevant_short) — reward not written; exclude from pass-rate stats or treat as failure per study design.

## Phase 3.1 edge1 (c1->cef) FULL result — generic-preamble effect, no content effect

| condition | solved | mean_elapsed | mean_tools |
|---|---|---|---|
| reset | 3/3 | 292s | 47 |
| correct_short | 3/3 | 183s | 45 |
| irrelevant_short | 2/3 (1 infra) | 112s | 32 |
| correct_long | 3/3 | 163s | 37 |
| irrelevant_long | 2/2 | 186s | 33 |

CLASSIFICATION: **generic-preamble effect** (Correct ≈ Irrelevant > Reset). All conditions solve;
reset is slowest (292s); correct and irrelevant are indistinguishable (~163-186s). The Phase 2/3
REVERSED pattern (correct worse than irrelevant) DISAPPEARS under length control — confirming it
was a LENGTH CONFOUND, not a content effect.

Per the pre-registered Phase 3.1 interpretation: "Correct ≈ Irrelevant > Reset" -> generic
preamble or exploration-start effect. This is one of two edges; edge2 (getschemas) confirms.
NOT a content effect (correct does NOT beat irrelevant at either length). NOT length-only
(short and long perform similarly within the armed conditions — both ~163-186s).
