# Task — clap: fish shell completion registration mangles paths with special characters

## Symptom (external behavior)

When clap generates a fish shell completion registration script, the completer command path is
not escaped correctly if it contains special characters such as backslashes (`\`) or dollar
signs (`$`). Fish parses the completion registration's argument list more than once: once at the
outer level when the registration is sourced, and again later when the embedded command
substitution is evaluated at completion time. The current quoting only survives the first pass,
so backslashes and dollar signs become unquoted by the time the completer actually runs — the
completer receives a different path than the one that was registered, and completions for that
binary silently break.

Concretely: registering a completer whose path contains a backslash (e.g. `/p/dyn\amic/foo`)
produces a script where the backslash is consumed during the second parse, so the completer is
invoked with `/p/dynamic/foo` (missing the backslash). A path containing a dollar sign (e.g.
`/p/$var/c`) has the dollar-sign interpreted as a variable expansion on the second pass, so the
completer receives the expanded (or empty) value instead of the literal `$var`.

The command-name token (the `--command` value) is read only once and is handled correctly; the
problem is specific to the completer path that is re-evaluated.

## Reproduction

Generate a fish completion registration for a completer whose path contains a backslash or a
dollar sign. Inspect the emitted script: the completer path is quoted in a way that does not
survive the second parse, so the path seen at completion time differs from the registered path.

## Acceptance

Make the emitted fish completion registration preserve the literal completer path across both
parses: a backslash in the path must still be a backslash when the completer runs, and a dollar
sign must still be a literal dollar sign (not a variable expansion). The command-name token
must continue to be handled correctly. Other shells' completion registrations must remain
unchanged.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the shell-completion registration quoting surface.

When done, output a one-line summary of what you changed.
