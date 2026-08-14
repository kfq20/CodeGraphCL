# Task — clap: help text shows required value names when the parser accepts fewer

## Symptom (external behavior)

When an option is declared with a value-count range (e.g., one-or-two values) and two value
names, the help text renders ALL value names as required (angle brackets). However, the parser
actually accepts providing just the minimum number of values, so the help contradicts what the
parser will take — it looks like the user must supply both values when they only need to
supply one.

The value names past the minimum should be rendered as optional (square brackets) to match
the parser's actual behavior. The first (minimum) value name stays required.

## Reproduction

Build an option with `num_args(1..=2)` and two value names `FOO` and `BAR`. Render the help.
The output reads `--example <FOO> <BAR>` — it should read `--example <FOO> [BAR]` (the second
value is optional, matching the parser).

## Acceptance

Value names past the minimum count must be rendered as optional (square brackets) in the
help text, while value names up to the minimum stay required (angle brackets). An option whose
value is optional as a whole (minimum is zero) already has its names handled by the caller's
bracketing, so those names must not get double-bracketed. Existing help rendering for
single-value and positional args must keep working unchanged.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the argument-to-string rendering surface.

When done, output a one-line summary of what you changed.
