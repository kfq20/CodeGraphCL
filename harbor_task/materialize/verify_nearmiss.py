#!/usr/bin/env python3
"""Anti-hardcoding gate (TODO step 5): a NEAR-MISS implementation must FAIL the verifier.

Near-miss = `start_tls` EXISTS on AsyncioBackend (correct signature) but is behaviorally
WRONG — it returns the plain stream without upgrading to TLS. A verifier that only checks
"method exists" would wrongly PASS this; a behavioral verifier (real cipher after start_tls)
must FAIL it.

This script: on T_A Base, apply the near-miss (NOT gold), apply verifier, run the target
test, and assert it FAILS. If it passes, the verifier is too weak (hardcoding-vulnerable).
"""
import json, os, subprocess, sys
from pathlib import Path

REPO = Path("/workspace/httpx")
W = Path("/materialize")

def git(*a):
    return subprocess.run(["git","-C",str(REPO),*a],capture_output=True,text=True)

def near_miss_patch():
    """Return the near-miss source text to inject into asyncio.py."""
    return '''
    async def start_tls(
        self,
        stream: "BaseStream",
        hostname: str,
        ssl_context: "ssl.SSLContext",
        timeout: "TimeoutConfig",
    ) -> "BaseStream":
        # NEAR-MISS: method exists + signature matches, but does NOT upgrade to TLS.
        # Returns the plain stream. Behavioral verifier must catch (no cipher appears).
        return stream
'''

def apply_nearmiss():
    """Inject near-miss start_tls before 'async def run_in_threadpool' in asyncio.py."""
    p = REPO / "httpx/concurrency/asyncio.py"
    txt = p.read_text()
    marker = "    async def run_in_threadpool("
    assert marker in txt, "anchor not found in asyncio.py"
    p.write_text(txt.replace(marker, near_miss_patch() + "\n" + marker, 1))
    print("  near-miss start_tls injected into asyncio.py")

def main():
    spec = json.loads(sys.argv[1])
    sha = spec["sha"]
    ver = W / spec["verifier_patch"]
    sel = spec["test_selector"]
    print(f"=== Near-miss anti-hardcoding test: {sha} ===")

    base = git("rev-parse", f"{sha}^").stdout.strip()
    git("checkout","-q","-f",base)
    subprocess.run(["git","-C",str(REPO),"clean","-fdx","--","tests/"],capture_output=True)
    print(f"  Base = {base[:8]}")

    # apply verifier (the test)
    r = git("apply", str(ver))
    if r.returncode != 0:
        print("  verifier patch failed to apply"); sys.exit(2)
    # apply NEAR-MISS instead of gold source
    apply_nearmiss()

    # run target test — expect FAIL (near-miss is behaviorally wrong)
    r = subprocess.run([sys.executable,"-m","pytest","-q","-x","-p","no:cacheprovider",
                        "-o","addopts=", sel],
                       cwd=str(REPO), capture_output=True, text=True,
                       env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    passed = r.returncode == 0
    out = r.stdout + r.stderr
    if passed:
        print("  [NEAR-MISS GATE] test PASSED — *** VERIFIER TOO WEAK *** (near-miss wrongly passes)")
        # show what it asserted
        for l in out.splitlines():
            if "assert" in l.lower() or "cipher" in l.lower():
                print(f"    {l.strip()[:110]}")
        sys.exit(1)
    else:
        print("  [NEAR-MISS GATE] test FAILED as expected — verifier catches behaviorally-wrong impl ✓")
        for l in out.splitlines():
            if "assert" in l.lower() and ("cipher" in l.lower() or "is_not" in l or "None" in l):
                print(f"    (caught at: {l.strip()[:110]})")
                break
        sys.exit(0)

if __name__ == "__main__":
    main()
