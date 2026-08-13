# fastify_contenttype_array experience atoms (fastify_contenttype_emptybody -> fastify_contenttype_array edge)

The producer (8c5e732f2e9b, "Allow parsing empty request bodies") removed the content-type
parser's zero-length-body early-reject, establishing that the parser's body-reading path must
HAND OFF non-canonical inputs to the registered custom parser rather than pre-rejecting them
based on a built-in assumption (the old "empty = invalid" was a JSON-era optimization that
broke once custom parsers existed). The consumer (7f378355, "Support array syntax to handle
multiple content types as the same") extends the registration surface: a single add call may
now receive a COLLECTION of content types, and the parser registration must register the
parser under EACH rather than treating the collection as a single (broken) type.

provenance:
  producer_sha: 8c5e732f2e9b   # producer-era: the body-reading path hands non-canonical inputs to
                               # the custom parser; don't pre-reject based on built-in assumptions
  consumer_sha: 7f378355      # consumer: registration accepts a collection; register per element
  audit: correct atom = producer-era "don't pre-reject / hand off" discipline; does NOT name
    array-handling or per-element registration (that is the consumer's scope; hindsight-blocked).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit 8c5e732f2e9b): the
content-type parser's body-reading path must HAND OFF non-canonical inputs to the registered
custom parser rather than pre-rejecting them based on a built-in assumption. A registered custom
parser is the authority on what its content type accepts — including shapes the framework's
defaults would reject (an empty body, a non-standard structure). The discipline: when the
registration or reading surface encounters an input that doesn't fit the framework's default
expectation, fan out to the custom parser / to each registered entry, rather than rejecting or
treating the collection as a single value.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: an earlier convention): the
content-type parser pre-validates inputs against the framework's built-in assumptions and
rejects anything that doesn't fit (empty bodies, non-string types) before the custom parser
runs. A registration call receives a single content type; passing a collection is an error and
the registration treats the collection object as if it were a single type.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): fastify's route registration binds a method,
url, and handler; the reply is finalized via send(); hooks run at onRequest/preHandler/onSend.
These are real project facts about the routing and reply surfaces.
<!-- /ATOM:irrelevant -->

provenance_note: the WRONG atom is scope-plausible — "the framework pre-validates and rejects;
collections are an error" is a real convention in stricter parsers. An agent that follows it will
treat the array as a single type (the consumer's near-miss "passthrough" / "firstonly" injectors
are exactly this failure), so the verifier catches it.
