"""
Near-miss patch for T_A anti-hardcoding test.
This implements `start_tls` on AsyncioBackend so the METHOD EXISTS (passes a naive
"method present" check) but is BEHAVIORALLY WRONG — it does NOT upgrade to TLS, just
returns the plain stream unchanged. A verifier that only checks "method exists" would
wrongly pass this; a behavioral verifier (real cipher after start_tls) must FAIL it.

Apply on top of T_A Base (a4b93b9) — i.e. BEFORE the gold source patch.
"""
import re
from pathlib import Path

NEAR_MISS_CODE = '''

    async def start_tls(
        self,
        stream: "BaseStream",
        hostname: str,
        ssl_context: "ssl.SSLContext",
        timeout: "TimeoutConfig",
    ) -> "BaseStream":
        # NEAR-MISS: method exists, signature matches, but does NOT actually upgrade to TLS.
        # Returns the plain stream as-is. A behavior-checking verifier must catch this
        # (no cipher appears after start_tls). A method-existence check would wrongly pass.
        return stream
'''

def make_near_miss_patch(repo_file_text: str) -> str:
    """Inject the near-miss start_tls into AsyncioBackend (after connect, before run_in_threadpool)."""
    # Anchor: insert before 'async def run_in_threadpool' in asyncio.py
    marker = "    async def run_in_threadpool("
    assert marker in repo_file_text, "anchor not found"
    return repo_file_text.replace(marker, NEAR_MISS_CODE + "\n" + marker, 1)

if __name__ == "__main__":
    import sys
    src = Path(sys.argv[1]).read_text()
    out = make_near_miss_patch(src)
    Path(sys.argv[2]).write_text(out)
    print(f"near-miss written to {sys.argv[2]}")
