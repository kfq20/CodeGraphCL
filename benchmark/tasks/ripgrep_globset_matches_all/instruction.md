# Task — ripgrep: glob set reports a path matches ALL globs when it matches only one

## Symptom (external behavior)

A glob set that contains multiple globs can incorrectly report that a single path matches *all*
globs in the set, when in fact it matches only one of them. For example, with a set containing
`abc` and `def`, querying whether the path `abc` matches *all* globs returns true — but `def`
does not match `abc`, so the correct answer is false.

The bug arises because the internal matching strategies bucket multiple distinct globs together
(by literal / basename-literal / extension / prefix / suffix / required-extension / regex), and
the all-matches check only verified that *each strategy bucket* had at least one match — not that
*every glob within a bucket* matched. So two different literal globs in the same bucket would
fool the check into reporting "all matched" as soon as either one matched.

## Reproduction

Build a glob set from `abc` and `def`. Ask whether the path `abc` matches all globs. Expected:
false (only `abc` matches; `def` does not). Actual (base): true.

## Acceptance

- `matches_all` must return true only when *every* glob in the set matches the candidate path.
- For a single-glob set, `matches_all` reduces to whether that one glob matches.
- The fix must not allocate extra memory to track per-glob match counts on the hot path.
- Existing `is_match` / `matches` behavior is unchanged.

## Constraints

- Do NOT create or modify any test file or the inline test block — the verifier applies its own test after you finish.
- The fix belongs in the glob-set matching strategies.

When done, output a one-line summary of what you changed.
