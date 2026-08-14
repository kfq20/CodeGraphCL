"""Near-miss B for fastify_middleware_encapsulation: buildMiddie returns an empty Middie without
registering any middleware.

The gold's `buildMiddie(middlewares)` creates a Middie instance and registers each entry from
the `_middlewares` array via `middie.use.apply(middie, middlewares[i])`. This near-miss keeps
the function and the null-when-empty guard, but drops the registration loop — it returns an
empty Middie — plausible "I created the instance, the middleware is already in the array"
wrong-wiring trap. The route's context gets an empty Middie, so the first plugin's middleware
never runs; `request.raw.midval` is undefined/null, and the handler's
`t.strictEqual(request.raw.midval, 10)` fails. Caught.

Distinct from A: B doesn't crash (the empty Middie runs fine and calls onRunMiddlewares); the
middleware just never executes, so the assertion sees the wrong value.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_fme_empty_middie.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold's buildMiddie: guard + create + register loop + return. Drop the register loop.
OLD = ("  function buildMiddie (middlewares) {\n"
       "    if (!middlewares.length) {\n"
       "      return null\n"
       "    }\n\n"
       "    const middie = Middie(onRunMiddlewares)\n"
       "    for (var i = 0; i < middlewares.length; i++) {\n"
       "      middie.use.apply(middie, middlewares[i])\n"
       "    }\n\n"
       "    return middie\n"
       "  }\n")
NEW = ("  function buildMiddie (middlewares) {\n"
       "    if (!middlewares.length) {\n"
       "      return null\n"
       "    }\n\n"
       "    // NEAR-MISS B: return empty Middie, never register middleware\n"
       "    return Middie(onRunMiddlewares)\n"
       "  }\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: buildMiddie register-loop block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (buildMiddie returns empty Middie, no middleware registered) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
