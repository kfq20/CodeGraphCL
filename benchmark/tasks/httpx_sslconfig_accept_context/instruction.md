# Task — httpx: passing a pre-built SSL context as the verify argument raises TypeError

## Symptom (external behavior)

The SSL configuration object accepts a `verify` parameter that can be a string (CA bundle
path) or a boolean (enable/disable verification). However, passing a pre-built
`ssl.SSLContext` object as `verify=` raises a `TypeError` — the constructor does not
recognize this type. Users who need a custom-configured SSL context (e.g. with specific
cipher suites or custom CA) have no way to pass it in.

## Reproduction

Create an `ssl.SSLContext` via `ssl.create_default_context()` and pass it as
`verify=ssl_context` to the SSL configuration constructor. It raises `TypeError` because
only `str` and `bool` are accepted.

## Acceptance

When `verify` is an `ssl.SSLContext`, the constructor must accept it, stash it directly
as the SSL context to use, and set the `verify` attribute to `True` (assume the caller
has configured the context to their needs). Client certificates (if configured) must also
be loaded into the passed-in context. The existing cert-loading logic should be shared
between the normal path and the pre-built-context path (not duplicated).

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the SSL configuration module.

When done, output a one-line summary of what you changed.
