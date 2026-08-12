# T_B experience-priming atoms (history interventions)

T_B has a **real upstream edge** from T_A: T_A established the `start_tls` contract on
`ConcurrencyBackend` + an `AsyncioBackend` implementation. T_B's task is to add the missing
`start_tls` to `TrioBackend`. The contract lives in the code tree (`base.py` abstract stub +
`asyncio.py` impl), so a Reset agent CAN re-derive it by reading — the edge is
**beneficial (cuts re-derivation cost), not required (doesn't gate success)**.

Each atom below is the EXACT text prepended to the agent's session (nothing else from this
file is shown to the agent — design notes live in the "Design notes" section at the bottom,
after the atom blocks, so they can never leak into a prompt).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase): a stream-upgrade capability was recently
added to the concurrency abstraction — `start_tls` is declared on `ConcurrencyBackend` and
implemented on the asyncio backend. Its signature is
`(stream, hostname, ssl_context, timeout) -> stream`, and it wraps the existing transport in
an SSL layer so the returned stream reports a real cipher. Every concrete backend is expected
to provide it with the same signature and observable behavior, so the backends stay
interchangeable. The trio backend does not yet implement it.
<!-- /ATOM:correct -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): URL parsing follows RFC 3986 via the
`rfc3986` library; request/response models live in `httpx/_models.py`; `certifi` provides the
default CA bundle and `chardet==3.*` handles charset detection; the `SSLConfig` helper exposes
`load_ssl_context_no_verify` for building test contexts. Timeouts are represented by
`TimeoutConfig`, which carries separate connect/read/write budgets used across the codebase.
<!-- /ATOM:irrelevant -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase): for stream-upgrade capabilities, the
established pattern in this codebase is to implement them as a method on the backend that
takes the stream and returns the *same* stream after mutating its internal transport in
place — the caller continues using the original stream object. The method should not return a
new stream; mutate-and-return-same is the convention for backend stream operations, and
callers rely on holding the original reference.
<!-- /ATOM:wrong -->

---

## Design notes (NEVER shown to the agent — below all atom blocks)

- **correct** is the genuine contract T_A established. Naming the signature is legitimate:
  it is a real product contract from prior work, not a gold-patch detail.
- **irrelevant** is length-matched and factually true, but concerns URL/model/config surfaces
  rather than backend stream operations. Tests whether *any* context helps (placebo control).
- **wrong** is the *stale* shape that T_C later revises into "return a new stream". It is
  scope-plausible (it sounds like a real codebase convention) rather than absurd, per the
  review's requirement. It conflicts with the asyncio implementation the agent can still read,
  so a careful agent should catch the conflict; a credulous one writes a start_tls that
  returns the un-upgraded stream, which the hermetic verifier catches (no cipher appears).
- Atom text is delimited by `<!-- ATOM:name -->` markers so extraction is exact and design
  notes cannot leak into a prompt.
