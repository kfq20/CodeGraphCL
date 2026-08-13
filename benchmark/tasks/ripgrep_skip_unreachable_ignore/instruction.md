# Task — ripgrep: an unreachable ignore file is loaded anyway, surfacing a parse error

## Symptom (external behavior)

When a directory walk is bounded to a shallow depth, a subdirectory that sits exactly at the
depth boundary is never descended into — none of its contents are visited. Nevertheless, the
walker still opens and parses that subdirectory's ignore file (`.ignore`, `.gitignore`). If that
file is malformed, the parse error surfaces on the directory's entry, even though no entry inside
the directory was ever visited. A caller that walks with a shallow depth and happens to have a
malformed ignore file in an unvisited subdirectory sees a spurious error on a directory it
should have been able to list cleanly.

The walk completes, but the directory entry carries an error it shouldn't, because a file that
cannot affect any visited entry was read and parsed for nothing.

## Reproduction

Create a directory with a subdirectory `leaf`; put a malformed `.ignore` (`{invalid`) in `leaf`;
walk the parent with a max depth that reaches `leaf` but does not descend into it. The `leaf`
entry carries a parse error, even though nothing inside `leaf` was visited.

## Acceptance

When a directory will not be descended into (it sits at the depth boundary, or is otherwise
skipped), do not open or parse its ignore file. The directory's entry must carry no error from
an ignore file that cannot apply to any visited entry. Descended-into directories must still
load their ignore files exactly as before (the ignore-matcher chain must still be built for
visited subtrees).

## Constraints

- Do NOT create or modify any test file or the inline test block — the verifier applies its own test after you finish.
- The fix belongs in the directory-walk iterator.

When done, output a one-line summary of what you changed.
