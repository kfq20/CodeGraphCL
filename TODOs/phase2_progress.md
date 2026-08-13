# Phase 2 Progress (updated 2026-08-13)

## Done
- protocol-v1 Quality Lock (5 fixes) + tag `protocol-v1` (a27e53c)
- ripgrep_c3: protocol-v1 COMPLETE (4/4 gates + 2 near-miss caught) — re-verifying with host-inject fix
- ripgrep_c4: protocol-v1 COMPLETE (4/4 gates + 2 near-miss caught, mat_c4_ql2)
- host-side near-miss inject fix (rust:slim has no python3 — .py inject now runs on host)
- fastify decorator family staged: instruction + atoms + patches + test.sh + 2 near-miss
  - base-fail VERIFIED (tap fails on cef base)
  - gold-pass VERIFIED (tap passes after cef source)
  - npm install works (538 packages, DinD-slow but done)
  - materialize via unified CLI: running
- clap derive-api segment audited: 7c10b5a9b4 (derive default_value_os parity) candidate

## In progress
- c3 re-materialize (host-inject fix verification)
- fastify materialize (npm install + tap + near-miss)

## Phase 2 target vs current
| asset | target | current |
|---|---|---|
| repos | >=3 | 3 (ripgrep+httpx+fastify) ✓ |
| families | 6-8 | 3 (ripgrep_ignore_path, httpx_start_tls, fastify_decorator) |
| executable nodes (protocol-v1) | 20-30 | 2 (c3+c4) + fastify pending |
| semantic edges | 10-15 | 5 |
| intervention-ready | >=8 | 3 |

## Candidate families for batch production (remaining)
1. clap derive-api (7c10b5a9b4): derive default_value_os parity. Rust, reuses ripgrep image.
2. clap builder-api (129 commits): deprecation/update chain.
3. fastify content-type (22 commits): contentTypeParser scope.
4. fastify errors (22 commits): error scope/parity.
5. ripgrep c5/c6: extend ignore_path family (global gitignore + GIT_CONFIG_GLOBAL).
6. ripgrep matcher/output-printer: different invariants.

## Known issues
- fastify near-miss anchors expect gold-applied code (base has no Object.defineProperty);
  materialize near-miss runs on base+verifier — needs 'gold+near-miss' mode. TODO.
- httpx_tB near-miss: patch malformed (hand-written). Needs conversion to .py injector.
- DinD: npm/apt/pip slow under nested docker. cargo OK (crates.io cache persists).
