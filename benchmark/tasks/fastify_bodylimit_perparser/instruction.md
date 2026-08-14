# Task — fastify: no way to set a body size limit per content-type parser, and the route limit is ignored

## Symptom (external behavior)

The application has a single, global cap on the size of a request body. There is no way to give
a specific content-type parser its own (smaller or larger) body limit, and a limit set on an
individual route is not honored when the body is actually read — only the global limit applies.
So a route that wants to accept large uploads for one content type but reject tiny bodies for
another cannot do so: every parser shares the same global ceiling, and a route-level limit has
no effect at parse time.

## Reproduction

Register a content-type parser with a small body limit (say 5 bytes). POST a 10-byte body of
that content type to a route that sets no route limit. The body is accepted and the parser is
invoked (it should have been rejected as too large). Separately, set a strict route body limit
(5) and a looser parser limit (100); POST a 10-byte body. The body is accepted (the route limit
was ignored).

## Acceptance

A content-type parser must accept its own body-limit option at registration time, applied only to
bodies of that content type. When reading the body, the limit must be selected by precedence:
a limit set on the route wins; otherwise the parser's own limit applies; otherwise the global
limit. An over-limit body must be rejected with a 413 status (and the parser must NOT be
invoked). A body under the selected limit must be parsed normally.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix spans the content-type parser registration/construction and the body-reading path.

When done, output a one-line summary of what you changed.
