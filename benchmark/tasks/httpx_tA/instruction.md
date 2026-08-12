# Task T_A — Add `start_tls` to the asyncio concurrency backend

## Background

This is an early (2019) snapshot of `httpx`. Concurrency is abstracted behind
`ConcurrencyBackend` (in `httpx/concurrency/base.py`), with concrete backends
`AsyncioBackend` (`httpx/concurrency/asyncio.py`) and `TrioBackend`
(`httpx/concurrency/trio.py`). The backend owns low-level stream operations:
connect, read, write, close.

At present the backend can open a plain TCP connection but **cannot upgrade an
existing connection to TLS**. There is no `start_tls` capability anywhere.

## Goal

Implement TLS upgrade-on-existing-connection for the asyncio backend:

1. Declare the capability on the `ConcurrencyBackend` abstraction in
   `httpx/concurrency/base.py` (a method other backends are expected to provide).
2. Implement it on `AsyncioBackend` in `httpx/concurrency/asyncio.py`.

### Required behavior (what the verifier checks)

Given a plain `connect(...)` to a local HTTPS server, then calling your
`start_tls(stream, hostname, ssl_context, timeout)` must:

- return a stream that is still alive (not dropped);
- leave that stream reporting a real TLS cipher (was `None` before, non-`None` after);
- allow a subsequent `stream.write(b"GET / HTTP/1.1\r\n...")` + `stream.read(...)` to
  return bytes beginning with `b"HTTP/1.1 200 OK"`.

### Constraints

- Use the provided `ssl.SSLContext` (do not create your own trust material).
- Respect `timeout.connect_timeout` for the handshake.
- Return the upgraded stream; the caller will keep using the returned object.
- Do NOT touch `TrioBackend` — that is a later task. Only the abstraction + asyncio.

### Running tests (the project's Python 3.7 + pytest 4.6 env is NOT on the host)

This codebase needs Python 3.7 + pytest 4.6.11 + pytest-asyncio 0.10 (host has newer, incompatible).
Run tests inside the prepared container:

```
docker exec cgcl-mat-box bash -c 'cd /pool/work && python3 -m pytest -q -p no:cacheprovider -o addopts= tests/test_concurrency.py'
```

(`tests/test_concurrency.py` may not exist yet in your workdir — that's fine; the verifier
adds it after you finish. You can still run other tests to sanity-check imports.)

### Hints (from the codebase, not the gold)

- `AsyncioBackend.connect` shows how a `Stream` (StreamReader/Writer pair) is built here.
- `loop.start_tls` is available (Python 3.7+) and upgrades an existing transport.
- The conftest `https_server` fixture serves HTTPS on `127.0.0.1:8001` for testing.

You do not need to match any specific function body or layout — only the behavior above.
