# Task — ripgrep: directory walker skips entries below a minimum depth

## Symptom (external behavior)

A directory walker exposes an option to set a minimum depth: entries whose depth is less than the
configured minimum are skipped (not yielded to the caller), while entries at or beyond that depth
are yielded as usual. Descending into subdirectories still happens regardless of the minimum, so
deeper entries are reachable — but the shallow entries are filtered out of the output stream.

The option mirrors the eponymous one in `walkdir`. Both the single-threaded and the parallel
walker must honor it.

## Reproduction

Build a tree `a/b/c` with a file `foo` at every level. Walk the root with a minimum depth of 2.
The walker yields only `a/b`, `a/b/c`, `a/b/c/foo`, `a/b/foo`, `a/foo` — it skips `a` and the
top-level `foo` (depth 0 and 1). With no minimum depth set, all entries are yielded.

## Acceptance

- A `min_depth` setter exists on the builder (takes `Option<usize>`, returns the builder).
- Entries whose depth is strictly less than the configured minimum are NOT visited (not passed to
  the caller's callback / not yielded by the iterator), in both the single-threaded and parallel
  walkers.
- Descending still happens for subdirectories shallower than the minimum (so deeper entries appear).
- When the minimum exceeds the maximum, the maximum is clamped up to the minimum (and vice versa)
  so the walker never silently produces nothing from an inverted range.
- Existing depth-less behavior is unchanged when no minimum is set.

## Constraints

- Do NOT create or modify any test file or the inline test block — the verifier applies its own test after you finish.
- The fix belongs in the directory-walk machinery (both the serial iterator and the parallel worker).

When done, output a one-line summary of what you changed.
