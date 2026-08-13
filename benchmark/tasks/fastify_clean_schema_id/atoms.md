# fastify_clean_schema_id experience atoms (fastify_get_shared_schemas -> fastify_clean_schema_id edge)

The producer (c9141a071d0f, "Add method to get all shared schemas") established that shared
schemas live in an internal store and are read back by returning a SNAPSHOT copy
(Object.assign({}, this.store)) — the stored originals are never handed out. The consumer
(5ffb131e40b9, "clean the $id key before passing it to the compiler") fixes the cross-use case:
when a shared schema is pulled into a route's schema tree for compilation, its $id must be
stripped from the COPY used for compilation — not the stored original, which must stay
retrievable. The consumer's own acceptance test asserts "the shared schema must still be
retrievable by its identifier after the strip" — directly invoking the producer's
snapshot/original-distinction.

provenance:
  producer_sha: c9141a071d0f   # producer-era: shared schemas have a read accessor that returns a
                               # snapshot copy; the internal store is never handed out directly
  consumer_sha: 5ffb131e40b9   # consumer: when reusing a shared schema in a different context,
                               # mutate only the snapshot copy, never the stored original
  audit: correct atom contains ONLY producer-era knowledge (snapshot-copy contract + "don't hand
    out the internal store"). It does NOT name $id-stripping or route-compilation (that is the
    consumer's discovery; naming it would be hindsight leakage, blocked by Separability S4).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit c9141a071d0f): shared
schemas registered on a fastify instance live in an internal store. They are read back through an
accessor that returns a SNAPSHOT copy — the map given to the caller is a fresh copy, not the
internal store object, so mutating it does not affect the instance and the instance's later
mutations do not leak into a previously-returned snapshot. The internal store is never handed
out directly. When a shared schema is to be reused or transformed for a different purpose, work
on the snapshot the accessor returns, not on the stored original — the stored original must stay
intact and retrievable.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: an earlier convention in this
codebase): the internal schema store is passed by reference to anything that needs it — the
fastify instance hands its own store object to callers, trusting them not to mutate it. There is
no copy-on-read; the accessor returns the live internal map. Callers that need to inspect or
transform a schema operate on that live object directly.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): fastify's request lifecycle is built on
hooks (onRequest, preHandler, onSend, onError); routes are registered with method+path;
reply.send() finalizes the response. These are real project facts about the lifecycle surfaces.
<!-- /ATOM:irrelevant -->

provenance_note: the WRONG atom is scope-plausible — "pass the internal store by reference,
trust callers not to mutate" is a real convention in some libraries (and is arguably simpler
than copy-on-read). An agent that follows it will mutate the stored schema in place and the
consumer's "stored original must stay retrievable" acceptance will fail.
