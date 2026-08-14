# Task — fastify: after close() is called, new requests still go through the full lifecycle instead of being rejected

## Symptom (external behavior)

When the application calls `fastify.close()`, the server begins shutting down, but incoming
requests that arrive before the server has fully closed still go through the entire request
lifecycle (route matching, hooks, handler, serialization). Under load this delays shutdown
indefinitely — each new request re-enters the pipeline and keeps a TCP connection open, so the
server never actually stops.

The visible effect: after `close()` is called, a new request still receives a normal 200
response from the route handler, instead of being rejected immediately.

## Reproduction

Register a route `GET '/'` that returns `{ hello: 'world' }`. Add an `onClose` hook with a
short delay (e.g. 150ms) so the server remains in a shutting-down state for a window. Inject
a first request (gets 200). Call `fastify.close()`. Wait 100ms (the onClose hook hasn't
finished yet). Inject a second request. On base, the second request goes through the handler
and gets 200. After the fix, the second request gets a 503 immediately.

## Acceptance

Once `close()` has been called, any new request must be rejected with a 503 (Service
Unavailable) response before reaching the route handler. The 503 response must include a JSON
body (`{ error, message, statusCode }`) and headers indicating the connection will be closed
(`Connection: close`). The request must be destroyed so it doesn't hold the connection open.
The first request (sent before close) must still complete normally.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the server lifecycle and the request handler entry point.

When done, output a one-line summary of what you changed.
