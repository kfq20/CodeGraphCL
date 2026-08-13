# Task — ripgrep: parent ignore rules applied to the wrong directory when searching multiple roots

## Symptom (external behavior)

When ripgrep is invoked with more than one search root on the command line, the parent
`.gitignore` / `.rgignore` rules are applied using the wrong directory's path context. A file
that should be ignored by a parent ignore file in one root can leak into the results, or be
ignored for the wrong reason, because the parent-ignore state established while walking the
first root carries the first root's directory context into the later root when it is reused.

The single-root case works correctly; only multiple explicit roots in one invocation expose
the bug.

## Reproduction

Given a project with a `.gitignore` that ignores `src/invalid`, and two search roots `src`
and `tests`, running `rg --files-with-matches <pattern> src tests` lists `src/invalid` even
though the parent `.gitignore` should exclude it. Reversing the order of the roots on the
command line should behave the same but the result depends on which root was prepared first.

## Acceptance

Fix the parent-ignore matching so each search root keeps its own directory context when
parent-ignore state from one root is reused for another. A file correctly ignored by a parent ignore
file must stay ignored regardless of how many roots are given or their order. Existing
regression tests must keep passing.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the ignore crate's directory-walking / parent-matcher handling.

When done, output a one-line summary of what you changed.
