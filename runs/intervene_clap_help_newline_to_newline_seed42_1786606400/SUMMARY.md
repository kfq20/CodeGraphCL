# N=1 intervention — clap error help_newline -> newline (STRONGEST text-evidence edge)

**Run:** `intervene_clap_help_newline_to_newline_seed42_1786606400` (full 4-arm, seed 42). This
edge had the STRONGEST textual evidence in the bank: the consumer's commit message reads "Found
this when auditing for cases related to #2787", and the producer fixed #2787.

Reset-only probe first (seed 13): reward=1 solved 185s 42 turns — easy-solvable profile (well
under 600s wall), predicting pass-rate saturation.

## Results (N=1 each)

| condition | reward | outcome | elapsed | turns | prefix |
|---|---|---|---|---|---|
| irrelevant | 1 | solved | 295s | 95 | 368c |
| correct    | 1 | timeout_solved | 600s (WALL) | 137 | 658c |
| wrong       | 1 | solved | 166s | 60 | 502c |
| reset       | 1 | solved | 421s | 133 | 0c |

## Honest reading

**Pass-rate saturated at 1.0 across all 4 arms** — even the WRONG/stale atom ("library returns
bare messages, caller terminates lines") did not cause failure; the agent solved it under every
prior. The task is too easy (2-line patch) for a pass-rate CL signal.

**Cost direction is OPPOSITE the beneficial-edge hypothesis, again.** The hypothesis predicts
correct < reset < wrong. The data shows wrong (166s) << irrelevant (295s) < reset (421s) <
correct (600s, at the wall). correct is the SLOWEST, not the fastest. This mirrors the
hasheader->removeheader N=1 (where correct also tied-reset-slowest). The pattern across BOTH
N=1 runs: a longer "correct" preamble sends the agent on a longer exploration (more turns,
closer to the wall), while a pithy "wrong" preamble lets it solve faster. The priors do not act
as knowledge that reduces work — they act as preamble that shapes effort length.

## Go/No-Go (per phase2 funnel)

**No-go for N=3.** N=1 sensitivity is not in the predicted direction on EITHER edge run
(hasheader + this one). phase2.md says escalate to N=3 only "if N=1 shows reasonable
sensitivity" — here sensitivity is present (cost varies) but consistently REVERSED, so it is
not the beneficial-transfer signal the edge types claim. Two reversed N=1s is enough to stop
the funnel on this edge class rather than burn ~40 more min.

## Cross-cutting conclusion (the real phase2 finding)

Three N=1 runs now (c4->c5 too-hard, hasheader saturated-easy, clap-newline saturated-easy +
reversed) converge on one finding: **the single-node consistency tasks in this bank do not
carry a clean CL causal signal**, even when the textual provenance evidence is strongest.
They saturate at either end — too easy (pass-rate 1.0, cost direction reversed) or too hard
(3/4 timeout). The narrow CL-readable band is multi-node revision edges where reset solves AT
the wall but doesn't time out (the c3->c4 shape). The bank's single-node tasks are good for
construction/anti-hardcoding evidence and the Separability Gate analysis, but not for the
causal-verification KPI. The causal-verification standard therefore cannot be met from the
current bank without building more multi-node revision edges in the c3->c4 difficulty band.
