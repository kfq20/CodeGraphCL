# Task — fastify: an unsupported method on a known path returns the wrong error status

## Symptom (external behavior)

When a request uses an HTTP method the application does not support on a route whose path IS
registered (for another method), the server responds with the method-not-allowed status. The
product decision is that this case should instead return the generic not-found status — the
path-with-unsupported-method case is treated as not-found, not as a method rejection.

The supported-method not-found case already returns the not-found status correctly; only the
unsupported-method case returns the wrong (method-not-allowed) status.

## Reproduction

Register a GET route at `/x`, then send a PUT (or other unsupported method) to `/x`. The server
responds with the method-not-allowed status; it should respond with the not-found status.

## Acceptance

Make the unsupported-method-on-a-known-path case respond with the not-found status instead of
the method-not-allowed status. The supported-method not-found case must keep responding with
the not-found status unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the request-handling path.

When done, output a one-line summary of what you changed.
