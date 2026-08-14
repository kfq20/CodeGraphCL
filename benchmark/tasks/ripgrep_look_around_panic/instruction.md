# Task — ripgrep: search crashes (panics) with multiline + replace on look-around patterns

## Symptom (external behavior)

When running a search in multiline mode together with a replacement, ripgrep can crash (panic)
on certain regex patterns that use look-around — particularly patterns with alternations and
optional groups where the regex engine's reported match end can extend beyond the line window the
printer was operating on. The crash happens mid-search with a slice-index-out-of-bounds panic.

The panic is triggered by the interaction of multiline mode (which lets matches span lines) and
the replace path (which slices the input buffer by indices that, due to look-around, can become
inverted).

## Reproduction

Search a two-line haystack ` b b b b b b b b\nc\n` for the look-around pattern
`(^|[^a-z])((([a-z]+)?)\s)?b(\s([a-z]+)?)($|[^a-z])` with `-U` (multiline) and `-rx` (replace with
empty). Expected: the search completes and prints `xbxbx\n`. Actual (base): the search panics
with a slice index out of bounds.

## Acceptance

- Multiline + replace on a look-around pattern must complete without panicking.
- When the end of the last replacement overshoots the line window (due to look-around), the
  printer must clamp the trailing slice to the buffer end rather than slicing with an inverted
  (end < start) range.
- Existing replace behavior on non-look-around patterns is unchanged.

## Constraints

- Do NOT create or modify any test file or the inline test block — the verifier applies its own test after you finish.
- The fix belongs in the printer's replacement helper.

When done, output a one-line summary of what you changed.
