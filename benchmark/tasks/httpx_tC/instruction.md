# Task T_C — Revise the stream-upgrade capability (contract revision)

## Background

Earlier work established a `start_tls` capability on the concurrency backend abstraction
(`ConcurrencyBackend` in `httpx/concurrency/base.py`), implemented on both the asyncio and
trio backends. In that shape, the *backend* owns `start_tls`: the caller passes a stream in
and gets an upgraded stream back.

This task **revises** that contract: the capability should move from the backend onto the
**stream** itself. A stream that has been opened (plain TCP) should be able to upgrade
itself to TLS by calling its own `start_tls`, and the upgraded stream should be a **new**
stream object (the original plain stream is not mutated in place).

## Goal

Move `start_tls` from the backend to the stream objects, with the revised signature and
return semantics:

- The **stream** class(es) expose `start_tls(self, hostname, ssl_context, timeout) -> stream`
  (no `stream` argument — `self` is the stream being upgraded).
- Calling it returns a **new** stream wrapping the upgraded transport; the original stream
  is not mutated.
- Remove the now-obsolete backend-level `start_tls` (or make the backend delegate to the
  stream) so the two backends + their streams stay consistent.

## Constraints

- Edit the stream classes + the backend abstraction; keep both backends behaviorally
  interchangeable.
- Do NOT create or modify files under `tests/` — the verifier applies its own tests.
- Match the observable behavior the abstraction establishes, not any implementation detail.

## Running code (Python 3.7 env, not on host)
```
docker exec cgcl-mat-box bash -c 'cd ${PWD} && python3 -m pytest -q -p no:cacheprovider -o addopts= ...'
```
When done, output a one-line summary of what you changed.
