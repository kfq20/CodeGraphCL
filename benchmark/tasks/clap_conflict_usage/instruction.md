# Task — clap: conflict-error usage string lists the conflicting argument twice

## Symptom (external behavior)

When a command has arguments configured as mutually exclusive (conflicting), and a user
supplies both, clap reports a conflict error. The error's usage line should show only the
argument that the user is being told to use instead — but it currently lists BOTH the argument
that triggered the conflict AND the conflicting argument in the usage string, which is
redundant and confusing (the usage line names the very arg the error is about, alongside the
one it's suggesting).

The conflict is detected correctly; only the rendered usage line is wrong (it includes the
arg that should be excluded).

## Reproduction

Define two conflicting args `--a` and `--conflict`. Supply both. The conflict error's usage
line reads `Usage: prog --a --conflict` — it should read `Usage: prog --conflict` (only the
non-triggering arg).

## Acceptance

The conflict error's usage string must list each conflicting argument only once and must NOT
include the argument that triggered the conflict (the one the user already supplied). Dedup the
conflict set before building the usage string. Existing conflict detection and error reporting
for non-overlapping conflicts must keep working.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the argument-validation / conflict-error construction surface.

When done, output a one-line summary of what you changed.
