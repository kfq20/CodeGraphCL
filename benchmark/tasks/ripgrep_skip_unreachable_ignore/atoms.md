# ripgrep_skip_unreachable_ignore experience atoms (b621e65 -> 435f59f edge)

The producer (b621e65, "ignore: add incremental checking") established the Ignore matcher-chain
cache architecture: parent matchers are cached by directory in `IgnoreInner.compiled`, and the
Walk iterator pushes/pops `Ignore` instances as it descends via `add_child` — which loads the
dir's ignore files (`.ignore`/`.gitignore`/`.rgignore`) into a child matcher. The chain must stay
consistent (every dir the iterator yields gets a stack entry, so the Exit event matches), but
LOADING ignore files is only meaningful for dirs whose entries will actually be visited.

The consumer (435f59f, "skip unreachable ignore files") applies this distinction: at the depth
boundary or a skipped dir, build the stack entry WITHOUT loading (an empty child matcher), so an
unreachable dir's malformed ignore file doesn't pollute the cache or surface a parse error on an
unvisited entry.

provenance:
  producer_sha: b621e65   # producer-era: the cache architecture (per-dir matchers; add_child loads;
                          # chain consistency via stack push/pop; loading only meaningful for visited dirs)
  consumer_sha: 435f59f   # consumer: at boundary/skip, build empty matcher without loading
  audit: correct atom = producer-era cache architecture knowledge only; does NOT name
    add_child_with_entries, the depth boundary, or the empty-matcher trick (consumer discovery;
    hindsight-blocked by Separability S4).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit b621e65): the ignore
matcher system maintains a chain of per-directory matchers, cached so parent matchers are reused
as the walk descends. Each directory the walk yields gets a stack entry so the descent/exit
pairing stays balanced, but the act of building a child matcher normally opens and parses that
directory's ignore file (`.ignore`/`.gitignore`/`.rgignore`). This loading is only meaningful for
directories whose contents will actually be visited — for a directory that the walk will not
descend into (it sits at the depth boundary, or is skipped), loading its ignore file reads and
parses a file that can apply to no visited entry, and a malformed such file surfaces a parse error
on a directory that is never visited. When a directory will not be descended into, the matcher
chain should still get its stack entry, but the ignore file should not be loaded.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: commit b621e65): the ignore
matcher system maintains a chain of per-directory matchers, cached so parent matchers are reused
as the walk descends. Every directory the walk yields is descended into via the same primitive —
build a child matcher by loading that directory's ignore file — and this is applied uniformly to
every directory the iterator produces, regardless of whether the walk will actually visit the
directory's contents. The chain is kept consistent by giving every yielded directory a child
matcher built the same way; there is no notion of "build the stack entry without loading."
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): ripgrep's CLI parses flags like --max-depth,
--ignore-file, and -g/--glob; the search reads stdin when no path is given; output is colored
based on --color. These are real project facts about the CLI and output surfaces, unrelated to the
matcher chain's caching or loading behavior.
<!-- /ATOM:irrelevant -->

provenance_note: the WRONG atom is literally the producer's own architecture (add_child is THE
descend primitive, applied uniformly) — it is the documented pattern, not an absurd prior. An
agent following it loads every dir's ignore file, which is exactly the base bug.
