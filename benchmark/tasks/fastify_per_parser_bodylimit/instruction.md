# Task — fastify: a per-parser body size limit is not enforced

## Symptom (external behavior)

The framework lets each route set a maximum request body size, but a custom content-type parser
registered with its own smaller limit has that limit ignored — the parser uses the route/default
limit instead. A caller who registers a custom parser with a tight body limit and sends a body
exceeding it does NOT get the expected "body too large" error; the body is accepted (or the
wrong limit applies).

A parser registered without an explicit limit works (uses the default); only parsers that
declare their own limit are mishandled.

## Reproduction

Register a custom content-type parser with `{ bodyLimit: 5 }`. Send a 10-byte body with that
content type. The expected behavior is a 413 (body too large); the actual is that the body is
parsed (the parser's limit of 5 is ignored, the route/default limit applies).

## Acceptance

A custom parser's declared body limit must be enforced during parsing. When a route specifies
its own body limit, that route limit takes precedence over the parser's limit. A parser without
a declared limit uses the instance default. The existing single-limit behavior (route limit,
instance default) must keep working when no per-parser limit is set.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the content-type-parser + request-parsing surface.

When done, output a one-line summary of what you changed.
