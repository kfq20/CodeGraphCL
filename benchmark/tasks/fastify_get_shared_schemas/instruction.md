# Task — fastify: read out all shared schemas registered on the instance

## Symptom (external behavior)

After a fastify instance has had several shared schemas added to it, there is no way to read
them back out. A caller that wants to inspect, export, or snapshot the set of shared schemas
registered on the instance has no accessor — the schemas are write-only from the instance's
public surface.

## Reproduction

After registering a couple of shared schemas on a fastify instance, calling a method to get
all of them back returns nothing (or throws, because no such accessor exists). The schemas are
stored internally but unreachable from the public API.

## Acceptance

Add a way to retrieve all shared schemas registered on the instance, returned as a map keyed
by their id, reflecting the schemas currently registered. The returned map must be a snapshot —
mutating it must not affect the instance's internal schema store (and vice versa). Existing
schema-registration behavior must keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The accessor belongs on the fastify instance's schema surface.

When done, output a one-line summary of what you changed.
