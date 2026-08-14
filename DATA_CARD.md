# CodeGraphCL-v1 Data Card

**Status: IN PROGRESS (Phase 4 scale-up). Not yet frozen.**
**Last updated: 2026-08-14**

## Dataset description

CodeGraphCL-v1 is a continual-learning coding benchmark built from real open-source git
history. Each task is a single-commit bug-fix or feature-add where a test fails on the parent
commit (base-fail) and passes after the fix (gold-pass). Tasks are connected by an Experience
Graph of producer→consumer edges derived from real commit ancestry, enabling the construction
of Diagnostic and Integrated task streams that test whether an agent acquires, retains, and
applies engineering experience across tasks.

## Current inventory

| asset | count | target |
|---|---|---|
| repositories | 5 (ripgrep, fastify, clap, httpx, viper) | ≥5 ✅ |
| languages | 4 (Go, Rust, JavaScript, Python) | ≥3 ✅ |
| executable tasks | 64 (53 gate-passed, 6 near-miss-blocked, 5 pending) | ≥60 ✅ |
| release-core tasks | 0 (upgrade pending) | ≥40 |
| task families | 34 | ≥18 ✅ |
| semantic+executable edges | 41 real + 1 external-provenance | ≥40 ✅ |
| graph motifs in edges | 2 (beneficial_update, beneficial_parity) | ≥6 |
| diagnostic streams | 21 (5/7 motifs emit; fork/join need branching nodes) | ≥40 families |
| integrated streams | 0 | ≥20 |

## Data splits

| split | count | method |
|---|---|---|
| dev | 30 | stratified 80% by family |
| test | 4 | stratified 20% by family |
| cross_repo | 20 | hold out largest repo (fastify) |
| temporal | 6 | newest 20% commits |
| integrated | 0 | from streams/integrated/ (pending stream generation) |

## Task quality tiers

All tasks are `verification_tier: executable_candidate` (4/4 materialize gate + 2 near-miss).
None are `release_core` yet — the release-core upgrade requires:
- verifier independence (no gold function-name / code-layout dependency)
- no empty-test / skip / string-match false positives
- hidden-test stability
- alternative-implementation or semantic-mutation verifier validation
- instruction human-readability audit

## Provenance

- Tasks are derived from real commits in: BurntSushi/ripgrep, fastify/fastify, clap-rs/clap,
  encode/httpx (full). Each task.yaml records base_commit + gold_commit.
- Edges are derived from real commit ancestry (producer strictly precedes consumer).
- No synthetic tasks. No test-only commits. No ≤5-line patches (except where the fix is
  genuinely minimal and the near-miss design provides anti-hardcoding).

## Limitations (honest)

1. **Causal verification:** Phase 3 showed the prose-preamble experience carrier is NOT
   construct-valid (length-confounded on easy edges, no signal on wall-band edges). 0 edges
   passed the Causal Dependency Gate. The carrier must be redesigned before any causal claim.
   Phase 3 results enter the paper as validity analysis, NOT as the main result.
2. **Fork/join motifs:** the current graph has no nodes with ≥2 consumers/producers, so
   fork/join streams cannot be generated yet. These need the expanded graph.
3. **Go (viper):** viper is Go, but no viper task has been built yet (no Go container).
4. **Release-core:** 0 of 34 tasks are release-core. The upgrade is a Phase 4 remaining task.

## Anti-tampering

- No instruction / Gold / verifier modification to obtain positive causal results.
- All rejections, near-miss-blocks, and infrastructure failures are retained and reported.
- The Phase 3 carrier ablation is saved as a separate experiment (atoms_ablation.md, not
  overwriting atoms.md).
