# CodeGraphCL-v1 Benchmark Report

**Status: IN PROGRESS (Phase 4 scale-up). Not yet frozen as CodeGraphCL-v1-rc1.**
**Last updated: 2026-08-14**

Run `python3 -m codegraphcl validate-benchmark` for the latest counts.

## 1. Benchmark statistics

| asset | count | target | status |
|---|---|---|---|
| repositories | 4 | ≥5 | need 1 more (viper Go, or another) |
| languages | 3 (Rust, JS, Python) | ≥3 | ✓ (Go pending via viper) |
| executable tasks | 34 (28 passed, 3 near-miss-blocked, 3 pending) | ≥60 | 26 more needed |
| release-core tasks | 0 | ≥40 | upgrade pending |
| task families | 13 | ≥18 | 5 more needed |
| semantic+executable edges | 10 real + 1 external | ≥40 | 29 more needed |
| graph motifs | 2 (update, parity) | ≥6 | 4 more needed |
| diagnostic streams | 21 (5/7 motifs emit) | ≥40 families | fork/join need branching nodes |
| integrated streams | 0 | ≥20 families | pending stream generation |
| intervention-audit subset | 10 (Phase 2+3 screened) | ≥10 | ✓ |

## 2. Executable / release-core ratio

- 28/34 tasks pass executable_gate (4/4 materialize + 2 caught near-miss)
- 3/34 near-miss-blocked (base-fail verified, near-miss design needs rework)
- 0/34 release-core (verifier-independence + alt-impl + hidden-test-stability upgrade pending)

## 3. Graph structure

- 10 real edges + 1 external-provenance (b621e65→skip_unreachable, external commit)
- No self-loops (all from/to resolve to distinct Task Nodes)
- Max graph degree: 1 (each node has at most 1 producer / 1 consumer — no fork/join yet)
- Dependency distance: max 3 (ripgrep c2→c3→c4→c5 chain)
- Parent count: 1 per node (no multi-parent joins)

## 4. Diagnostic / Integrated stream distribution

- 5/7 motifs emit on the current graph: direct(5), delayed(3), scope(5), update(3), hard_negative(5)
- fork/join: 0 (need branching nodes — the graph is a set of linear chains)
- Integrated streams: 0 (pending — need integrated stream generation after graph expansion)

## 5. Rejected and infrastructure-blocked

- Rejected (Phase 2-3): httpx_tA (instruction leak), httpx_tC (instruction leak), clap 404-encapsulated
  (99-line refactor), clap 404-error-headers (no base-fail), clap nushell DirPath (3-line, too small),
  fastify trust-proxy (test-only consumer)
- Near-miss-blocked: clap_conflict_usage (base-fail verified, near-miss needs rework)
- Infrastructure-blocked: clap require-literal-attr (needs Rust 1.97+ trybuild)

## 6. Intervention audit coverage

Phase 2-3 screened 8 ready edges + 1 N=3 (c3→c4). Result: 0 causally_verified_v0. Phase 3.1
carrier ablation (5-condition N=3 on 2 edges) showed the prose-preamble carrier is NOT
construct-valid (length-confounded on easy edges, no signal on wall-band edges). The carrier
must be redesigned. Phase 3 enters the paper as validity analysis, not the main result.

## 7. Smoke test

**Not yet run.** Phase 4 Task 7 requires all formal tasks re-materialized + graph/stream static
validation + ≥10% diagnostic families sampled + 5 integrated streams end-to-end with one fixed
model (Reset vs Native Stateful). Infrastructure success rate target: ≥95%. Pending the
graph/task expansion to sufficient size.

## 8. Data splits and dedup

- dev: 30, test: 4 (stratified by family, 80/20)
- cross_repo: 20 (fastify held out)
- temporal: 6 (newest 20% commits)
- integrated: 0 (pending stream generation)
- Family-level constraint checked (no family crosses dev/test)
- SWE-bench dedup: not yet run (pending)

## 9. Phase 5 experiment matrix (planned)

| dimension | method |
|---|---|
| Reset vs Native Stateful | main comparison (one fixed model) |
| Motif | direct/delayed/fork/join/scope/update/hard_negative |
| Dependency distance | 1/2/3+ |
| Parent count | 1/2+ |
| Negative transfer | stale/wrong-history variant |
| Cross-repo generalization | cross_repo split |
| Diagnostic–Integrated correlation | stream-level |

## 10. Allowed vs not-allowed claims

ALLOWED:
- CodeGraphCL is a runnable candidate Task/Edge Bank with a pre-registered causal-dependency-gate
  protocol, motif-aware stream generator, and data splits.
- The Phase 3 carrier ablation is a construct-validity contribution (the prose-preamble carrier is
  length-confounded / signal-free).

NOT ALLOWED:
- "The benchmark measures continual learning" — the carrier is not construct-valid; 0 verified edges.
- "The graph formulation fails" — the 0-verified result is carrier-confounded, not a graph verdict.
- Any causal claim from the Phase 3 N=1/N=3 screening (n too small, carrier not construct-valid).
