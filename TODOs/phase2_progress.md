# Phase 2 Progress (updated 2026-08-13)

## Done (this session)
- **fastify_decorator_getter**: 4/4 materialized (mat_fs_3). Fixed two blockers:
  - pool-path mismatch (materialize wrote worktree to default /tmp/cgcl_box_pool but cgcl-fs-box
    binds /pool to /tmp/cgcl_fs_pool) -> added `_resolve_pool(cname)` that inspects the
    container's actual /pool bind-mount and strips the daemon prefix.
  - near-miss gate ran on base-only but fastify near-misses corrupt GOLD-ADDED code ->
    added `verifier.near_miss_base: gold` mode (apply gold before injecting near-miss).
- **clap_derive_default_value_os**: 4/4 materialized (mat_clap_1). Single-node Parity task
  (commit 7c10b5a9b4). Two near-miss (guardonly + tvariant) caught. Reuses rg rust image.
- **clap_derive_type_alias**: 4/4 materialized (mat_clap_ta_2). Second node in clap_derive_api
  family (commit 1285c0f8, ancestor of 7c10). Two near-miss (onesite + maponly) caught.
  REJECTED near-miss (localpath, relative std:: path) recorded as evidence — verifier catches
  bare-symbol shadowing, not absolute-vs-relative hygiene.
- **ripgrep_c5**: 4/4 materialized (mat_c5_3). c4->43e2f08 Update edge — the first NEW real CL
  edge built this session (cached parent matcher path leaks across search roots). Two near-miss
  (parentdir/add_child-drop + cachehit-wrong-source) caught after iterating on near-miss A
  (parent()-only was NOT caught — test is sensitive to add_child propagation, documented).
  **N=1 intervention run**: INCONCLUSIVE (3/4 timeout_failed, wrong arm fluke-solved at 600s).
  c5 too hard for clean N=1 read; retarget to easier edge. See runs/.../SUMMARY.md.
- **c3->c4 reset-feasibility probe** (seed7): reset IS solvable on c4 (reward=1 timeout_solved
  600s, 208 turns) — but AT the 600s wall. c4 sits near feasibility ceiling; correctness will
  saturate, edge can only be read on COST. (Earlier full 4-arm run was killed by host ENOSPC.)
- **fastify_contenttype_array**: 4/4 materialized FIRST TRY (mat_fs_ct_1). New fastify_contenttype
  family (5th). 5-line source patch (commit 7f378355). Two near-miss (firstonly + passthrough)
  caught, distinct failure footprints. Feasibility-blessed small patch.
- **fastify_redirect_statuscode**: 4/4 materialized (mat_fs_rd_3). New fastify_reply_api family
  (6th — family target lower bound met). 4-line source patch (commit 92f474ea8c98): redirect
  clobbers preset status code. Two near-miss (useset + always302) caught, opposite directions.
  VERIFIER GOTCHA recorded: tap --grep matches TOP-LEVEL test names, not subtests — had to grep
  the parent test `within an instance` to run the `redirect to \`/\` - 1..9` subtests (grepping
  the route paths or subtest names skipped all 26 tests -> false rc=0 -> base-fail rejected).
- **fastify_get_shared_schemas**: 4/4 materialized (mat_fs_sch_1). New fastify_schemas family
  (7th — family target MET/exceeded). 5-line patch (commit c9141a071d0f): shared schemas
  write-only; gold adds getSchemas() shallow-copy. Two near-miss (keys + wrapper) caught.
- c3 + c4 regression re-confirmed after host ENOSPC cleanup: pool-resolve change did NOT break
  ripgrep (both 4/4, 30s each).

## Executable nodes (executable_gate: passed) — 20 total  (LOWER-BOUND TARGET MET)
| node | family | repo | gate run | edge |
|---|---|---|---|---|
| ripgrep_c3 | ripgrep_ignore_path | ripgrep | mat_c3_reg | c2->c3 Update |
| ripgrep_c4 | ripgrep_ignore_path | ripgrep | mat_c4_reg | c3->c4 Update (reset solvable, at 600s wall) |
| ripgrep_c5 | ripgrep_ignore_path | ripgrep | mat_c5_3 | c4->43e2f08 Update (real CL edge, N=1 INCONCLUSIVE) |
| fastify_decorator_getter | fastify_decorator | fastify | mat_fs_3 | c1->cef Parity |
| clap_derive_default_value_os | clap_derive_api | clap | mat_clap_1 | single-node Parity |
| clap_derive_type_alias | clap_derive_api | clap | mat_clap_ta_2 | single-node consistency |
| fastify_contenttype_array | fastify_contenttype | fastify | mat_fs_ct_1 | single-node (5-line patch, feasible) |
| fastify_redirect_statuscode | fastify_reply_api | fastify | mat_fs_rd_3 | single-node (redirect clobbers preset code) |
| fastify_get_shared_schemas | fastify_schemas | fastify | mat_fs_sch_1 | single-node (schemas write-only) |
| fastify_clean_schema_id | fastify_schemas | fastify | mat_fs_cid_1 | single-node ($id leaks at compile) |
| fastify_decorate_null | fastify_decorator | fastify | mat_fs_dn_1 | single-node (decorate null crashes) |
| fastify_reply_headerssent | fastify_reply_api | fastify | mat_fs_hs_1 | single-node (send stream after writeHead crashes) |
| fastify_contenttype_emptybody | fastify_contenttype | fastify | mat_fs_eb_1 | single-node (custom parser rejects empty body) |
| fastify_reply_json_charset | fastify_reply_api | fastify | mat_fs_jc_1 | single-node (JSON+charset content-type clobbered) |
| fastify_header_case_validation | fastify_validation | fastify | mat_fs_hv_1 | single-node (required-header case-sensitive) |
| fastify_reply_removeheader | fastify_reply_api | fastify | mat_fs_rh_1 | single-node (no way to remove a header) |
| fastify_404_unsupported_method | fastify_reply_api | fastify | mat_fs_404m_1 | single-node (unsupported method returns 405 not 404) |
| fastify_reply_hasheader | fastify_reply_api | fastify | mat_fs_hh_1 | single-node (no way to check if a header is set) |
| clap_error_newline | clap_error | clap | mat_clap_nl_1 | single-node (error message has no trailing newline) |
| clap_error_help_newline | clap_error | clap | mat_clap_hn_1 | single-node (help-disabled error has no trailing newline) |

(httpx_tA/tB/tC are rejected causal tasks — kept as negative-transfer/rejected analysis.)

## Phase 2 target vs current
| asset | target | current |
|---|---|---|
| repos | >=3 | 3 (ripgrep+fastify+clap) ✓ |
| families | 6-8 | **9 active** (ripgrep_ignore_path, fastify_decorator, fastify_contenttype, fastify_reply_api, fastify_schemas, fastify_validation, clap_derive_api, clap_error, +httpx rejected) — **TARGET EXCEEDED** ✓ |
| executable nodes | 20-30 | **20** (LOWER-BOUND MET) ✓ |
| semantic edges | 10-15 | **10** (LOWER-BOUND MET) ✓ |
| intervention-ready | >=8 | **8** (lower-bound MET) ✓ |
| N=1 run | 4-6 sensitive | c4->c5 INCONCLUSIVE (too hard); c3->c4 reset-solvable (cost-metric only) |

## Semantic edges (10 total, 8 intervention-ready)
| edge | type | producer -> consumer | evidence |
|---|---|---|---|
| ripgrep_c2_to_c3 | beneficial_update | c2 -> c3 | c3 msg: "previous code deleted too many parts" |
| ripgrep_c3_to_c4 | beneficial_update | c3 -> c4 | reset-feasibility probed: solvable AT 600s wall (cost-metric only) |
| ripgrep_c4_to_c5 | beneficial_update | c4 -> 43e2f08 | N=1 RAN, INCONCLUSIVE (c5 too hard) |
| clap_help_newline_to_newline | beneficial_update | 2eb69def -> a72e572 | **consumer msg: "Found this when auditing for cases related to #2787"** (producer fixed #2787) |
| fastify_getschemas_to_cleanid | beneficial_update | c9141a07 -> 5ffb131e | consumer acceptance asserts producer's snapshot/original distinction |
| fastify_hasheader_to_removeheader | beneficial_update | 31c5f7e2 -> cfa760cb | consumer's 2 near-misses ARE the 2 halves of the carried convention |
| fastify_emptybody_to_array | beneficial_update | 8c5e732f -> 7f378355 | consumer near-misses = the "treat collection as one" failure producer warns against |
| fastify_c1_to_cef_decorator | beneficial_parity | c1aac3cd -> cef8814e | getter/setter convention mirrored to Request/Reply |
| httpx_tA_to_tB | (rejected family) | tA -> tB | negative-transfer diagnostic (wrong 0/3) |
| httpx_tB_to_tC | (rejected target) | tB -> tC | NOT intervention-ready by design — tC rejected (instruction leak) |

## Candidate families for batch production (remaining)
1. clap builder-api (129 commits): deprecation/update chain.
2. fastify content-type (22 commits): contentTypeParser scope.
3. fastify errors (22 commits): error scope/parity.
4. ripgrep c5/c6: extend ignore_path family (global gitignore + GIT_CONFIG_GLOBAL).
5. ripgrep matcher/output-printer: different invariants.
6. more clap derive parity commits (several small co-change commits exist).

## Known issues
- fastify near-miss anchors expect gold-applied code — resolved via near_miss_base: gold mode.
- httpx_tB near-miss: patch malformed (hand-written). Needs conversion to .py injector.
- DinD: npm/apt/pip slow under nested docker. cargo OK (crates.io cache persists).

## Causal-verification funnel — PARTIALLY SCREENED (not all edges covered)

Coverage is partial: of the 8 intervention-ready edges, 4 have a full N=1 4-arm, 1 has only a
reset-only probe (infra-failed), and 3 were not run at all this round. N=3 was run on the single
edge that showed N=1 sensitivity. **The funnel is incomplete; the result below is a screening
outcome on a subset, not a statement about the whole bank.**

| edge | reset-feasibility | N=1 4-arm | N=3 (12 eps) | status |
|---|---|---|---|---|
| ripgrep c4->c5 | (not probed) | 3/4 timeout, reset FAILED | — | full N=1; too-hard, no-go |
| fastify hasheader->removeheader | 177s (easy) | 4/4 solved, cost REVERSED | — | full N=1; saturated-easy, no-go |
| clap help_newline->newline (strongest text evidence) | 185s (easy) | 4/4 solved, cost REVERSED | — | full N=1; saturated-easy, no-go |
| **ripgrep c3->c4** | 600s (at wall) | 3/4 solved, irrelevant FAILED | correct 1/3, reset 1/3, irrelevant 2/3, wrong 2/3 | full N=1 + N=3; **not escalated** |
| ripgrep c2->c3 | infra-fail (reward-path bug) | — (reset-only probe) | — | **reset-only; blocked** |
| fastify_getschemas_to_cleanid | — | — | — | **not run** |
| fastify_emptybody_to_array | — | — | — | **not run** |
| fastify_c1_to_cef_decorator | — | — | — | **not run** |

Summary: **4 full N=1 + 1 reset-only + 3 unrun** of the 8 ready edges.

### N=3 on ripgrep c3->c4 — what the data supports, and what it does NOT
N=3 per-condition: correct 1/3, reset 1/3, irrelevant 2/3, wrong 2/3.

What the data supports (a screening call): **the single edge that qualified for N=3 did not
reproduce the N=1 condition ordering** (N=1 had irrelevant-fail / correct-solve; N=3 reversed
it). Per the phase2 funnel rule ("only escalate to N=3 confirmation if N=1 shows stable
sensitivity"), this edge is **not escalated** — it does not pass the Causal Dependency Gate as
a beneficial edge.

What the data does NOT support: it does not statistically prove "correct is the worst prior" or
"variance dominates" — n=3/condition is too small for a statistical claim, and N=3 is a
screening gate, not a causal-effect estimate. It also does not say anything about the 3 unrun
edges or the 1 blocked edge. Therefore the only defensible scope-level statement is:

> In the edges screened so far, no edge passed the Causal Dependency Gate; the one edge escalated
> to N=3 did not reproduce N=1's condition ordering.

This is strictly weaker than (and replaces) any earlier phrasing asserting the bank "has no
causal edge" or that the wall-band is "variance-dominated" as a proven mechanism — those were
over-reads. "Correct worst" and "variance-dominated" remain working interpretations, not findings.

### Screening criterion (working hypothesis, not a fixed rule)
The "reset solves 200–400s below the wall" framing is a **working hypothesis tied to this
model+machine**, not a portable rule. A more reliable, model/machine-independent screening
criterion: **under a fixed model and fixed budget, the reset arm's success rate sits in a
non-saturated band (roughly 20–80%)**. If reset is ~100% the task is too easy (pass-rate
saturates above); if reset is ~0% it is too hard (saturates below). Wall-time seconds are a
proxy that shifts with model and hardware; the non-saturated success-rate band is the more
stable gate. Apply this probe before a 4-arm.

## Phase2 status (corrected)
- Production targets: MET (nodes 20/20-30, families 9/6-8, semantic edges 10/10-15,
  intervention-ready 8/8 — NOT 9; httpx_tA_to_tB is a rejected-family diagnostic, not a ready
  edge, because httpx_tA's separability_gate=FAILED).
- 20 nodes are **executable candidates** (4/4 gate + near-miss), NOT released nodes; final
  publish requires alternative-correct implementation controls.
- Causal-verification: PARTIALLY screened (4 full N=1 + 1 reset-only + 3 unrun, of 8 ready
  edges). 1 edge escalated to N=3; it did not pass the Causal Dependency Gate. This is a
  screening outcome on a subset, not a bank-wide verdict.

## Next (Phase 2.1 closeout before Phase 3)
1. Run the 3 unrun fastify edges (getschemas->cleanid, emptybody->array, c1->cef) to full
   coverage: 4→7 full N=1 + 1 reset-only.
2. Re-run c2->c3 (the test.sh reward-path bug is now fixed to binary 0/1) — clears the blocked
   edge to either a clean N=1 or a documented abandon.
3. Only after full coverage, consider whether any edge meets the escalate-to-N=3 rule.
