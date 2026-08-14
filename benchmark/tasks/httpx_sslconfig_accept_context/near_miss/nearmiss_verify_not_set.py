"""Near-miss A for httpx_sslconfig_accept_context: accept SSLContext but don't set verify=True.

The gold __init__ stashes the SSLContext AND sets verify=True (assume caller configured it).
This near-miss accepts the SSLContext and stashes it, but leaves verify as the SSLContext object
(doesn't set it to True). Plausible "the caller passed an SSLContext, verify should reflect what
they passed" — but the test asserts verify is True. Caught: ssl_config.verify is the SSLContext
object, not True.

Distinct from B: A fails on verify attribute; B fails on ssl_context attribute.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_verify_not_set.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """        ssl_context = None
        if isinstance(verify, ssl.SSLContext):
            ssl_context = verify
            verify = True
            self._load_client_certs(ssl_context)"""

NEW = """        ssl_context = None
        if isinstance(verify, ssl.SSLContext):
            ssl_context = verify
            # NEAR-MISS A: don't set verify=True, leave it as the SSLContext
            self._load_client_certs(ssl_context)"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "config.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: SSLContext isinstance block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (accept SSLContext but don't set verify=True) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
