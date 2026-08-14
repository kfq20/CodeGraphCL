# Task — fastify: error is logged before the custom error handler runs, leaking the wrong status

## Symptom (external behavior)

When a route handler raises an error and a custom error handler is registered, the framework
logs the error (with its status level) BEFORE the custom error handler has a chance to process
it. So if the custom error handler transforms the error (e.g. turns a 500 into a 400), the
log still shows the original 500-level entry, and the log line appears out of order (the
"error" log appears before the handler's "request completed" log, instead of after).

The visible effect: the log stream shows an ERROR-level entry (level 50) for a request that the
custom error handler actually resolves as a 400 (level 30). The request-completion log line
shows statusCode 400, but the error log line shows level 50 — they disagree.

## Reproduction

Register a custom error handler that catches a specific error message and responds with a
400 status. Trigger the error from a route handler. Inspect the log stream: the error is
logged at ERROR level (50) before the handler runs, and the "request completed" line shows
statusCode 400. After the fix, the error should be logged at INFO level (30) after the handler
runs, matching the 400 status.

## Acceptance

The error log entry must appear AFTER the custom error handler has been invoked (or not at
all if the handler fully handles it). When the handler transforms the error to a different
status code (e.g. 400), the log level must reflect the final status (INFO for 4xx), not the
original 500. When there is no custom error handler, the error must still be logged at the
appropriate level (ERROR for 5xx, INFO for 4xx).

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's error-handling path.

When done, output a one-line summary of what you changed.
