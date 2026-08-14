# summarize — intervene_fastify_getschemas_to_cleanid_seed42_1786682338

Source CSV: `runs/intervene_fastify_getschemas_to_cleanid_seed42_1786682338/results.csv` (the authoritative raw data for this summary).
Episodes: 15  (5 conditions: correct_long, correct_short, irrelevant_long, irrelevant_short, reset)

| condition | solved/N | reward-series | mean turns | mean elapsed | mean out_tok |
|---|---|---|---|---|---|
| reset | 3/3 | [1,1,1] | 119 | 600s | 23043 |
| correct_long | 1/3 | [0,1,0] | 97 | 536s | 44063 |
| correct_short | 2/3 | [1,1,0] | 96 | 573s | 24274 |
| irrelevant_long | 2/3 | [0,1,1] | 85 | 531s | 16508 |
| irrelevant_short | 2/3 | [0,1,1] | 121 | 498s | 28223 |

## Phase 3.1 edge2 (getschemas->cleanid) FULL result — wall-band, variance-dominated, no content effect

| condition | solved/3 | reward-series | mean elapsed |
|---|---|---|---|
| reset | 3/3 | [1,1,1] | 600s |
| correct_short | 2/3 | [1,1,0] | 573s |
| irrelevant_short | 2/3 | [0,1,1] | 498s |
| correct_long | 1/3 | [0,1,0] | 536s |
| irrelevant_long | 2/3 | [0,1,1] | 531s |

CLASSIFICATION: variance-dominated at the wall (this is the Phase-2 'reversed' edge, a 5-line
patch where reset barely solves 3/3 at the 600s wall). NO content effect: correct is not
consistently > irrelevant (correct_short 2/3 ≈ irrelevant_short 2/3 ≈ irrelevant_long 2/3; only
correct_long 1/3 is worst). Does NOT replicate edge1's clean generic-preamble result (edge1:
reset slowest, all armed solve; edge2: reset solves most, opposite direction at the wall).

The length confound IS controlled (pairs matched <=5%), so this edge2 result is a clean read of
"wall-band variance" — not a length artifact. The combined picture: the reversed pattern from
Phase 2/3 was partly a length confound (edge1 shows it disappears under length control) AND
partly wall-band variance (edge2 shows no stable ordering even with length control). Neither
edge shows a semantic content effect (correct > irrelevant at matched length).
