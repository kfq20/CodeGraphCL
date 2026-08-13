# ripgrep c5 experience atoms (c4->c5 candidate beneficial edge)

c5 refines c4's parent-matcher caching for the multi-root case. This is a candidate
BENEFICIAL edge: Correct-from-c4 (the caching discipline c4 established) vs
Stale-from-c3 (c3's pre-caching approach) vs Irrelevant (CLI/printer facts). c4's atom is the
correct experience for c5; c3's atom is stale for c5 (it predates the caching c4 introduced).

provenance:
  c3_sha: 14f4957b3d            # c3-era: build match-path per directory on demand, no cross-root caching
  c4_sha: 0407e104f6            # c4: cache parent matchers by directory for reuse; keep each walk root's path context distinct from the cached matcher
  c5_sha: 43e2f08               # c5: a cached parent matcher reused across a second root carried the first root's path context; the context must live with the walk, not the shared cached matcher
  audit: c3 atom = c3-era only (no caching knowledge). c4 atom = c4-era only (no cross-root-leak
    discovery — that is c5's finding; including it would be hindsight leakage, blocked by S4).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit 0407e104f): parent
ignore matchers are expensive to build, so they are compiled once per directory and reused
when the same directory is encountered again. But the path context used to rewrite a file's
path before matching against a parent ignore file belongs to the search root being walked —
it is not a property of the cached matcher itself. When a cached parent matcher is reused
while walking a different search root, it must be applied with the current root's path
context, not whatever context happened to be active when the matcher was first built. Keep
the walk-relative path with the walk, separate from the shared cached matcher state.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: commit 14f4957b3d — the
established approach at that time): when walking a directory, build the match-path against
the parent ignore files for that directory directly from the directory's own path, computed
fresh as each directory is visited. The directory being walked is the source of truth for the
path used in matching; there is no shared or reused parent-matcher state to consider.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): ripgrep's CLI flags include `--files`,
`--hidden`, `-g/--glob`, and `-t/--type` for filtering; the printer supports `--json`,
`--count`, and text output modes; the searcher respects `--max-count` and context flags.
These are real project facts about the CLI and output surfaces.
<!-- /ATOM:irrelevant -->

provenance_note: c5's correct atom is c4's caching discipline (walk-relative path stays with
the walk, not the cached matcher) — stated as the general principle, NOT the c5-specific
"structural move of a field off the shared inner" (that is c5's discovery and would be
hindsight leakage). c5's wrong atom is c3's pre-caching approach (stale, predates c4's
caching). c3->c5 would test whether ignoring caching entirely (c3) hurts; c4->c5 tests
whether the caching discipline transfers forward.
