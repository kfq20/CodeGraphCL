# Task — ripgrep: parallel walker hangs (deadlocks) when a visitor panics

## Symptom (external behavior)

The parallel directory walker can hang forever when the caller's visitor closure panics. Once a
worker thread panics mid-walk, the remaining worker threads may sit idle in their receive loop,
never noticing that the run is over, so the whole parallel walk never returns. The process must be
killed externally.

A related variant: if the panic happens while the walker is still *constructing* workers (before
any worker thread is spawned), the already-spawned workers wait indefinitely for partners that
were never created.

Both cases should instead propagate the panic and shut the whole pool down — the test asserts that
a panicking visitor causes the walker itself to panic (and never hang).

## Reproduction

Walk a directory containing a file with a parallel walker configured for multiple threads, and
supply a visitor closure that unconditionally panics. Expected: the `run` call panics (the panic
propagates to the caller). Actual (base): the call hangs forever (deadlock).

The builder-panic variant: configure two threads and make the *visitor-builder* closure panic on
its third invocation. Expected: the `run` call panics with the builder's message. Actual (base):
hangs (a worker was spawned before the panic and waits for a never-created partner).

## Acceptance

- A panicking visitor must cause the parallel walk to *panic* (not hang). The panic must propagate
  so a caller can catch it; the test is marked `#[should_panic]`.
- A panic in the visitor-builder closure must likewise propagate and not hang (the test is marked
  `#[should_panic(expected = "...")]`).
- A non-panicking walk must still complete normally (existing behavior unchanged).

## Constraints

- Do NOT create or modify any test file or the inline test block — the verifier applies its own test after you finish.
- The fix belongs in the parallel-walk worker lifecycle.

When done, output a one-line summary of what you changed.
