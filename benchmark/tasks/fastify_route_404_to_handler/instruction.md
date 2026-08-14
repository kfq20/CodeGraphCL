# Task — fastify: a 404 error from a route handler renders a JSON error body instead of the not-found page

## Symptom (external behavior)

When a route handler sends a not-found error (an error object carrying a 404 status), the
framework does NOT route it through the registered not-found handler. Instead it falls through
to the generic error path and renders a JSON `{ error: "Not Found", message: ... }` body — so
the user's custom not-found handler (which might return a branded page, a redirect, or a
specific body) never runs for a 404 that originates inside a route.

A 404 raised by a missing route (no route matched) works fine; only a 404 that a matched
route handler explicitly sends is mishandled.

## Reproduction

Register a custom not-found handler that returns a specific body (e.g. `'this was not found'`).
In a route handler, send a not-found error (`reply.send(new errors.NotFound())`). The response
body is the generic JSON error, not the custom not-found handler's body. The status is 404 but
the body is wrong.

## Acceptance

When a matched route handler sends a not-found error (404 status), the framework must route it
through the registered not-found handler, so the response carries the not-found handler's body
and behavior — not the generic error-serialization body. Errors with other status codes must
keep going through the generic error path unchanged. A not-found error raised inside the
not-found handler itself must not loop (it should fall back to a basic 404).

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's error-handling path.

When done, output a one-line summary of what you changed.
