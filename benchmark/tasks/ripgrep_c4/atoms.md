# ripgrep c4 experience atoms (c3->c4 candidate beneficial edge)

c4 refines c3's rule for the `.` / hidden-file scope. This is the candidate BENEFICIAL edge:
Correct-from-c3 (the precise strip rule c3 established) vs Stale-from-c2 (c2's naive single
strip, which over-strips in the `.` case). c3's atom is the correct experience for c4;
c2's atom is stale for c4 (it predates even c3's precision fix).

provenance:
  c2_rule_sha: cad1f5fae2   # c2-era: strip common prefix to avoid dir duplication (NO over-strip knowledge)
  c3_revision_sha: 14f4957b3d  # c3: strip must be precise — avoid both duplication AND over-strip, preserve boundaries
  c4_refinement_sha: 0407e104f6  # c4: `.` dir is a degenerate prefix that mangles hidden-file names
  audit: c2 atom = c2-era only (no over-strip). c3 atom = c3-era only (no `.`-scope knowledge).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit 14f4957b3d): when
building the match-path for a parent ignore while searching a subdirectory, stripping a
common prefix off the search path must be done precisely — it must avoid both (a) leaving a
duplicate directory component AND (b) removing more than intended and shortening the path.
Prefix elimination has to preserve path-component boundaries, not just slice a string. The
relative base, the absolute parent, and any leading `./` or `/` each have to be handled as
distinct cases.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: commit cad1f5fae2 — the
established rule at that time): when searching a subdirectory, the path passed to a parent
ignore must be built by taking the absolute base path of the directory and joining it with
the search path. To avoid accidentally duplicating directory components, strip any common
prefix off the search path before the join. This single strip is the established approach
for subdirectory search.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): ripgrep's CLI flags include `--files`,
`--hidden`, `-g/--glob`, and `-t/--type` for filtering; the printer supports `--json`,
`--count`, and text output modes; the searcher respects `--max-count` and context flags.
These are real project facts about the CLI and output surfaces.
<!-- /ATOM:irrelevant -->

provenance_note: c4's correct atom is c3's rule (precise strip); c4's wrong atom is c2's
rule (naive single strip). The difference from c3's own intervention: here the STALE prior is
c2 (two revisions back), and the CORRECT prior is c3 (one revision back) — so c3->c4 tests
whether the most-recent revision transfers forward (beneficial), while c2 is stale.
