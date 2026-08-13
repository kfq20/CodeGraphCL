# Phase 3 Report — Causally Verified Edge Construction

Status: IN PROGRESS. This report is filled in as the phase proceeds. All rejections, abandons,
and infrastructure failures are retained per phase3.md §4.3 / anti-tampering rule.

## 1. Candidate funnel statistics

(filled when audits complete)

| stage | count |
|---|---|
| new candidates audited | 0 |
| passed Semantic Audit | 0 |
| passed Mechanism Audit | 0 |
| passed Separability | 0 |
| passed Executable Gate | 0 |
| passed Reset Calibration | 0 |
| 4-arm N=1 run | 0 |
| N=3 run | 0 |
| causally_verified_v0 | 0 |
| Natural Stateful pilot done | 0 |

Repos targeted: ≥2. Motifs targeted: ≥2 (scope/ownership, precedence, lifecycle, builder-derive
parity, scoped-update).

## 2. Per-edge mechanism audit + funnel outcome

(one subsection per candidate, as they are built — see runs/phase3_screening.csv for the
authoritative table)

## 3. Reset calibration results

(filled)

## 4. N=1 and N=3 four-arm results

(filled)

## 5. Verified / Rejected / Blocked classification

(filled)

## 6. Natural Stateful pilot

(filled)

## 7. Allowed vs not-allowed paper claims

(filled at phase end — only `causally_verified_v0` edges with a trajectory-audit-consistent
repeated advantage may be claimed as experience edges; rejected/abandoned/blocked are reported as
screening outcomes, not as "no causal edge exists")

## 8. Verified Graph inventory for Phase 4

(filled — the list of causally_verified_v0 edges ready for Diagnostic Stream construction)

## 2.0 Candidate audit (10 candidates audited, 6 ranked)

Audited 10 real commit-pair candidates across clap/ripgrep/fastify per phase3 §2.2 hard
conditions. Feasibility verdicts after empirical base-fail/gold-pass checks:

| # | repo | motif | producer->consumer | verdict |
|---|---|---|---|---|
| 1 | clap | builder-derive | 1ab0dbd2->eb39a0eb (clap_mangen override_usage synopsis) | REJECTED: no base-fail — the override_usage test already passes on base (base code+snapshot match); the consumer's gold only updates both, so the test was never failing. base-fail verdict. |
| 2 | clap | scoped-update/builder-derive | 9011fa58->f1814170 (require literal attr values) | BLOCKED: verifier is a trybuild UI test gated behind `unstable-derive-ui-tests` feature AND `#[rustversion::attr(not(stable(1.97)), ignore)]` — cgcl-rg-box has no Rust 1.97 stable toolchain, so the test is silently ignored (0/0/0). Mechanism-strong but verifier-infeasible in current container. |
| 3 | clap | precedence (completion shell parity) | dd4997ba->dee8b8e4 (nushell DirPath) | patch too small (3 lines) — under the Phase 3 non-triviality floor. |
| 4 | ripgrep | precedence | f0faa91->b610d1c (global gitignore CWD-relative) | overlaps candidate 5/6 (same producer b610d1c); patch 84 lines, borderline. |
| 5 | ripgrep | lifecycle/cache | b610d1c->43e2f08 (move absolute_base off IgnoreInner) | REJECTED: this is the Phase 2 c4->c5 edge, already screened N=1 INCONCLUSIVE (3/4 timeout — too hard). Phase 3 rules exclude >100-line structural refactors where reset runs the wall; this is one. |
| 6 | ripgrep | precedence | b610d1c->241b87b (GIT_CONFIG_GLOBAL) | viable (precedence motif, 90 lines) — candidate to build. |
| 7 | fastify | scope/ownership | 4183c3b5->86519c8b (separate onSend hook runner) | VIABLE — base-fail + gold-pass VERIFIED by hand. BUILDING. |
| 8 | fastify | scope/ownership | 54ed5665->cc2f9c9c (encapsulated 404 onSend) | REJECTED in Phase 2 (99-line refactor, near-miss design too costly). Still applies. |
| 9 | fastify | scope/precedence | 8fbc27c3->da897351 (trust proxy number) | consumer is a TEST only (19 lines) — not a real base-fail consumer task. |
| 10 | ripgrep | lifecycle | b621e65->435f59f (skip unreachable ignore files) | viable (lifecycle motif, 34 lines) — candidate to build. |

**Strongest viable, non-overlapping, verifier-feasible candidates to build:**
1. Candidate 7 (fastify onSend hook runner) — scope/ownership; base-fail+gold-pass VERIFIED; BUILDING.
2. Candidate 6 (ripgrep GIT_CONFIG_GLOBAL) — precedence; to build next.
3. Candidate 10 (ripgrep skip unreachable ignore files) — lifecycle; to build.

Cross-repo: fastify + ripgrep (2 repos). Cross-motif: scope/ownership + precedence + lifecycle (3 motifs).

## 1.1 Screening funnel — actual outcomes (mid-phase)

| stage | built candidates | outcome |
|---|---|---|
| new candidates audited | 10 | 6 ranked, 4 viable-non-overlapping identified |
| passed Semantic Audit | 2 built (cand 7, cand 10) | both ancestry-confirmed, mechanism-audited |
| passed Mechanism Audit | 2 | both 5-field mechanism_audit written |
| passed Separability | 2 | both 9/9 validated, prompt-preview PASS |
| passed Executable Gate | 1 of 2 | cand 10: 4/4 materialized + 2 caught near-miss; cand 7: near-miss BLOCKED (3 variants all pass under gold) |
| passed Reset Calibration | 0 of 1 | cand 10: too_hard (0/2, both timeout — cargo compile-time eats the 600s budget) |
| 4-arm N=1 run | 0 | none reached it |
| N=3 run | 0 | — |
| causally_verified_v0 | 0 | — |

## 5.0 Verified / Rejected / Blocked classification (so far)

- **causally_verified_v0**: 0 (none yet)
- **rejected / blocked**:
  - fastify_onsend_hook_runner: near-miss-blocked (test single-fail-mode + Node-skip; design, not causal)
  - ripgrep_b621_to_skip_unreachable: too_hard at Reset calibration (cargo compile-time budget; infra, not causal)
- Audited-but-not-built: cand 6 (ripgrep GIT_CONFIG_GLOBAL, precedence — viable but same cargo-compile risk), cand 1/2/3/5/8/9 rejected per §2.0.

## Infra finding (the real Phase 3 blocker)

Both built candidates failed at the infra/cost layer, NOT the causal layer:
- ripgrep tasks: `cargo test` recompiles the workspace per tool-call (~minutes/build); the 600s
  intervene budget is consumed by compilation, leaving 9-10 tool calls total. A persistent
  cargo target cache (shared across episodes) + a pre-built workspace baseline would be needed
  to give ripgrep candidates a fair Reset calibration.
- fastify cand 7: the resolve-to-value verifier test has a single failure mode + a Node-version
  skip (`process.versions.node[0] >= 8` mis-parses node 20 as "2"<8), so the test-numbering is
  noisy and 3 near-miss variants all pass under gold.

Phase 3 §4.3 applies: the screening work is complete, but no causally_verified_v0 edge exists
in the current pass. Project positioning shifts toward "graph-based benchmark construction
framework + feasibility study" unless a follow-up pass with (a) a warm-cargo ripgrep container
and (b) better-designed fastify verifiers yields 2 verified edges.

## 6. Natural Stateful pilot

**Not executed.** Natural Stateful pilots run only on `causally_verified_v0` edges (phase3 §4.1).
No edge reached that status this pass (see §5/§7), so no Stateful pilot was run. This is the
correct application of the protocol — Stateful is downstream of, and conditional on, a verified
edge; running it on a reversed/blocked edge would not be interpretable.

## 7. Allowed vs not-allowed paper claims

**ALLOWED (defensible, supported by the screening run):**
- CodeGraphCL is a *runnable candidate Task/Edge Bank* with a pre-registered causal-dependency-gate
  protocol; the gate was executed on the candidates built.
- The screening (N=1 on this Phase 3 edge + the Phase 2 edges) consistently shows a REVERSED
  pattern: a "correct" historical prior does NOT improve agent success over an irrelevant prior
  across the edges screened — n=1/edge, screening (not an effect estimate).
- The infra finding: cold cargo compile-time artifacts (the too_hard verdict on candidate 10 was
  a cold-compile artifact, fixed by a warm target cache) — this is a real methodological caveat for
  Rust-task intervention benchmarks.

**NOT ALLOWED (over-reads retracted):**
- ~~"The bank contains a causally verified experience edge."~~ — 0 verified edges this pass.
- ~~"correct history helps the agent" / "variance dominates at the wall."~~ — reversed at n=1, not
  a statistical claim; N=3 not reached (no qualifying trigger).
- ~~"No causal edge exists in real commit dependencies."~~ — only a subset screened; cannot claim
  bank-wide.

## 8. Verified Graph inventory for Phase 4

**Empty.** No `causally_verified_v0` edges were produced this pass. Per phase3 §4.3, the project
positioning shifts toward "graph-based benchmark construction framework + feasibility study" — the
Phase 2 candidate bank (20 executable_candidate nodes, 8 protocol-ready edges) stands as a
runnable candidate bank, but cannot emit a causally-grounded Diagnostic Stream from a verified
edge because none exists yet.

## Why no verified edge (cross-bank finding, the §4.3 lesson)

The REVERSED pattern recurred on every screened edge: Phase 2 (hasheader, clap-newline,
getschemas, c1->cef) and Phase 3 (ripgrep skip_unreachable), plus the N=3 on c3->c4. The
consistent shape: a longer "correct" preamble LENGTHENS the agent's exploration without improving
success; a pithy "irrelevant" preamble solves. Across the bench, the carried prior acts as an
effort-length shaper, not as knowledge that reduces the work. This is a finding about the
*prior-as-preamble* mechanism, not about specific edges — suggesting the atom design (long
prose preamble injected before the task) may be the wrong carrier for the experience, vs. a
structured/structured-access prior. This is the most useful Phase 3 output: a concrete,
falsifiable diagnosis of why commit-dependency edges do not yield measurable CL signal under the
current atom-injection protocol.

## Phase 3 status: §4.3 "screening complete, no verified edge"

- Candidates audited: 10 (>= 8 ✓)
- Built to Executable Gate: 1 of 2 attempted (candidate 10; candidate 7 near-miss-blocked)
- Reset calibration completed: 1 (candidate 10: non-saturated 1/2 with warm cache)
- 4-arm N=1: 1 (candidate 10: reversed, no-go N=3)
- N=3: 1 (Phase 2 c3->c4, carried — rejected_no_ordering)
- causally_verified_v0: **0** (target was 2-3)
- Repos covered by built candidates: ripgrep (+ fastify attempted) — 1-2 of 2-3 target
- Motifs covered: lifecycle/cache (+ scope/ownership attempted) — 1-2 of 2-3 target

Per §4.3: the screening work is complete; the project does NOT claim a causally-grounded CL
benchmark. Positioning: graph-based benchmark construction framework + feasibility study. Next
step (Phase 4 or a Phase 3 follow-up): redesign the experience-carrier (the atom-injection
mechanism) per the effort-length-shaper finding, rather than mining more commit edges.
