# T_C experience-priming atoms (history interventions)

T_C revises the contract T_A/T_B established: `start_tls` moves from the backend onto the
stream, returning a NEW stream (not mutate-in-place). The T_A/T_B shape is **stale** for T_C.
This is the strongest CL test: the stale prior contradicts the contract LOCATION (backend vs
stream), not just an impl detail. Atoms delimited by `<!-- ATOM:name -->` (build_prompt.py).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase): the stream-upgrade capability was
recently revised. `start_tls` is no longer a method on the backend; it now lives on the
stream object itself, with signature `start_tls(self, hostname, ssl_context, timeout) ->
stream`. Calling it returns a NEW stream wrapping the upgraded transport; the original plain
stream is not mutated. The backend-level `start_tls` is obsolete and should be removed (or
delegated). Both backends and their stream classes must stay consistent with this revised
contract.
<!-- /ATOM:correct -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): URL parsing follows RFC 3986 via the
`rfc3986` library; request and response models live in `httpx/_models.py`; `certifi`
provides the default CA bundle and `chardet==3.*` handles charset detection; connection
pooling is governed by `PoolLimits`; the public client API exposes `get`, `post`, `request`
and similar verbs. These are real project facts about the URL, model, and client surfaces.
<!-- /ATOM:irrelevant -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase): the stream-upgrade capability is owned
by the backend. The `ConcurrencyBackend` abstraction exposes `start_tls(stream, hostname,
ssl_context, timeout) -> stream`, which the concrete backends implement. The method takes
the stream as an argument, mutates the stream's internal transport in place, and returns the
SAME stream object. Streams themselves do not carry an upgrade method — that responsibility
belongs to the backend, and callers invoke `backend.start_tls(stream, ...)` to upgrade an
existing connection.
<!-- /ATOM:wrong -->

---

## Design notes (NEVER shown to the agent — below all atom blocks)

- **correct**: T_C's revised contract (start_tls on stream, returns new stream). Legitimately
  names the new signature — it is the real product contract T_C establishes.
- **irrelevant**: length-matched, true, no SSLConfig/TimeoutConfig/stream-backend mention.
- **wrong = STALE T_A/T_B contract**: "backend owns start_tls, pass stream in, mutate in
  place, return same; streams don't carry an upgrade method." This is *exactly* the code at
  T_C's base (base.py:122 + trio.py:174 backend.start_tls). It is surface-plausible (it WAS
  the correct contract) but STALE for T_C. If the agent follows it, it leaves
  `backend.start_tls` in place and never adds `stream.start_tls` — the verifier calls
  `stream.start_tls(...)` and hits AttributeError → reward=0. This is the proposal's
  stale-history intervention: a prior that was once correct but now contradicts the code.
  Unlike T_B's wrong (defer-handshake impl detail the agent could override by reading),
  T_C's stale prior is about the contract LOCATION — following it structurally prevents the
  right answer. Expected: stronger negative transfer than T_B (stale 0/3 like wrong was).
- **positive-transfer test**: correct's revised contract is non-trivial to derive by reading
  (the revision spans asyncio.py 76 lines + base + trio). If correct separates from reset
  on solve rate or cost, that's the beneficial edge T_B couldn't show.
