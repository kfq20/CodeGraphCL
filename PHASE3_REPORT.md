# Phase 3 Report — Causally Verified Edge Construction

**Status: Phase 3A complete — first round of edge-first screening done; causal screening
underpowered and carrier-confounded; Phase 3.1 (carrier ablation) in progress.**

This is the single, non-duplicated report version. Per phase3.md §4.3, this report does NOT
claim a causally-grounded CL benchmark — only that a screening pass was run and a confound was
identified that blocks any causal conclusion.

## 1. Candidate funnel statistics

| stage | count |
|---|---|
| new candidates audited | 10 (>= 8 target ✓) |
| passed Semantic Audit | 2 built (cand 7, cand 10) |
| passed Mechanism Audit | 2 (both 5-field) |
| passed Separability | 2 (both 9/9, prompt-preview PASS) |
| passed Executable Gate | 1 of 2 (cand 10: 4/4 + 2 caught near-miss; cand 7: near-miss blocked) |
| passed Reset Calibration | 1 (cand 10: non-saturated 1/2 with warm cargo cache) |
| 4-arm N=1 run | 1 (cand 10: reversed, no-go N=3) |
| N=3 run (this phase) | 0 (1 N=3 carried from Phase 2 c3->c4: rejected_no_ordering) |
| causally_verified_v0 | 0 (target 2-3) |
| Natural Stateful pilot | 0 (no verified edge to gate it on) |

## 2. Per-edge mechanism audit + funnel outcome

### Candidate 10 — ripgrep skip_unreachable_ignore (BUILT, gated, N=1 reversed)
- repo: ripgrep | motif: lifecycle/cache-invalidation
- producer: b621e65 (ignore: add incremental checking — the per-dir matcher cache architecture)
- consumer: 435f59f (skip unreachable ignore files — empty matcher at boundary, no file load)
- ancestry: confirmed
- Executable Gate: 4/4 + 2 caught near-miss (onlyskipdir, invert) — VERIFIED
- Reset calibration (warm cache): 1/2 non-saturated -> 4-arm
- 4-arm N=1: 1/4 solved (irrelevant solved; correct/wrong/reset FAILED) — REVERSED, no-go N=3
- mechanism_audit: 5 fields written (reusable_decision, 2 plausible paths, why-instruction-
  doesn't-disambiguate, why-correct-selects, why-wrong-plausible)

### Candidate 7 — fastify onSend hook runner (near-miss blocked)
- repo: fastify | motif: scope/ownership
- base-fail + gold-pass VERIFIED, but 3 near-miss variants all PASS under gold (resolve-to-value
  test has a single failure mode + a Node-version skip interferes with test numbering). Cannot
  satisfy the >=2 caught-near-miss gate. Marked pending near-miss.

### Audited, not built (per §2.0 feasibility verdicts)
- cand 1 (clap mangen): no base-fail (test passes on base)
- cand 2 (clap require-literal): blocked (trybuild UI test needs Rust 1.97 + unstable feature)
- cand 3 (clap nushell DirPath): patch too small (3 lines)
- cand 4 (ripgrep global gitignore): overlaps cand 5/6
- cand 5 (ripgrep c4->c5): Phase 2 overlap, too hard
- cand 6 (ripgrep GIT_CONFIG_GLOBAL): viable, same cargo-compile risk as cand 10
- cand 8 (fastify 404 encapsulated): 99-line refactor, rejected
- cand 9 (fastify trust proxy): test-only consumer

## 3. Reset calibration results
- cand 10 cold cache: 0/2 timeout (too_hard) — a COLD-CARGO-COMPILE artifact (cargo rebuilds the
  workspace per tool call, ~min/build, eating the 600s budget; 9-10 tool calls). NOT intrinsic
  difficulty.
- cand 10 warm cache (CARGO_TARGET_DIR): 1/2 (ep0 timeout_solved 60 tools, ep1 timeout_failed) —
  non-saturated -> 4-arm. This retracts the too_hard verdict.

## 4. N=1 four-arm result (cand 10, warm cache, seed 42)
| condition | reward | outcome | tool_uses |
|---|---|---|---|
| irrelevant | 1 | timeout_solved | 42 |
| correct | 0 | timeout_failed | 36 |
| wrong | 0 | timeout_failed | 11 |
| reset | 0 | timeout_failed | 63 |
1/4 solved (irrelevant); REVERSED vs the beneficial hypothesis (correct FAILED, irrelevant
solved). None of phase3 Gate 6's escalation triggers fire. No-go for N=3. n=1 screening, not an
effect estimate.

## 5. Verified / Rejected / Blocked classification
- causally_verified_v0: 0
- rejected: cand 10 (N=1 reversed); Phase 2 c3->c4 (N=3 rejected_no_ordering)
- blocked: cand 2 (Rust 1.97 toolchain); cand 7 (near-miss design); cand 10 cold (compile-time,
  since fixed)
- **SELF-LOOP CORRECTION (reviewer):** the ripgrep_b621_to_skip_unreachable edge had from==to
  (self-loop) because the producer b621e65 is a real commit but NOT a materialized Task Node. It
  is now marked provenance_type: external_commit (from: b621e65 external) — NOT a strict
  Task-Graph edge and won't count for stream construction until a producer node is materialized.

## 6. Natural Stateful pilot
Not executed. Natural Stateful runs only on causally_verified_v0 edges (§4.1); none exist. This
is the correct protocol application — running Stateful on a reversed/blocked edge would not be
interpretable.

## 7. Allowed vs not-allowed paper claims
ALLOWED:
- CodeGraphCL is a runnable candidate Task/Edge Bank with a pre-registered causal-dependency-gate
  protocol; the gate was executed.
- The screening shows a REVERSED pattern (correct not better than irrelevant) on cand 10 +
  the Phase 2 edges — n=1/edge, screening (not an effect estimate).
- Infra caveat: cold cargo compile is a false-too_hard artifact (fix: warm CARGO_TARGET_DIR).

NOT ALLOWED (over-reads retracted, per reviewer):
- ~~"The bank contains a causally verified experience edge."~~ — 0 verified.
- ~~"correct history helps" / "variance dominates."~~ — reversed at n=1, not statistical.
- ~~"No causal edge exists."~~ — only a subset screened; cannot claim bank-wide.
- ~~"effort-length shaper is a finding."~~ — DOWNGRADED TO HYPOTHESIS. The reversed pattern is
  CONFOUNDED: correct atoms were 1.5–2.8x longer than irrelevant across all edges (cand 10:
  correct 936 vs irrelevant 334 chars). Semantic content and prompt length are not separated.
  The Phase 3.1 carrier ablation (5-condition, length-matched) tests this directly; until it
  reproduces, "effort-length shaper" is a hypothesis, not a finding.

## 8. Verified Graph inventory for Phase 4
EMPTY. 0 causally_verified_v0 edges. The candidate bank (20 executable_candidate nodes, 8
protocol-ready edges) stands as runnable, but cannot emit a causally-grounded Diagnostic Stream.

## 9. Phase 3.1 — Experience Carrier Control (in progress)
The reviewer's core point: the 0-verified-edge result cannot distinguish "graph formulation
fails" from "the intervention implementation (long-prose-preamble atom) is not construct-valid."
Phase 3.1 runs a 5-condition N=3 carrier ablation on 2 stable fastify edges to separate content
effect from length/carrier effect:

| condition | purpose |
|---|---|
| Reset | no-history baseline |
| Correct-short | minimal correct experience |
| Irrelevant-short | strictly length+format-matched to Correct-short |
| Correct-long | current long-prose correct experience |
| Irrelevant-long | strictly length+format-matched to Correct-long |

Controls: short pair and long pair each token-matched <=5% (tiktoken); same sentence structure,
paragraph count, technical density; only semantic content changes; instruction/Gold/verifier
unchanged; N=3 block-randomized; saved as a NEW experiment (atoms_ablation.md, not overwriting
atoms.md). Pre-registered interpretation:
- Correct-short > Irrelevant-short -> content effect real, long carrier harmful
- short > long, semantics-independent -> length/carrier effect
- Correct ≈ Irrelevant > Reset -> generic-preamble effect
- no stable direction -> the N=1 reversed pattern was mostly noise
- Correct < Irrelevant stable AFTER length-match -> correct prior over-commits to wrong path

Atoms written + length-verified (both edges PASS <=5%): fastify_decorator_getter (c1->cef),
fastify_clean_schema_id (getschemas->cleanid). Run in flight.

## 10. Next-step decision (3-way, contingent on Phase 3.1 outcome)
| Phase 3.1 result | next step |
|---|---|
| semantic valid, long carrier harmful | re-verify 2-3 edges with compact (short) oracle |
| length effect only | paper adds carrier ablation; redesign diagnostic history carrier |
| neither length nor semantic stable effect | stop pursuing verified edge; formally pivot to construction framework + feasibility study |

This step is load-bearing: the core claim is "the benchmark measures continual learning." Until
the Oracle History is minimal, equal-length, and controlled, 0 verified edges does NOT show the
graph formulation fails — only that the current intervention implementation is not yet a
construct-valid measurement.
