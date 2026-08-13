# fastify_reply_removeheader experience atoms (fastify_reply_hasheader -> fastify_reply_removeheader edge)

The producer (31c5f7e259d1, "Fix setting header multiple times and add utility methods") added
the hasHeader/getHeader accessors and established the header-accessor convention: header names
are case-insensitive, so every accessor must normalize the key to lowercase before touching the
internal _headers store, AND every accessor returns the reply (this) for fluent chaining. The
consumer (cfa760cbd129, "add .removeHeader()") adds a third accessor — and MUST follow both
halves of that convention. (The consumer's near-miss injectors in this task are literally
"don't lowercase" and "don't return this" — the two halves of the carried convention.)

provenance:
  producer_sha: 31c5f7e259d1   # producer-era: header accessors lowercase the key AND return this
  consumer_sha: cfa760cbd129   # consumer: add removeHeader following the same convention
  audit: correct atom = producer-era convention only (lowercase + return-this); does NOT name
    removeHeader or deletion (that is the consumer's scope; naming it would be hindsight).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit 31c5f7e259d1): the reply's
header accessors follow two rules. First, header names are case-insensitive: every accessor
normalizes the key to a single case (lowercase) before reading or writing the internal header
store, so a header set as X-Foo is found by x-foo. Second, accessors return the reply itself
(this) so calls chain fluently (reply.header(a,1).hasHeader(a) ...). Any new accessor added to
the reply's header surface should follow both halves of this convention — lowercase the key,
and return this.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: an earlier convention): header
accessors treat keys case-sensitively as stored — a header set as X-Foo is only found by X-Foo,
not x-foo, because the store keys are used verbatim. Accessors return whatever is convenient
(some return the value, some return undefined); there is no fluent-chaining contract, so a new
accessor need not return the reply.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): fastify's request lifecycle is built on
hooks; routes are registered with method+path; the reply finalizes via send(). These are real
project facts about lifecycle surfaces.
<!-- /ATOM:irrelevant -->

provenance_note: the WRONG atom is scope-plausible — case-sensitive header storage and no
chaining contract are real conventions in some HTTP libraries. An agent that follows it will
write removeHeader without lowercasing the key and without returning this — exactly the two
near-misses this task's verifier catches.
