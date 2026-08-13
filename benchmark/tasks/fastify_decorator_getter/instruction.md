# Task — fastify: decorateRequest/decorateReply don't accept getter/setter config

## Symptom (external behavior)

The `decorate` method supports decorating with a getter/setter object (an object with
`getter` and/or `setter` functions). But `decorateRequest` and `decorateReply` do NOT
recognize this configuration — passing a getter/setter object to them is silently ignored
instead of defining the property with accessors.

## Reproduction

Given a fastify instance `app`:
```js
app.decorateRequest('user', { getter: () => 'alice' })
// on a request object, req.user should be 'alice' (via the getter)
// currently: the getter is not installed — req.user is undefined or throws
```

The same pattern works for `decorate` but is missing for `decorateRequest`/`decorateReply`.

## Acceptance

Fix `decorateRequest` and `decorateReply` so they recognize a getter/setter configuration
the same way `decorate` does. Existing decorator tests must keep passing.

## Constraints

- Edit `lib/decorate.js`. Do NOT modify `test/` — the verifier applies its own tests.
- Match the observable behavior `decorate` establishes, not any implementation detail.

When done, output a one-line summary of what you changed.
