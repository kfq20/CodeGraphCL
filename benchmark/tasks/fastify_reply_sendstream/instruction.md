# Task — fastify: a stream that errors before headers are sent resets the connection

## Symptom (external behavior)

When a response is sent by piping a readable stream to the reply, and that stream emits an
error before the response headers have been written, the HTTP connection is reset (the client
sees a socket hang-up / connection reset) instead of receiving an HTTP status code. The
stream's error status (for instance a 404 "not found" error from a file-serving stream that
points at a missing file) is lost: the client never learns why the response failed. There is
no way to surface the stream's error as a proper HTTP error response.

## Reproduction

Register a route that sends a stream which will error before any headers are written (for
example, a file stream over a non-existing path that emits a 404 error). Request that route.
The client receives a connection reset (ECONNRESET), not a 404 response with a JSON error body.

## Acceptance

When a piped stream errors before the response headers are sent, the framework must surface
that error as a proper HTTP error response: the stream's error status becomes the response
status, and the error is serialized through the normal error path (so the content-type is the
error content-type, e.g. application/json, and the body is the error object). When a stream
errors AFTER the headers are already sent (too late to change the response), the connection
should be torn down and the error logged. A stream that completes normally must still be
piped to the response unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's stream-sending path.

When done, output a one-line summary of what you changed.
