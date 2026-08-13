# Task — clap: an "argument not found" error message has no trailing newline

## Symptom (external behavior)

When clap reports that a required argument was not found, the resulting error message string
does not end with a trailing newline. Other clap error messages do end with a newline, so this
one is inconsistent — downstream code that assumes error strings are newline-terminated
mis-handles this case (for instance, printing the error leaves the next prompt on the same
line).

## Reproduction

Build an app with a required argument, omit it, and convert the resulting error to a string.
The string does not end with a newline; other clap error strings do.

## Acceptance

Make the argument-not-found error message end with a trailing newline, consistent with clap's
other error messages. Existing error-message behavior for other errors must keep working
unchanged.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the clap error-formatting surface.

When done, output a one-line summary of what you changed.
