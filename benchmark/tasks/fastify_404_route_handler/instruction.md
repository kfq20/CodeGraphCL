# Task — fastify: 404 errors raised during a request do not reach the custom 404 handler

## Symptom (external behavior)

The application allows registering a custom handler for "not found" responses (a 404 handler).
When a route handler — or a response lifecycle hook — produces an error whose status is 404
(for instance, by sending a "not found" error object), that error is treated like any other
generic error: the response comes back as a 500, and the custom 404 handler is never invoked.
Only requests for URLs that match no registered route reach the custom 404 handler; explicitly
signalling "not found" mid-request does not.

## Reproduction

Register a custom 404 handler. Add a route that, inside an onSend (response) hook, calls back
with a 404 error. Request that route. The response status is 500, not 404, and the custom 404
handler's body is not produced. (The same happens if a route handler sends a 404 error object
directly.)

## Acceptance

When a 404-status error is produced during a request — whether from a route handler or from a
response lifecycle hook — the framework must route it to the registered custom 404 handler,
so the response status is 404 and the custom handler's body is sent. If no custom 404 handler
is registered, a basic 404 response is sent instead. Calling the 404 path from within an
already-active 404 handler must not recurse: it should log a warning and send a basic 404.
Non-404 errors must keep being handled as before (their own status code / 500 fallback).

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the error-handling path of the reply.

When done, output a one-line summary of what you changed.
