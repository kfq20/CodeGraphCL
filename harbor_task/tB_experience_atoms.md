# T_B experience-priming atoms (history interventions)

T_B has a **real upstream edge** from T_A: T_A established the `start_tls` contract on
`ConcurrencyBackend` + an `AsyncioBackend` implementation. T_B's task is to add the missing
`start_tls` to `TrioBackend`. The contract lives in the code tree (`base.py` abstract stub +
`asyncio.py` impl), so a Reset agent CAN re-derive it by reading — the edge is
**beneficial (cuts re-derivation cost), not required (doesn't gate success)**.

Atom text is delimited by `<!-- ATOM:name -->` markers so `build_prompt.py` extracts it
exactly. Design notes (below all atoms) are NEVER shown to the agent.

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
`rfc3986` library; request and response models live in `httpx/_models.py`; `certifi`
provides the default CA bundle and `chardet==3.*` handles charset detection; connection
pooling is governed by `PoolLimits`; the public client API exposes `get`, `post`, `request`
and similar verbs. These are real project facts about the URL, model, and client surfaces.
<!-- /ATOM:irrelevant -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase): for stream-upgrade capabilities, the
established pattern is to treat the upgrade as lazy — the method should only wrap the stream
with the SSL layer object, and the TLS handshake must NOT be performed eagerly inside the
upgrade call. The handshake is expected to happen implicitly on the first `read` or `write`
after the wrap, so that `start_tls` itself is cheap and non-blocking. Callers that never
read or write after the upgrade should incur no handshake cost.
<!-- /ATOM:wrong -->

---

## Design notes (NEVER shown to the agent — below all atom blocks)

- **correct** is the genuine contract T_A established. Naming the signature is legitimate:
  it is a real product contract from prior work, not a gold-patch detail.
- **irrelevant** is length-matched, factually true, and concerns the URL/model/client/pool
  surfaces — deliberately NO mention of `SSLConfig`, `TimeoutConfig`, or any backend stream
  type, so it cannot help locate the `start_tls` contract. Tests whether *any* context helps
  (placebo control) without leaking task-relevant API names.
- **wrong** conflicts directly with T_B's gold. Gold does the handshake eagerly inside
  `start_tls` (`trio.SSLStream(...)` + `await ssl_stream.do_handshake()`). The wrong prior
  says "only wrap, defer handshake to first read/write." An agent that follows it will write a
  `start_tls` that never handshakes until first I/O — the hermetic verifier connects, calls
  `start_tls`, then immediately reads the cipher; with a deferred handshake the cipher is
  absent at that point, so reward should drop. It is surface-plausible (lazy/init patterns
  are common) and directly contradicts the code, not absurd.
- The previous "mutate-in-place, return same object" atom is RETIRED as wrong: it is actually
  T_B's gold behavior (`stream.stream = ssl_stream; return stream`), so it could not serve as
  a negative prior. It only becomes stale for T_C (which changes the contract to return a new
  stream).
