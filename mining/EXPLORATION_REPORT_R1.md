# Exploration Report R1 — CodeGraphCL premise recon

> **Status:** Reconnaissance only. Metadata-level findings, NOT verified causal edges.
> All motif labels below are *hypotheses for hand-audit*, not claims. Aligns with the
> proposal's L0–L4 evidence ladder: this is L1–L2 (observed co-change), nothing here is L5
> (causally verified).
>
> **Date:** 2026-08-12  ·  **Scope:** 5 repos (httpx, viper, fastify, clap, ripgrep)
>  ·  **Outputs:** `mining/out/*.jsonl`  ·  **Scripts:** `cochange_miner.py`, `motif_segments.py`

## What this round set out to test

`docs/ref_codebase.md` makes a load-bearing premise:

> These mid-size infra repos *naturally* produce repeated cross-cutting constraints
> (sync/async parity, config precedence, plugin scope, dual-API surface) that recur
> across many commits/modules/versions — and therefore grow Fork / Join / Scope / Update /
> Hard-negative experience edges on their own, without us inventing them.

If that premise is false, the entire commit→task→edge pipeline is built on sand. So R1
asks the cheapest possible question: **does the raw commit history actually contain enough
co-change (source + test changing together, repeatedly, on the same files) to plausibly
seed motifs?** We do NOT yet claim to identify which motif — only whether the raw material
is there.

## Method (two-pass, no embeddings, fully auditable)

1. **`cochange_miner.py`** — for every non-merge commit, list changed files, classify each
   as src/test/ignore via per-repo rules (`repo_config.py`), keep only commits that change
   **source AND test together** (co-change = the behavior-under-test was modified). Cluster
   coarsely by primary subsystem. Output: `<repo>.commits.jsonl` + `<repo>.clusters.jsonl`.
2. **`motif_segments.py`** — within each coarse cluster, drop noise commits
   (formatter/linter/bump/changelog — counted, not hidden), build a file-set fingerprint per
   commit, connect commits whose fingerprints share ≥34% Jaccard, take connected components
   as "segments". A segment is **motif-grade** iff ≥3 commits, ≥30d span, ≥2 files.
   Output: `<repo>.segments.jsonl`.

**Honest limits, by design:** file-level fingerprints resolve motifs inside one big
module file poorly (see viper below). Motif *identity* (Fork vs Join vs Update) is a semantic
judgment a script cannot make from metadata — every segment below is a *read-this* queue
entry, not a labeled edge.

## Headline numbers

| repo | lang | co-change commits | coarse clusters | **motif-grade segments** |
|---|---|---:|---:|---:|
| httpx | py | 382 | 11 | **16** |
| viper | go | 158 | 3 | **3** ⚠ |
| fastify | js | 988 | 14 | **35** |
| clap | rs | 887 | 10 | **44** |
| ripgrep | rs | 54 | 6 | **4** |
| **total** | | **2469** | | **102** |

**Read:** the premise survives. 102 motif-grade segments across 5 repos, each anchored to a
concrete (source-file, test-file) pair that a human can read in one sitting. The signal is
not uniform — it is strong for multi-file-module languages (py/js/rs) and weak for Go's
single-big-file style. That asymmetry is a real finding, not a bug.

## Per-repo finding

### httpx (16 segments) — flagship motifs present
- `client-api` (169 co-change commits) is the sync/async parity invariant: `httpx/_client.py`
  carries both `Client` and `AsyncClient`. This is a textbook **Fork** embryo (one source
  invariant, two surfaces that must stay equal).
- `transport` + `auth` + `config-ssl` cluster together ⇒ **Join** candidate (transport is
  the sink where proxy/redirect/ssl/auth all funnel).
- 29/169 `client-api` commits use deprecate/migrate/remove language ⇒ **Update** chain
  candidate (API surface revised over time).
→ *Premise confirmed and richest here, as ref_codebase predicted (A+).*

### fastify (35 segments) — most segments, but noisiest
- `plugin-scope` only 9 commits but is the executable **Scope** oracle (encapsulation
  boundary). Quality over quantity.
- `schema` (17 commits, core=`lib/schemas.js + lib/validation.js`) ⇒ **Update** candidate.
- `hook-lifecycle` + `decorator` ⇒ **Join** candidate.
- ⚠ `type-parity` (127 commits) and `fastify.js` segments have 1-file cores — likely
  "types file touched by every feature", not a single invariant. **Flag for filtering in R2.**

### clap (44 segments) — richest Fork/Update ground
- `builder-api` (129) + `derive-api` (18, core=`clap_derive/src/derives/args.rs`) ⇒ the
  flagship **Fork**: builder and derive must expose the same surface.
- `completion` splits into two segments (engine vs dynamic) ⇒ natural **Scope** test
  (same principle, different completion subsystem).
- Heavy deprecation language ⇒ **Update** chains are real and numerous.
→ *Best repo for Fork + Update motifs; ref_codebase's "A" rating holds.*

### ripgrep (4 segments) — small but clean
- `ignore-precedence` (6 commits, core=`dir.rs + gitignore.rs + tests/regression.rs`) ⇒
  the gitignore precedence **Scope + Update** invariant. Tiny, sharp, exactly as predicted.
→ *Phase-0 infra role validated: cheap to verify, clean signal.*

### viper (3 segments) ⚠ — premise holds but our tool can't see it
- 105/158 commits touch only 2 files (Go idiom: `foo.go + foo_test.go`). 125 commits pile
  into one `viper.go + viper_test.go` segment because file-level fingerprints can't
  separate distinct invariants living in different functions of the same big file.
- **This is a tool limitation, not a premise failure.** viper's config-precedence
  invariant is real (ref_codebase A+), but resolving it needs *test-function-level*
  fingerprints (which `_test.go` function the commit's diff touches), not file-level.
- → R2 for viper: parse `go test` function names from diff hunks, build per-test-function
  fingerprints. Likely lifts viper from 3 → 10–15 segments.

## Honest weaknesses of R1 (do not paper over)

1. **Motif identity is not automated.** "Fork/Join/Scope/Update" labels above are
   hand-assigned from repo knowledge, not detected. A segment says *these N commits keep
   co-touching files X, Y, test_T* — that is L1–L2 evidence a human invariant exists, full
   stop. The paper cannot claim motif coverage from these counts alone.
2. **1-file-core noise.** Several large segments (fastify `type-parity`, clap `builder-api`)
   have a single core file ⇒ "everyone edited the shared file" ≠ "one evolving invariant".
   Need a core-files-cardinality gate or min-shared-file threshold in R2.
3. **Go blind spot.** File fingerprints fail for Go. Needs test-function fingerprints.
4. **No FAIL_TO_PASS / base-fail / gold-pass yet.** We have *candidates*; none are
   materialized into task nodes with a behavioral verifier. The mining gate from
   ref_codebase (base-fail, gold-pass, PASS_TO_PASS, SWE-bench dedup) is untouched.
5. **No causal verification.** Zero interventions run. Everything here would need to survive
   Reset-vs-Stateful and history-intervention arms before any paper claim.

## What R1 actually proves (and only this)

- **The raw material exists and is plentiful.** 2469 co-change commits, 102 motif-grade
  segments with concrete file anchors. ref_codebase's central premise — that these repos
  *naturally* produce repeated cross-cutting constraints — is **not hand-wavy; it is
  load-bearing and survives a first metadata check.**
- **The premise is language-dependent.** Multi-file-module languages (py/js/rs) expose
  motifs at file granularity; Go hides them inside single files and needs finer
  fingerprints. This is itself a paper-worthy finding (a scope threat to flag, §12.5).
- **A concrete audit queue now exists.** 102 named segments, each pointing at 2–4 specific
  files + a representative test. The next human step is bounded: read ~5 commits per
  flagship segment and decide whether the motif is real.

## Recommended R2 (next round, in priority order)

1. **Hand-audit the flagship segments** (httpx client-api, fastify plugin-scope/schema,
   clap builder↔derive, ripgrep ignore-precedence): 5 repos × 2–3 segments × ~5 commits =
   ~75 commits. Goal: convert L1–L2 segments into L3 semantically-audited edges with a
   real `experience` statement per edge. This is the gate before any task materialization.
2. **Fix viper granularity** (test-function fingerprints) — cheap, unblocks a flagship A+
   repo.
3. **Filter 1-file-core noise** (add `len(core_files) >= 2` gate to motif-grade).
4. **Stand up the task materializer** for 2–3 audited segments: base-snapshot-fails /
   gold-passes / PASS_TO_PASS controls (ref_codebase mining gate). Only after this does
   R1 stop being recon and start being benchmark data.

## Artifacts

```
mining/
├── repo_config.py            # per-repo src/test/ignore + module rules
├── cochange_miner.py         # pass 1: co-change commits + coarse clusters
├── motif_segments.py         # pass 2: file-fingerprint segments
└── out/
    ├── <repo>.commits.jsonl  # per-commit co-change record
    ├── <repo>.clusters.jsonl # coarse module clusters
    └── <repo>.segments.jsonl # motif-grade segments (the audit queue)
```
