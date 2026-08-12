# Task T_B — Complete the Trio backend so it matches the concurrency backend abstraction

## Background

This codebase abstracts concurrency behind `ConcurrencyBackend`
(`httpx/concurrency/base.py`), with concrete backends `AsyncioBackend`
(`httpx/concurrency/asyncio.py`) and `TrioBackend` (`httpx/concurrency/trio.py`).

`ConcurrencyBackend` declares the capabilities every backend should provide. Some
backends may currently be missing capabilities that the abstraction expects. Read the
abstraction to find which capabilities are declared, then check which concrete backends
don't yet implement them.

## Goal

Make `TrioBackend` satisfy every capability the `ConcurrencyBackend` abstraction declares.
Focus on the capability that is currently unimplemented on the Trio backend but implemented
elsewhere — implement it on Trio, following the same interface and the same observable
behavior the existing implementation provides (so that the two backends are behaviorally
interchangeable for that capability).

## Constraints

- Only edit `TrioBackend` (and the abstraction if strictly needed). Do not modify the other
  backend's implementation.
- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you
  finish.
- Match the interface and observable behavior the abstraction + existing backend establish,
  not any particular implementation detail.

## Running code (Python 3.7 env, not on host)

```
docker exec cgcl-mat-box bash -c 'cd ${PWD} && python3 -m your_check_here'
```

When done, output a one-line summary of what you implemented.
