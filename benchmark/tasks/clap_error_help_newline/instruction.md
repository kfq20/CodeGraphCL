# Task — clap: a help-related error message has no trailing newline

## Symptom (external behavior)

When clap reports an error in the help-flag / subcommand path (for instance, an unrecognized
subcommand when the help flag is disabled), the resulting error message string does not end
with a trailing newline. Other clap error messages end with a newline, so this branch is
inconsistent — downstream code that assumes error strings are newline-terminated mis-handles
this case.

## Reproduction

Build an app with the help flag disabled and an unrecognized subcommand, and convert the
resulting error to a string. The string does not end with a newline; other clap error strings
do.

## Acceptance

Make the help-flag/subcommand error message end with a trailing newline, consistent with
clap's other error messages. Existing error-message behavior for other error paths must keep
working unchanged.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the clap error-formatting surface.

When done, output a one-line summary of what you changed.
