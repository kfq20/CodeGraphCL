# Phase 2 Progress (2026-08-13)

## Done
- protocol-v1 Quality Lock (5 fixes) + tag `protocol-v1` (a27e53c)
- ripgrep_c3: protocol-v1 COMPLETE (4/4 gates + 2 near-miss caught)
- fastify decorator Update chain identified: c1aac3cd85 (add getter/setter to decorate)
  -> cef8814ea1 (propagate to decorateReply/decorateRequest). Parity motif, clean SWE-bench split.

## In progress
- ripgrep_c4: 2 near-miss (overstrip guard + noguard) materialize running
- httpx_tB: needs 2nd near-miss + patch format fix

## Phase 2 target vs current
| asset | target | current |
|---|---|---|
| repos | >=3 | 2 (ripgrep+httpx) |
| families | 6-8 | 2 |
| executable nodes (protocol-v1) | 20-30 | 1 (c3) |
| semantic edges | 10-15 | 4 |
| intervention-ready | >=8 | 3 |

## Candidate families for batch production
1. **fastify decorator** (c1aac3cd85->cef8814ea1): getter/setter parity. Needs node image.
2. **fastify content-type** (22 commits, test anchor): contentTypeParser scope.
3. **fastify errors** (22 commits): error scope/parity.
4. **clap builder/derive** (builder-api + derive-api segments): parity + deprecation update.
5. **ripgrep c5/c6** (global gitignore + GIT_CONFIG_GLOBAL): extend the ignore_path family.
6. **ripgrep more segments** (matcher, output-printer): different invariants.

## Stop-loss per family
- semantic audit: 2h max
- env/verifier: 0.5d max
- instruction leak -> reject
- N=1 saturated -> stop
