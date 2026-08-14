# Task — clap: value completion ignores position in multi-value arguments

## Symptom (external behavior)

When the dynamic completion engine completes values for a multi-value argument
(an argument that accepts several values in sequence, such as
`--set-upstream <REMOTE> <BRANCH>`), the completer always returns the same
candidate list regardless of which value position is being completed. The first
slot and the second slot get identical suggestions.

The expected behavior is that completion can return different candidates per
value position: for `--set-upstream <REMOTE> <BRANCH>`, completing the first
value should suggest remote names, and completing the second value should
suggest branch names.

## Reproduction

Build a clap app with a multi-value argument and a custom value completer that
intends to return position-dependent candidates. Trigger completion after the
flag for the first value, then for the second value. Both positions return the
full candidate set instead of the position-specific subset.

## Acceptance

Make the dynamic completion engine thread each value's position within the
argument's value range into the completer, so a multi-value argument can return
different candidates per slot. Existing single-value completion behavior must
keep working unchanged — implementors that do not care about position continue
to receive the same candidates they did before.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own
  tests after you finish.
- The fix belongs in the dynamic completion engine surface.

When done, output a one-line summary of what you changed.
