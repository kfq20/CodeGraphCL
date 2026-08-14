# Task — fastify: a plugin's onSend hooks are skipped when a route inside that plugin sends a not-found error

## Symptom (external behavior)

When a plugin registers an `onSend` hook and a route inside that same plugin sends a not-found
error, the registered not-found handler produces the 404 response but the plugin's `onSend` hooks
never run. The response goes out without ever passing through the encapsulated hooks, so anything
those hooks do — rewriting the payload, adding a header, recording a metric — is silently skipped
for this one path.

Hooks registered on the plugin DO run for the plugin's normal (non-404) responses, and a 404 from
a genuinely missing route behaves as expected. Only the case where a matched route inside a plugin
sends a not-found error loses the plugin's hooks.

## Reproduction

Register a plugin that (a) adds an `onSend` hook and (b) declares a route which responds with a
not-found error (`reply.send(new errors.NotFound())`). Request that route. The status is 404, but
the plugin's `onSend` hook is never invoked — its callback does not fire.

## Acceptance

When a route inside a plugin sends a not-found error, the response must still run through the
`onSend` hooks that are in scope for that route, while the not-found handler continues to own the
404 response itself. Hooks must stay encapsulated: the hooks in scope for one route must not leak
onto unrelated routes or onto the root instance's not-found path.

Separately, the default not-found error message must use the HTTP reason phrase capitalization —
`'Not Found'`, matching the `error` field — instead of the lower-case `'Not found'` it currently uses.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs where a route's request context is finalized once all plugins and routes have loaded.

When done, output a one-line summary of what you changed.
