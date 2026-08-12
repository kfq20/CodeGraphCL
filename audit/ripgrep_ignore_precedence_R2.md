# Audit R2 — ripgrep / ignore-precedence segment

> Promotes the R1 segment from **L1–L2 (co-change)** to **L3 (semantically audited)**.
> All motif labels below are *audited hypotheses*, still NOT causally verified (no
> intervention run yet). Aligns with proposal L0–L5 ladder.
>
> **CORRECTION (post-review):** This is an **Update chain** `c2 → c3 → c4`, NOT a Join.
> c4 cannot be called Join merely because it "involves knowledge from both c2 and c3" —
> c2 and c3 are a *revision chain* (c3 revises c2), not two non-overlapping combinable
> sources. True Join would require two non-includable, non-substitutable experience atoms
> (e.g. one on path canonicalization + one on global ignore scope) jointly required by the
> target. Corrected motif: **Update + Stale/Scoped-Negative**.
>
> **Edge strength:** same as httpx — because the trunk is linear and c2's code lands before
> c3, c3's Base already contains c2's implementation. A Reset agent can read c2's strip-prefix
> code and re-derive the lesson. So the edge is **beneficial, not required**; the experiment
> measures cost (re-derivation effort) not only pass-rate.

## 1. The six commits

| # | sha | date | subject | locus |
|---|---|---|---|---|
| c1 | 9f0e88bcb1 | 2022-06-14 | fix gitignore parsing for trailing `\/` | `gitignore.rs` |
| c2 | cad1f5fae2 | 2022-08-29 | fix filtering when searching subdirectories (dup path parts) | `dir.rs` |
| c3 | 14f4957b3d | 2024-11-15 | fix filtering searching subdir / `.ignore` in parent dir (deleted too many path parts) | `dir.rs` |
| c4 | 0407e104f6 | 2025-10-08 | fix whitelisted hidden files when whitelist from parent gitignore (`.` special-case) | `dir.rs` |
| c5 | b610d1cb15 | 2025-10-15 | fix global gitignore with absolute paths (new `global_gitignores_relative_to` field) | `dir.rs` |
| c6 | 241b87b337 | 2026-07-09 | support `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` for `core.excludesFile` | `gitignore.rs` |

**Ancestry:** all six are on `main`; `merge-base --is-ancestor c2 c3` = YES (c2 is in c3's
ancestry). They are *linearly ordered on trunk*, but separated by thousands of unrelated
commits. Each task's base = `parent(sha)`, so each is independently snapshot-isolated.
This matches the proposal's §3.5 Snapshot-isolated Stream — experience can only propagate
via agent session memory, NOT via file state.
**Key caveat:** because c2 lands before c3 on the trunk, **c3's Base already contains c2's
strip-prefix code** — the lesson is re-derivable by reading `dir.rs`. So the c2→c3 edge is
beneficial (reduces re-derivation cost), not required.

## 1. The six commits

| # | sha | date | subject | locus |
|---|---|---|---|---|
| c1 | 9f0e88bcb1 | 2022-06-14 | fix gitignore parsing for trailing `\/` | `gitignore.rs` |
| c2 | cad1f5fae2 | 2022-08-29 | fix filtering when searching subdirectories (dup path parts) | `dir.rs` |
| c3 | 14f4957b3d | 2024-11-15 | fix filtering searching subdir / `.ignore` in parent dir (deleted too many path parts) | `dir.rs` |
| c4 | 0407e104f6 | 2025-10-08 | fix whitelisted hidden files when whitelist from parent gitignore (`.` special-case) | `dir.rs` |
| c5 | b610d1cb15 | 2025-10-15 | fix global gitignore with absolute paths (new `global_gitignores_relative_to` field) | `dir.rs` |
| c6 | 241b87b337 | 2026-07-09 | support `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` for `core.excludesFile` | `gitignore.rs` |

**Ancestry:** all six are on `main`; `merge-base --is-ancestor c2 c3` = YES (c2 is in c3's
ancestry). They are *linearly ordered on trunk*, but separated by thousands of unrelated
commits. Each task's base = `parent(sha)`, so each is independently snapshot-isolated.
This matches the proposal's §3.5 Snapshot-isolated Stream — experience can only propagate
via agent session memory, NOT via file state.

## 2. The recurring invariant (the "experience" this segment encodes)

All six commits return to the **same engineering problem**: *when searching a subdirectory
(or applying a parent/global gitignore), ripgrep must build the correct path that the
gitignore glob is matched against, and the path-stripping logic is subtle and repeatedly
wrong*.

Concretely the invariant under repeated revision is:

> **Path canonicalization before gitignore matching.** The `Ignore` traversal in `dir.rs`
> joins the absolute base with the search path, and must strip a common prefix so the
> resulting path is what the gitignore globs expect. Getting the strip *exactly right* —
> not too much (deletes path components, shortens the path) and not too little (leaves a
> `./` or duplicate component) — is the recurring failure. c2 introduced strip logic; c3
> found it stripped too much; c4 found a `.` special-case where it mangled hidden-file
> names; c5 found global gitignores need a *different* relative-to base entirely.

This is a genuine **Update / Revision motif**: each later commit *revises* a decision an
earlier commit made, and the revision is causally downstream of the earlier decision (the
later commit's message literally says "the previous code deleted too many parts").

## 3. The candidate experience-dependency edge

I pick **c2 → c3** as the primary triplet — it is the cleanest, and the causal link is
explicit in the commit message.

### Edge: `T_{c2} ──e,update──> T_{c3}`

| field | value |
|---|---|
| **Producer task (T_A = c2)** | "Fix subdirectory search so the absolute path doesn't contain duplicate parts." Adds a `strip_prefix(path_prefix, path)` block in `dir.rs` that strips the dir prefix from the search path before joining with the absolute base. |
| **Experience atom (e)** | *When building the path a parent gitignore glob is matched against (searching a subdir), you must strip a common prefix off the search path before joining it onto the absolute base — both to avoid duplicate path components AND to avoid over-stripping (which shortens the path). The prefix elimination must respect path-component boundaries and cover relative-path bases, absolute-parent bases, and the degenerate `.` directory case separately.* |
| **Evidence** | c2 diff (`dir.rs:442` adds the strip block + the comment "The main issue we want to avoid is accidentally duplicating directory components"); c3 diff rewrites that exact block AND its comment; c3 message: "The previous code deleted too many parts of the path". |
| **Consumer decision (T_B = c3)** | When fixing "subdir + `.ignore` in parent dir" matching, the agent must decide *how* to rebuild the match-path — reusing c2's strip-prefix idea but making the elimination precise so it neither duplicates nor over-strips. c2's experience points at the right family of solutions. **However**, since c3's Base already contains c2's code, a Reset agent can re-derive the lesson by reading `dir.rs`; the experience reduces *cost* (fewer wrong attempts), not *solvability*. |
| **Scope** | `crates/ignore/src/dir.rs`, the `Ignore` traversal `parents()` path-building block (~L442–L480). Holds across versions c2→c5 (c4/c5 further revise the same block). |
| **Alternative explanation** | Plausible: both touch `dir.rs` because it's the only place path-building lives. **Rejected as full explanation:** c3's message explicitly references "the previous code" (c2's), and c3's diff operates on c2's *specific* added lines + comment — this is not coincidental file overlap, it is a revision of a prior decision. |
| **Leakage check** | The atom states a *decision principle* (strip prefix exactly, respecting component boundaries, cover relative/absolute/`.` cases) — NOT a concrete Rust function, not `take_while`, not the `./ → prefix → /` ordering. The specific implementation is left to the agent. **Passes leakage filter.** |
| **Negative intervention (scope-plausible, not obviously-wrong)** | Per review: avoid the absurd "never strip" atom. Use a *real invariant correct in a different scope but inapplicable here*: the **global-gitignore relative-to-CWD** rule (c5's lesson — global/explicit gitignores are interpreted relative to CWD, not their file location). That rule is true and valuable, but irrelevant to *path-component stripping for parent-ignore matching* (c3's task). An agent that over-applies it to c3 should be misled or cost extra. This tests scope-judgment, not absurdity-rejection. |

### Verdict on the edge
**Consumer decision is concretely identifiable** (how to rebuild the match-path precisely).
The edge is **beneficial, not required** (c3's Base contains c2's code). Pass-rate may
saturate; cost metrics (re-derivation reads, wrong attempts) carry the signal.
→ **ripgrep qualifies for materialization** (pending Rust toolchain for the executable gate).

## 4. A second edge (Update, NOT Join)

**c3 → c4** is a second update edge in the same chain:
- c3 made the prefix-elimination precise (nested `./ → prefix → /` stripping).
- c4 found that when `ig.0.dir == "."` (the `consult`-tool special case), this stripping
  mangles a hidden-file name by stripping its leading `.`. c4 adds an early guard for the `.` case.
- This is **Update** (c4 revises c3's strip logic for the `.` degenerate case), NOT Join:
  c3 and c4 are a revision chain, not two independent combinable sources. The corrected
  family is **Update chain c2→c3→c4 + Stale/Scoped-Negative** (feed c2's "naive strip" or
  c5's "global relative-to-CWD" atom to c4 — scope-inapplicable).

## 5. Proposed task family (ripgrep, for materialization)

| node | commit | role | motif (corrected) |
|---|---|---|---|
| T_A | c2 `cad1f5f` | establish the strip-prefix path-building approach | anchor |
| T_B | c3 `14f4957` | revise c2's over-strip; make stripping precise | **Update** from T_A |
| T_C | c4 `0407e104` | fix `.`-dir special-case | **Update** from T_B |
| T_neg (stale/scoped-negative) | synthetic | feed c5's "global-gitignore relative-to-CWD" rule (real, correct in its scope, inapplicable to path-component stripping) | **Stale / Scoped-Negative** |

**Experience atoms (corrected, no leakage):**
1. *(c2→c3, beneficial)* When building the match-path for a parent gitignore, strip a common prefix off the search path before joining onto the absolute base — but the strip must be exact: it must avoid both duplicate components AND over-stripping (which shortens the path), and must respect path-component boundaries across relative-path, absolute-parent, and `.`-dir cases. *(principle only; no Rust functions or ordering prescribed)*
2. *(c3→c4, update)* When the search dir is literally `.`, prefix-elimination must NOT strip a leading `.` — hidden-file names begin with `.` and a `.`-dir is a degenerate prefix. Atom #1's "always strip the prefix" is **stale/under-scoped** for the `.` case.

## 6. Materialization plan (per TODO §3, SWE-bench procedure)

For each of {c2, c3, c4} (c2/c3 as producers, c4 as target):
1. `Base = parent(sha)` — checkout the commit's parent.
2. **Split the commit** into source patch (the `dir.rs`/`gitignore.rs` hunks) and verifier
   patch (the `tests/regression.rs` hunks). c2/c3/c4 each add a `rgtest!(...)` block — that
   is the verifier.
3. Apply verifier patch to `Base` → must **FAIL** (the bug is present).
4. Apply source patch + verifier to `Base` → must **PASS**.
5. Run `Base`'s existing `tests/regression.rs` → **PASS_TO_PASS** (no regression).
6. Reject if the commit is a mixed refactor / dep-bump / non-behavioral (c2–c4 are clean
   single-purpose bugfixes — verified by `--stat`: only src + test + CHANGELOG).
7. **Intentional-update flag:** none of c2/c3/c4 are behavior redefinitions; they are
   bugfixes where old behavior violates a reasonable expectation. No special flag needed.

### Risk to watch
- c4's regression test (#3173) — need to confirm the `rgtest!` block is self-contained
  (creates its own `.ignore`, dirs, files). From the R1 audit it is; will confirm at
  materialization.
- Ripgrep test build time: Rust. Must verify a single `cargo test --test regression <name>`
  for one `rgtest!` is <2 min after first build (ref_codebase mining gate).

## 7. Open questions / what this audit does NOT yet establish

- **No causal verification.** The c2→c3 edge is *semantically* a revision, but whether a
  coding agent actually does better on c3 *given* c2's experience (vs without) is unproven
  until the experiment runs (Task 6).
- **Hard-negative atom is hand-authored**, not mined. That's acceptable per the proposal
  (interventions are constructed), but must be noted in the data card.
- **c5/c6 not used** in the minimal family. c5 (global gitignore relative-to) is a deeper
  structural change — good material for an *Integrated* stream later, not the diagnostic family.

## 8. Decision

**Proceed to materialize the ripgrep family {c2, c3, c4} + 1 hard-negative.** The
Consumer-decision bar is met (§3). The commits are clean SWE-bench-style bugfixes on a
linear trunk, so the base-fail/gold-pass procedure is directly applicable. This is the
segment to take through the full vertical closure first; httpx/client-api audit (Task 2)
can run in parallel as a second family once this pipeline stands up.
