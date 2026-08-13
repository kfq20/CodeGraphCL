# Task — fastify: register a single custom parser for multiple content types at once

## Symptom (external behavior)

The method that registers a custom body parser for a content type only accepts a single
content-type string. A user who wants the same custom parser to handle several distinct
content types must call the method once per type, even though the parser, options, and intent
are identical for all of them.

There is no way to pass several content types in one registration call.

## Reproduction

Calling the registration method with more than one content type (for instance, two
near-identical custom types that should share a parser) registers only the first / last one or
throws, rather than registering the parser under every type given. Each type then has to be
registered in a separate call.

## Acceptance

Allow the content-type registration method to accept either a single content type (as today) or
several content types at once, registering the given parser under every one of them. A request
sent with any of the registered types must hit the custom parser and return the parsed body.
Existing single-type registration must keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the fastify builder's body-parser registration surface.

When done, output a one-line summary of what you changed.
