# Task — fastify: required-header validation is case-sensitive

## Symptom (external behavior)

Header validation treats required-header names as case-sensitive. A route that declares a
required header in one letter-case, while the incoming request supplies the same header name in
a different case, fails validation — the required header is reported as missing even though it
was sent (just with different capitalization). HTTP headers are case-insensitive by spec, so
this is wrong.

Non-required headers, and required headers sent with matching case, validate fine; only the
case-mismatch on a required header fails.

## Reproduction

Declare a route with a required header (say, `X-Token`), then send a request that includes
that header but spelled `x-token` (lowercase). The validation rejects the request as missing the
required header, even though the header was present.

## Acceptance

Make required-header validation case-insensitive: normalize the declared required header names
to a single case before comparing, so a required header sent in any letter-case is accepted.
Existing case-matched validation must keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the request-validation surface.

When done, output a one-line summary of what you changed.
