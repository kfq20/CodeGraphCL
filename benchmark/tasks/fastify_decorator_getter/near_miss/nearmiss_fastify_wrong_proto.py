"""Near-miss B for fastify: Object.defineProperty on `this` (the instance) not the prototype.
The accessor only exists on the decorator instance, not on request/reply objects — test fails.
Runs on HOST. Usage: python3 nearmiss_fastify_wrong_proto.py <repo_dir>
"""
import re, sys
from pathlib import Path

def main():
    p = Path(sys.argv[1]) / "lib/decorate.js"
    t = p.read_text()
    # replace this._Reply.prototype -> this (wrong target) and this._Request.prototype -> this
    t2 = t.replace('this._Reply.prototype', 'this  // NEAR-MISS B: wrong target (instance not proto)')
    t2 = t2.replace('this._Request.prototype', 'this  // NEAR-MISS B: wrong target')
    if t2 == t:
        print("near-miss B: no _Reply/_Request.prototype found — is gold applied?"); return 1
    p.write_text(t2)
    print("near-miss B (wrong-proto) injected"); return 0

if __name__ == "__main__":
    sys.exit(main())
