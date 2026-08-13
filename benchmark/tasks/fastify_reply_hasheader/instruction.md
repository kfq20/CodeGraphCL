# Task — fastify: no way to check whether a response header has been set

## Symptom (external behavior)

After a response header is set on a reply, there is no way to ask whether a given header is
currently set. A handler that needs to branch on "did I already set this header" has no accessor
— the headers are write-only from the reply's public surface (you can set a header, but cannot
check whether one is present without sending).

## Reproduction

Set a response header on a reply, then attempt to check whether it is set. There is no method
to do so; the only way to find out is to send the response and inspect it after the fact.

## Acceptance

Add a way to test whether a given response header has been set on the reply (without sending).
It must return a boolean: true if the header is currently set, false otherwise. Asking about a
header that was never set returns false (not an error). Header names are case-insensitive, so
the check must match a previously-set header regardless of the letter-case used to set it or to
query it. Existing header-setting behavior must keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's header surface.

When done, output a one-line summary of what you changed.
