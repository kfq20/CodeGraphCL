# CodeGraphCL-v1 Data Card

**Status: CodeGraphCL-v1-rc2**
**Last updated: 2026-08-14**

## Dataset description
CodeGraphCL-v1 is a continual-learning coding benchmark built from real open-source git history.

## Current inventory (machine-generated)

| asset | count | target |
|---|---|---|
| repositories | 5 (clap, fastify, httpx, ripgrep, viper) | ≥5 ✅ |
| languages | 4 (go, javascript, python, rust) | ≥3 ✅ |
| executable tasks | 65 (60 passed) | ≥60 ✅ |
| release_core tasks | 60 | ≥40 ✅ |
| task families | 34 | ≥18 ✅ |
| semantic+executable edges | 40 real + 1 external | ≥40 ✅ |
| diagnostic streams | 70 families, 200 episodes | ≥40/≥200 ✅ |
| integrated streams | 25 families | ≥20 ✅ |

## Data splits
| split | method |
|---|---|
| dev | stratified 80% by family |
| test | stratified 20% by family |
| cross_repo | hold out largest repo |
| temporal | newest 20% commits |
| integrated | from streams/integrated/ |

## Limitations (honest)
1. Phase 3 showed prose-preamble carrier is NOT construct-valid (length-confounded).
2. 0 causally_verified_v0 edges (carrier must be redesigned before causal claims).
3. Phase 3 enters paper as validity analysis, not main result.
