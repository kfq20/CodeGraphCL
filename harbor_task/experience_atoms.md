# T_A experience-priming atoms (history interventions)

T_A is an **anchor** task (no producer before it). So the "experience" in each condition
is a *constructed* session prefix — exactly the proposal §7.2 history-intervention design.
The point is not that T_A has a real upstream edge (it doesn't), but that this exercises
the full Reset-vs-Correct-vs-Irrelevant-vs-Wrong pipeline on a task whose Executable Gate
we already proved. If the pipeline produces a directionally-correct signal here, the
machinery is ready for T_B/T_C where real edges exist.

Each condition = a short "project context" note prepended to the agent's session, matched
in length so the only variable is content, not size.

---

## reset (no priming)
(no prefix — bare instruction)

## correct (the real contract)
> Project context: this codebase abstracts concurrency behind `ConcurrencyBackend`
> (in `httpx/concurrency/base.py`) with concrete backends. Capabilities that the backend
> must provide are declared as methods on `ConcurrencyBackend` (raising NotImplementedError
> as the abstract stub) and then implemented on each concrete backend. A stream upgrade
> capability like `start_tls` follows this pattern: signature
> `start_tls(stream, hostname, ssl_context, timeout) -> stream`, wrapping the existing
> transport in an SSL layer so the returned stream reports a cipher.

## irrelevant (length-matched, unrelated)
> Project context: this codebase uses `certifi` for the default CA bundle and pins
> `chardet==3.*` for charset detection. The `SSLConfig` helper loads contexts with
> `load_ssl_context_no_verify` for testing. Request/response models live in
> `httpx/_models.py`. URL parsing follows RFC 3986 via the `rfc3986` library. These are
> factual project facts but do not concern the concurrency backend's stream-upgrade path.

## wrong (scope-plausible but inapplicable to start_tls)
> Project context: in this codebase, `start_tls` should be implemented as a method on
> the *backend* that takes the stream and returns the *same stream* after mutating its
> internal transport in place — the caller keeps using the original stream object. The
> method should not return a new stream; mutate-and-return-same is the established pattern
> for backend stream operations.

(correct says "return a stream of the same type" + the contract-on-base pattern;
 wrong says "mutate in place, return the SAME object" — which is the *stale* T_A/T_B shape
 that T_C later revises; feeding it to T_A is a scope-plausible-but-wrong prior, exactly the
 hard-negative design the review asked for: not absurd, just inapplicable to this target.)
