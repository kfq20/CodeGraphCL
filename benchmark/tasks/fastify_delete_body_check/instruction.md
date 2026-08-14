# Task — fastify: a DELETE request with a Content-Type header but no body fails with a parse error

## Symptom (external behavior)

When a DELETE request includes a `Content-Type` header (e.g. `application/json`) but carries
no request body, the framework attempts to parse the body and fails — returning a 415
(unsupported media type) or a parse error instead of routing the request to the handler.
The handler never runs.

The same issue affects OPTIONS requests with a Content-Type header but no body.

A GET or POST with no Content-Type header works fine (parsing is skipped); only DELETE and
OPTIONS with a Content-Type header but no actual body are mishandled.

## Reproduction

Register a DELETE route handler that reads `req.body` and sends it back. Send a DELETE request
with `Content-Type: application/json` and an empty (null) body. The response is a 415 or parse
error, not the handler's response. After the fix, the response should be 200 with `null` as the
body (the handler runs, `req.body` is null, and the handler sends it).

## Acceptance

When a DELETE or OPTIONS request has a Content-Type header set but no request body is present,
the framework must skip body parsing and call the route handler directly — the handler receives
a null body. When a body IS present, parsing must still run as before. Requests without a
Content-Type header must continue to skip parsing (unchanged).

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the request-handling path for DELETE and OPTIONS methods.

When done, output a one-line summary of what you changed.
