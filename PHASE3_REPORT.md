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
