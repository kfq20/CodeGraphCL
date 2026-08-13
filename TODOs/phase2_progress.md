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

## Executable nodes (executable_gate: passed) — 12 total
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

(httpx_tA/tB/tC are rejected causal tasks — kept as negative-transfer/rejected analysis.)

## Phase 2 target vs current
| asset | target | current |
|---|---|---|
| repos | >=3 | 3 (ripgrep+fastify+clap) ✓ |
| families | 6-8 | **7 active** (ripgrep_ignore_path, fastify_decorator, fastify_contenttype, fastify_reply_api, fastify_schemas, clap_derive_api, +httpx rejected) — **TARGET MET** ✓ |
| executable nodes | 20-30 | 12 |
| semantic edges | 10-15 | 6 (c2->c3, c3->c4, c4->c5, c1->cef, +2 clap single-node) |
| intervention-ready | >=8 | 4 (c2->c3, c3->c4, c4->c5, c1->cef) |
| N=1 run | 4-6 sensitive | c4->c5 INCONCLUSIVE (too hard); c3->c4 reset-solvable (cost-metric only) |

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

## Next
- **c5 N=1 INCONCLUSIVE** (3/4 timeout_failed, wrong arm fluke-solved) — c5 too hard for clean
  N=1 read (agent times out regardless of prior). NOT escalating to N=3. Retarget to easier
  revision edge: c3->c4 (smaller `.`-dir refactor) or fastify parity, where reset solves <300s
  so the edge measures experience COST not feasibility.
