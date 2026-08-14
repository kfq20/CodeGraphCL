# Task — ripgrep: a gitignore file starting with a Unicode BOM has its first rule ignored

## Symptom (external behavior)

When a `.gitignore` (or `.ignore`/`.rgignore`) file begins with a Unicode byte-order mark (BOM),
the first ignore rule in that file is not recognized — the BOM prefix attaches to the first
line's pattern, so the pattern never matches a real path. Files that should be ignored are not.

Git strips the BOM from the start of a gitignore file; ripgrep does not, so a BOM-prefixed
gitignore behaves differently from Git.

Git strips the BOM from the start of a gitignore file; ripgrep does not, so a BOM-prefixed
gitignore behaves differently from Git.

## Reproduction

Write a `.gitignore` whose first line is `ignore/this/path` but the file begins with a UTF-8 BOM
(the byte-order mark character). Walk a directory containing `ignore/this/path`. The file is NOT
ignored (the BOM prefix prevents the first-line pattern from matching). The same file without the
BOM ignores it.

## Acceptance

A UTF-8 BOM at the START of an ignore file must be stripped before parsing, so the first-line
pattern matches. BOMs appearing on LATER lines (not the start) must NOT be stripped — they are
literal characters in the pattern. This matches Git's behavior. Existing ignore-file parsing for
non-BOM files must keep working unchanged.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the ignore-file loading surface.

When done, output a one-line summary of what you changed.
