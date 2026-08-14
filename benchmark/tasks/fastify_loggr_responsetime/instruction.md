# Task — fastify: the per-request response time disappeared from the logs when logging is on

## Symptom (external behavior)

A recent change broke per-request response-time logging. When the application is configured
with a logger (logging to stdout), each request's "request completed" log line used to carry a
response-time field measuring how long the request took. After the change, that field is gone
(the log line is emitted, but with no response-time measurement). The field is still expected by
tooling that consumes the logs.

## Reproduction

Start the application with logging enabled. Make a request. The "request completed" log line is
written, but it carries no response-time field (the field is absent, not zero). The response-time
measurement is never computed for the request.

## Acceptance

When logging is enabled, the "request completed" log line must carry a truthy response-time
field (a positive number measuring the elapsed time from request start to response finish).
When logging is disabled, no response-time work should be done (the response-completion callback
is a no-op). The response-time must be computed from a per-request start timestamp captured when
the request begins, and must not crash when that timestamp is absent.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix spans the application setup (where the logger is detected and the response callback is chosen) and the response-completion path.

When done, output a one-line summary of what you changed.
