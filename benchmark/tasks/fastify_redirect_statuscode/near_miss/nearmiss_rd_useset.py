"""Near-miss A for fastify redirect: always use the preset status code, even when redirect
was given an explicit code.

The gold fix makes redirect honor a previously-set status code when redirect has NO explicit
code arg (the string-arg branch uses `_hasStatusCode ? res.statusCode : 302`), while keeping
the explicit-code-arg (number) branch as-is (caller's explicit code wins).

This near-miss over-applies the "honor the preset" rule: it uses the stored statusCode in BOTH
branches, including when redirect was given an explicit numeric code. Plausible reasoning —
"the caller set it, respect it" — but it breaks the override contract: `redirect(302, '/')`
after `code(307)` should respond 302 (explicit wins), not 307. The overwrite test fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_rd_useset.py <repo_dir>
"""
import sys
from pathlib import Path

# gold: string-arg branch uses the ternary; number branch uses `code` as-is.
# near-miss A: number branch ALSO uses res.statusCode, ignoring the explicit code arg.
OLD = "  this.header('location', url).code(code).send()"
NEW = "  this.header('location', url).code(this._hasStatusCode ? this.res.statusCode : code).send()  // NEAR-MISS A"


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: redirect send() line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (always use preset, ignore explicit redirect code) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
