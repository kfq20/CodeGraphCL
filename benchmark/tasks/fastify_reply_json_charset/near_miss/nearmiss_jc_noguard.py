"""Near-miss A for fastify json_charset: substring-match the JSON type but skip the charset guard.

The gold fix has TWO parts: (1) substring-match the JSON media type so charset-suffixed forms
are recognized, AND (2) a nested charset guard so the default content type is NOT set when the
caller already supplied a charset. This near-miss does part (1) only — drops the charset guard.
Plausible reasoning "I relaxed the match, the default-set is fine" — but the caller's charset
is now clobbered by the default-set. The charset-preserved assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_jc_noguard.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("  } else if (hasContentType === false || contentType.indexOf('application/json') > -1) {\n"
       "    if (hasContentType === false || contentType.indexOf('charset') === -1) {\n"
       "      this._headers['content-type'] = 'application/json; charset=utf-8'\n"
       "    }\n")
NEW = ("  } else if (hasContentType === false || contentType.indexOf('application/json') > -1) {\n"
       "    this._headers['content-type'] = 'application/json; charset=utf-8'  // NEAR-MISS A: no charset guard\n"
       "    if (false) {}\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: gold JSON+charset block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (substring match but no charset guard -> clobber) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
