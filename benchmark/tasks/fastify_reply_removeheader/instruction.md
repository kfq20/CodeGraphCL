# Task — fastify: no way to remove a response header once set

## Symptom (external behavior)

After a response header has been set on a reply, there is no way to remove it. A handler that
sets a header and then decides it should not be sent (for instance, based on a later branch of
logic) has no recourse — the header stays set and is sent with the response. The only options
are to overwrite its value, not to drop it.

## Reproduction

Set a response header on a reply, then attempt to remove it. There is no method to do so; the
header remains and is sent with the response.

## Acceptance

Add a way to remove a previously-set response header from the reply, so it is no longer sent.
Removing a header that was never set must be a no-op (not an error). Setting and other header
operations must keep working unchanged. Header names are case-insensitive, so removal must
match a previously-set header regardless of the letter-case used to set it or to remove it.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's header surface.

When done, output a one-line summary of what you changed.
