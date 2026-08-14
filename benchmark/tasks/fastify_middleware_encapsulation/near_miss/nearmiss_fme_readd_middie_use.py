"""Near-miss A for fastify_middleware_encapsulation: re-add this._middie.use(url, fn) to use().

The gold removes the shared `fastify._middie` instance and the `this._middie.use(url, fn)` call
from `use()` — middleware is now only pushed to the `_middlewares` array, and a per-context
Middie is built (snapshotted) from that array via `buildMiddie()`. This near-miss re-adds the
`this._middie.use(url, fn)` line to `use()` — plausible "I still need to register the middleware
on the instance" incomplete-removal trap — but `this._middie` is now undefined (gold removed the
shared instance), so `use()` throws `TypeError: Cannot read properties of undefined (reading
'use')` the moment the first plugin registers middleware. Caught.

Distinct from B: A crashes in use() (TypeError); B doesn't crash but the middleware never runs
(wrong value).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_fme_readd_middie_use.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold's use() only pushes to the array. Re-add the old _middie.use() line.
OLD = ("    this._middlewares.push([url, fn])\n"
       "    return this\n")
NEW = ("    this._middlewares.push([url, fn])\n"
       "    this._middie.use(url, fn)\n"
       "    return this\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    n = t.count(OLD)
    if n != 1:
        print(f"near-miss A: use() push-line count={n} (is gold applied? does use() still have _middie.use?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (re-add this._middie.use(url, fn) — this._middie is undefined) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
