# Task — clap derive: generated code breaks when a user defines common type aliases

## Symptom (external behavior)

When a downstream struct uses the clap derive macro and its surrounding module (or the crate)
happens to declare common single-word aliases for well-known standard-library types, the
derive's generated code fails to compile. The failure is a type-resolution error inside the
macro output — the generated code refers to a standard type by its bare single-word name,
which now resolves to the user's alias instead of the standard type it was meant to denote.

This only manifests when such an alias is in scope at the derive site; without one, the
generated code compiles fine.

## Reproduction

A struct derives `Parser` in a module that declares, for example, single-word aliases that
re-map two well-known standard types onto wrapper types. Building that struct fails to
compile, pointing into the derive-generated code. The same struct compiles if no such aliases
are in scope.

## Acceptance

Make the derive-generated code robust to the presence of user-defined single-word aliases for
standard types: the generated code must refer to the standard types unambiguously, so it
compiles regardless of what aliases are in scope at the derive site. Existing derive tests must
keep passing.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the derive crate's code generation, not in the runtime `clap` crate.

When done, output a one-line summary of what you changed.
