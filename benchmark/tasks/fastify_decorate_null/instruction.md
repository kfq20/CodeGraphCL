# Task — fastify: decorating with an empty value crashes

## Symptom (external behavior)

Calling the instance's decorate method to register a decorator with an empty (null / undefined)
value throws a TypeError instead of registering the value. A user who legitimately wants to
register an empty decorator value cannot — the method assumes the value is an object and reads
a property off it unconditionally.

Registering a non-empty object decorator works; only the empty-value case crashes.

## Reproduction

Call `instance.decorate('name', null)`. It throws a TypeError ("cannot read a property of
null", or equivalent) and the decorator is not registered. The same call with an object value
succeeds.

## Acceptance

Allow the decorate method to register an empty (null / undefined) decorator value without
crashing. The empty value must be registered as the decorator (subsequent reads of that name
return the empty value). The existing behavior for object values that declare accessor
properties must keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the fastify decorate implementation.

When done, output a one-line summary of what you changed.
