# Task — fastify: a route's header schema only applies when the schema spells the header name in lower case

## Symptom (external behavior)

A route's header validation schema silently does nothing for any header whose name is not written
entirely in lower case in the schema. Declare a header named `Y-Test` in a route's header schema and
send a request with a `Y-Test` header: the declaration has no effect. The header is neither validated
against its declared type nor type-coerced — a schema saying `{ type: 'number' }` leaves the value as
the raw string `'3'`.

Writing the exact same declaration as `y-test` works. So two schemas that a user would reasonably
expect to be equivalent behave differently, and the difference is invisible: nothing errors, the
request succeeds with a 200, and the declared constraint is simply skipped.

## Reproduction

Give a route a header schema with a property named `Y-Test` typed as a number, and have the handler
echo the request headers back. Send a request with the header `Y-Test: 3`. The response is 200, but
the echoed value is the string `'3'`, not the number `3` — the schema's type never applied. Change
the schema's property name to `y-test` and the value comes back as the number `3`.

## Acceptance

HTTP header names are case-insensitive (RFC 2616 §4.2), so a route's header schema must apply
regardless of the case used to spell the header name in the schema. A header declared as `Y-Test`,
`y-test`, or `Y-TEST` must all match the same incoming header and apply the same validation and
coercion. Header schemas that declare no properties at all must keep working unchanged, and the rest
of the schema (its type, required list, and other keywords) must be preserved.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs where a route's schemas are prepared for validation.

When done, output a one-line summary of what you changed.
