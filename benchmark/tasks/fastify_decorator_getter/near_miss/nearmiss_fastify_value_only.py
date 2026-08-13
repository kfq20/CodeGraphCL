"""Near-miss A for fastify: add getter/setter to Request/Reply but as PLAIN VALUE (not accessor).
Replaces Object.defineProperty(..., {get, set}) with plain assignment prototype[name] = fn.
The getter function ends up stored as the value, not invoked — test fails.
Runs on HOST (container may lack python3). Usage: python3 nearmiss_fastify_value_only.py <repo_dir>
"""
import re, sys
from pathlib import Path

def main():
    p = Path(sys.argv[1]) / "lib/decorate.js"
    t = p.read_text()
    t2 = re.sub(
        r'Object\.defineProperty\(this\._Reply\.prototype, name, \{[^}]+\}\)',
        'this._Reply.prototype[name] = fn  // NEAR-MISS A: plain value, not accessor', t)
    t2 = re.sub(
        r'Object\.defineProperty\(this\._Request\.prototype, name, \{[^}]+\}\)',
        'this._Request.prototype[name] = fn  // NEAR-MISS A: plain value, not accessor', t2)
    if t2 == t:
        print("near-miss A: no defineProperty found — is gold applied?"); return 1
    p.write_text(t2)
    print("near-miss A (value-only) injected"); return 0

if __name__ == "__main__":
    sys.exit(main())
