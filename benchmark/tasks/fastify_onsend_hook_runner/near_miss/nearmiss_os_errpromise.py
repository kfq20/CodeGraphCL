"""Near-miss B for fastify onSend hook runner: error when a hook returns a promise.

The gold fix lets the generic hookRunner continue past a resolved promise (handleResolve -> next).
This near-miss treats a returned promise as an error: handleReject is called on resolve too.
Plausible reasoning "hooks should be synchronous; a returned promise is a misuse" — but the
resolve-to-value test deliberately registers hooks returning promises (Promise.resolve(1), etc)
to assert they're fine; erroring on them makes the request fail. Caught.

Distinct from near-miss A: A threads the value (base behavior, value overwrites state); B rejects
the promise entirely (the request errors before any state mutation). Both fail the test, different
reason.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_os_errpromise.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("    if (result && typeof result.then === 'function') {\n"
       "      result.then(handleResolve, handleReject)\n"
       "    }\n")
NEW = ("    if (result && typeof result.then === 'function') {\n"
       "      result.then(handleReject, handleReject)  // NEAR-MISS B: a returned promise is an error\n"
       "    }\n")


def main():
    p = Path(sys.argv[1]) / "lib/hookRunner.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: promise-then block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (treat a returned promise as an error) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
