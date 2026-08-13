# Task — fastify: a custom content-type parser rejects empty request bodies

## Symptom (external behavior)

The content-type parser framework rejects any request with a zero-length body before it ever
calls the user's custom parser, responding with a 400 error about the request payload. This was
reasonable when the only content type was JSON (whose empty body is invalid), but now that
arbitrary content types can be registered with custom parsers, an empty body may be a legitimate
input the custom parser should handle (for instance, parse an empty body to an empty string or
buffer).

Sending a non-empty body works; only an empty body is rejected outright, regardless of the
registered parser.

## Reproduction

Register a custom content-type parser that returns an empty string for empty input, then send
a POST with an empty body and that content type. The request is rejected with a 400 before the
custom parser runs; the body is never parsed.

## Acceptance

Allow an empty request body to reach the registered custom parser (do not pre-reject zero-length
bodies). The custom parser must receive the empty input and may return whatever it deems correct
(an empty string, buffer, etc.). Non-empty bodies must keep being parsed exactly as before. The
body-size limit must still be enforced (a body exceeding the limit is still rejected).

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the content-type-parser body-reading path.

When done, output a one-line summary of what you changed.
