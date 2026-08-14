"""Near-miss B for httpx_sslconfig_accept_context: accept SSLContext but don't load client certs.

The gold __init__ calls self._load_client_certs(ssl_context) after stashing the SSLContext,
ensuring client certificates are loaded into the passed-in context. This near-miss stashes the
SSLContext and sets verify=True but skips the cert-loading call. Plausible "the caller already
configured their SSLContext, no need to load certs" — but the _load_client_certs method is the
shared helper that handles all cert configurations. Caught: the test may not directly test cert
loading with a passed SSLContext, but the _load_client_certs call is part of the gold contract.
If the test passes without it, the near-miss is too weak — but if the test checks the repr or
the ssl_context identity, it may still pass. Let's verify empirically.

Actually, looking at the test:
    def test_load_ssl_context():
        ssl_context = ssl.create_default_context()
        ssl_config = httpx.SSLConfig(verify=ssl_context)
        assert ssl_config.verify is True
        assert ssl_config.ssl_context is ssl_context
        assert repr(ssl_config) == "SSLConfig(cert=None, verify=True)"

The test doesn't test cert loading directly (cert=None). So this near-miss might PASS the
verifier. In that case, we need a different near-miss. Let me try: accept SSLContext, set
verify=True, but DON'T stash ssl_context (leave it as None). This fails the identity check.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_no_cert_loading.py <repo_dir>
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
            # NEAR-MISS B: accept SSLContext, set verify=True, but don't stash it
            verify = True
            self._load_client_certs(verify)"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "config.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: SSLContext isinstance block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (accept SSLContext but don't stash ssl_context) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
