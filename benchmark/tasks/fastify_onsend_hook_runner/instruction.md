# Task — fastify: a hook that resolves to a value breaks the request

## Symptom (external behavior)

When a request/preHandler/onResponse hook is asynchronous and resolves to a value (a number, a
string, an object — anything), the request fails: the framework treats the hook's resolved
value as if it were a replacement for some internal piece of request state, and the response
errors out instead of proceeding. A hook that resolves to `undefined` (or that is synchronous
and returns nothing) works fine; only hooks whose promise resolves to a concrete value break.

This is wrong: a hook resolving to a value is the normal case (a hook may compute something and
return it without intending to mutate request state). The resolved value of a
request/preHandler/onResponse hook should be ignored by the hook chain, not threaded in as state.

## Reproduction

Register an `onRequest` hook that does `return Promise.resolve(1)` (or `true`, `null`, `'a'`,
`{}`, `[]`) on a route, then send a request. The framework errors; the response is not 200 and
the body is not the handler's output. The same hook returning `Promise.resolve()` (no value)
succeeds.

## Acceptance

Hooks whose promise resolves to a value must NOT cause an error — the resolved value of a
request/preHandler/onResponse hook is ignored by the chain (it does not overwrite any state).
A request with such hooks must respond 200 with the handler's body. The reply-payload mutation
path (the onSend hook chain, which DOES legitimately transform the payload) must keep working
unchanged — onSend hooks may return a new payload, and that new payload replaces the response
body; but the generic hook chain does not thread values.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the hook-runner surface.

When done, output a one-line summary of what you changed.
