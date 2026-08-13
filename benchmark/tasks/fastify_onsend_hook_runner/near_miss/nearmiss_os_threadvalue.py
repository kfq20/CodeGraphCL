"""Near-miss A for fastify onSend hook runner: thread the resolved value into state (base behavior).

The gold fix makes the generic hookRunner IGNORE resolved values — `handleResolve()` calls
`next()` with no value, so a hook resolving to 1/true/'a'/{} does not overwrite state. This
near-miss reverts to threading the value: `handleResolve(value) -> next(null, value)` and `next`
updates `state = value` when value !== undefined. Plausible reasoning "a hook that returns a
value is updating request state" — but the resolve-to-value test registers hooks resolving to
1/true/null/'a'/{} precisely to assert they do NOT mutate; threading them in overwrites state
and the request errors. Caught (same as base).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_os_threadvalue.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("  function handleResolve () {\n    next()\n  }\n")
NEW = ("  function handleResolve (value) {  // NEAR-MISS A: thread resolved value into state\n"
       "    next(null, value)\n  }\n")


def main():
    p = Path(sys.argv[1]) / "lib/hookRunner.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: handleResolve block not found (is gold applied?)"); return 1
    t2 = t.replace(OLD, NEW, 1)
    # also re-thread value into next: change `function next (err) {` to `function next (err, value) {`
    # and add `if (value !== undefined) state = value` after the err/length check
    OLD2 = ("  function next (err) {\n    if (err || i === functions.length) {\n      cb(err, state)\n      return\n    }\n\n")
    NEW2 = ("  function next (err, value) {\n    if (err || i === functions.length) {\n      cb(err, state)\n      return\n    }\n    if (value !== undefined) state = value  // NEAR-MISS A\n\n")
    if OLD2 not in t2:
        print("near-miss A: next() block not found (is gold applied?)"); return 1
    p.write_text(t2.replace(OLD2, NEW2, 1))
    print("near-miss A (thread resolved value into state, base behavior) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
