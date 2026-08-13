# Task — fastify: a shared schema's identifier leaks into route schema compilation

## Symptom (external behavior)

When a shared schema is referenced from a route's schema, the shared schema's identifier
(`$id`) is left in place as the schema is merged into the route's schema tree and passed to the
JSON-schema compiler. The compiler then sees a nested identifier where it does not belong and
rejects / mis-compiles the combined schema.

The identifier is meaningful only at the top level of a shared schema (where it names the
schema in the shared store); once the shared schema is pulled into a route's schema tree, that
identifier should not travel with it.

## Reproduction

Register a shared schema with an identifier, reference it from a route's response schema, and
compile. The compile step errors or the nested identifier surfaces in the compiled schema
where it should have been stripped. The same route schema compiled without referencing the
shared schema compiles fine.

## Acceptance

When a shared schema is pulled into a route's schema tree for compilation, strip its
identifier from the schema (and from any nested schema objects) so the identifier does not
reach the compiler. The shared schema in the store must still be retrievable by its identifier
afterwards (the strip is on the copy used for compilation, not the stored original). Existing
schema-registration and lookup behavior must keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the schema resolver / shared-schema surface.

When done, output a one-line summary of what you changed.
