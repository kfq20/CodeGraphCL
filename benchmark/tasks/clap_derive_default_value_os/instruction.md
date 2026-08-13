# Task — clap derive: `default_value_os` argument is still treated as required

## Symptom (external behavior)

In the `clap` derive API, an argument declared with an OS-string default value behaves
differently from one declared with a plain string default value. Declaring a default via the
OS-string form does not have the effect the user expects: the derived argument still ends up
marked as required, so building the app triggers a debug assertion failure about a required
argument that also has a default.

The plain-string form works correctly. The OS-string form does not.

## Reproduction

```rust
use clap::{IntoApp, Parser};

#[derive(clap::Parser)]
pub struct Options {
    #[clap(default_value_os = ("123".as_ref()))]
    x: String,
}

Options::into_app().debug_assert();
```

This panics today. The equivalent declaration using the plain-string default does not panic.

## Acceptance

Make the OS-string default form behave consistently with the plain-string default form
everywhere the derive layer reasons about whether a defaulted argument is required. The
example above must build and pass `debug_assert()` without panicking.

The same consistency must hold for the derive layer's existing validation rules: declaring a
default on a `bool` field, or on an `Option` field, must still be rejected with the existing
diagnostics — regardless of which of the two default forms was used.

Existing derive tests must keep passing.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the derive crate's attribute handling, not in the runtime `clap` crate.

When done, output a one-line summary of what you changed.
