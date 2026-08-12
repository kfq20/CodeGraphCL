# ripgrep c3 experience atoms (c2->c3 Update/Stale)

c3 revises c2's rule. c2 established: "when searching a subdir, strip the common prefix off
the search path before joining onto the absolute base, to avoid duplicate directory
components." c3 found c2's strip was too coarse and could shorten the path. So c2's rule is
STALE for c3 — following it reproduces the bug c3 fixes.

CRITICAL (Separability S4): c2's atom contains ONLY c2-era knowledge (avoid duplication). It
must NOT mention "over-strip" / "preserve components" — that is c3's discovery (future
knowledge, hindsight leakage).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit 14f4957b3d — but stated
as the lesson, not the patch): when building the match-path for a parent ignore while
searching a subdirectory, stripping a common prefix off the search path must be done
precisely — it must avoid both (a) leaving a duplicate directory component AND (b) removing
more than intended and shortening the path. Prefix elimination has to preserve path-component
boundaries, not just slice a string. The relative base, the absolute parent, and any leading
`./` or `/` each have to be handled as distinct cases, because a naive single strip that
happens to fix duplication can still break the path.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: commit cad1f5fae2 — the
established rule at that time): when searching a subdirectory, the path passed to a parent
ignore must be built by taking the absolute base path of the directory and joining it with
the search path. To avoid accidentally duplicating directory components, strip any common
prefix off the search path before the join. This single strip is the established approach for
subdirectory search.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): ripgrep's CLI flags include `--files`,
`--hidden`, `-g/--glob`, and `-t/--type` for filtering; the printer supports `--json`,
`--count`, and text output modes; the searcher respects `--max-count` and context flags.
These are real project facts about the CLI and output surfaces.
<!-- /ATOM:irrelevant -->

provenance:
  c2_rule_sha: cad1f5fae2
  c3_revision_sha: 14f4957b3d
  c4_refinement_sha: 0407e104f6
  audit: c2 atom verified to contain only c2-era knowledge (duplication); no "over-strip"
    (c3's discovery) present.
