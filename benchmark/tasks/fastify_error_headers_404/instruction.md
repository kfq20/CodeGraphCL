# Task — fastify: custom response headers attached to an error are missing from the 404 not-found response

## Symptom (external behavior)

When a route handler sends an error that carries custom response headers (e.g. `{ 'x-foo':
'bar' }` attached to the error object) and the error has a 404 status, the framework routes
it through the not-found handler — but the not-found handler's response is sent WITHOUT the
custom response headers. The `x-foo` header is absent from the response.

A 404 raised by a missing route works fine (the not-found handler runs). A route-sent 404
with custom response headers is the problem: the custom headers are set too late — after
the not-found handler has already sent the response.

Non-404 errors with custom response headers work fine (the headers are applied before the
generic error response is serialized); only 404 errors that go through the not-found
handler are affected.

## Reproduction

Register a not-found handler that returns a specific body (e.g. `'this was not found'`).
In a route handler, send a not-found error with custom response headers attached to the
error object (e.g. `{ 'x-foo': 'bar' }; reply.send(err)`). The response has status 404 and
the not-found body, but the `x-foo` header is missing. After the fix, the response should
carry the `x-foo: bar` header.

## Acceptance

When a route handler sends an error with custom response headers and a 404 status, the
not-found handler's response must include those custom headers. The headers must be applied
to the reply before the not-found handler sends the response. Errors with other status codes
must continue to carry their custom headers as before. The not-found handler's own headers
must also still work.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's error-handling path.

When done, output a one-line summary of what you changed.
