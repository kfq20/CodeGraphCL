# fastify decorator_getter experience atoms (c1->cef Parity edge)

c1 (Add support for decorating with a getter/setter object) established the rule on `decorate`.
cef (Fix decorate{Request,Reply} not recognizing getter/setter) propagates it to decorateRequest/decorateReply.
c1's rule is the CORRECT prior for cef (transfers forward); this is a candidate beneficial Parity edge.

provenance:
  c1_rule_sha: c1aac3cd85      # producer: added getter/setter to decorate
  cef_revision_sha: cef8814ea1 # target: propagate to decorateRequest/decorateReply
  audit: c1 atom = c1-era only (decorate getter/setter rule); no cef discovery (Request/Reply gap).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit c1aac3cd85): the `decorate`
method supports decorating with a getter/setter object — when the config object has `getter`
and/or `setter` functions, the property is defined with those accessors rather than as a plain
value. This capability was added to `decorate`. Every decoration method that accepts a config
object should recognize the same getter/setter configuration so decorators behave consistently
across `decorate`, `decorateRequest`, and `decorateReply`.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: commit c1aac3cd85): the `decorate`
method supports getter/setter config. However, `decorateRequest` and `decorateReply` are simpler
methods that only accept plain value decoration — they deliberately do NOT support getter/setter
because request/reply decorators should be lightweight. Adding accessor support there would
over-complicate the request/reply decoration path.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): fastify's route registration uses `method`,
`url`, and `handler` properties; the schema validation supports `querystring`, `params`, and
`body` schemas; the reply object exposes `code()`, `header()`, and `send()` for response shaping.
These are real project facts about routing and reply surfaces.
<!-- /ATOM:irrelevant -->

provenance_note: cef's correct atom = c1's rule (getter/setter on decorate transfers to
Request/Reply). cef's wrong atom = "Request/Reply deliberately don't support getter/setter"
(scope-plausible but wrong — cef proves they should). The stale/wrong prior is NOT c1's rule
(it's correct); the wrong prior is a false justification for the gap.
