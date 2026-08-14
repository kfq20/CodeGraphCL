# Task — fastify: middleware registered in a later non-encapsulated plugin runs for an earlier route

## Symptom (external behavior)

When middleware is registered inside a non-encapsulated plugin (a plugin wrapped with
`fastify-plugin`, so it does NOT create an encapsulated child instance), and a route is
registered BEFORE that plugin, the middleware still runs for that route on request. The
middleware should only apply to contexts that exist at registration time — a route already
built should not pick up middleware registered later.

Concretely: register a non-encapsulated plugin that adds middleware setting a value on the
request; register a `GET '/'` route that reads that value; then register a SECOND
non-encapsulated plugin whose middleware should NOT run for that route. On the buggy build,
the second plugin's middleware IS called when `/` is hit (it should not be), because the
middleware registry is a single live object shared across all contexts — registrations after
the route leak into it.

## Reproduction

1. `instance.register(fp(pluginA))` where `pluginA` calls `i.use(mw)` (sets `req.midval = 10`).
2. `instance.get('/', handler)` where `handler` asserts `request.raw.midval === 10`.
3. `instance.register(fp(pluginB))` where `pluginB` calls `i.use(mw2)` that fails the test
   (`t.fail('middleware should not be called')`).
4. `instance.inject({ method: 'GET', url: '/' })` — expects `statusCode 200`, body
   `{ hello: 'world' }`, and the second middleware must NOT run.

On the buggy build, the second middleware runs (the test's `t.fail` fires) because the
middleware registry is live and shared. After the fix, the route's context has its middleware
snapshotted at route-registration time, so the later registration does not leak in.

## Acceptance

Middleware registered in a non-encapsulated plugin must apply to routes registered BEFORE that
plugin only if the plugin was registered before the route — otherwise the middleware must NOT
run for that route. Encapsulated child instances must inherit the parent's middleware (so a
non-encapsulated plugin's middleware is available to encapsulated children registered after
it). When no middleware is registered for a context, the request must still proceed to the
route handler without error.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the framework's middleware and plugin-encapsulation code.

When done, output a one-line summary of what you changed.
