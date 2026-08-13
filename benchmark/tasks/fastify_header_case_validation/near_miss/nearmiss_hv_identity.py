"""Near-miss A for fastify header_case_validation: map the required array as identity (no-op).

The gold fix lowercases the required header names via .map(h => h.toLowerCase()). This near-miss
maps the array but returns each element unchanged (.map(h => h)) — plausible reasoning "iterate
the required headers to normalize them" where the normalization step was forgotten. The required
array stays mixed-case, the case-mismatched header is still reported missing, test fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hv_identity.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "      headersSchemaLowerCase.required = headersSchemaLowerCase.required.map(h => h.toLowerCase())"
NEW = "      headersSchemaLowerCase.required = headersSchemaLowerCase.required.map(h => h)  // NEAR-MISS A: identity map"


def main():
    p = Path(sys.argv[1]) / "lib/validation.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: required-map line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (identity map, required stays mixed-case) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
