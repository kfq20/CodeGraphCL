"""Near-miss B for fastify header_case_validation: lowercase the wrong object's required array.

The gold fix lowercases `headersSchemaLowerCase.required` (the lowercased schema the validator
actually uses). This near-miss lowercases the ORIGINAL `headers.required` instead — plausible
reasoning "normalize the source required headers" — but the validator reads the lowercased
schema copy, whose `required` is never normalized. The case-mismatched header is still reported
missing, test fails.

Distinct from near-miss A: A maps the right object but identity (no-op); B maps with the right
function (toLowerCase) but the WRONG object. Different mistake axis.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hv_wrongobj.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "      headersSchemaLowerCase.required = headersSchemaLowerCase.required.map(h => h.toLowerCase())"
NEW = "      headers.required = headers.required.map(h => h.toLowerCase())  // NEAR-MISS B: wrong object"


def main():
    p = Path(sys.argv[1]) / "lib/validation.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: required-map line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (toLowerCase the original headers.required, not the lowercased copy) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
