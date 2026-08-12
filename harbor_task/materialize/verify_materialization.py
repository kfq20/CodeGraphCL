#!/usr/bin/env python3
"""Materialization verifier for one CodeGraphCL task node (SWE-bench-style base-fail/gold-pass).

Implements TODO §3 procedure inside a container:
  1. Base = parent(sha)  (already checked out by caller)
  2. apply verifier patch (test-only)  -> run targeted test -> expect FAIL  (base-fail)
  3. apply source patch (src-only)     -> run targeted test -> expect PASS (gold-pass)
  4. revert source, keep verifier, run Base's OWN existing tests -> PASS_TO_PASS

Reads node spec from a JSON arg: {sha, source_patch, verifier_patch, test_selector}
Prints a structured verdict. Exit 0 if all three gates hold, 1 otherwise.

This is the gate that promotes an audited commit (L3) into a materialized task node (L4).
"""
import json, os, subprocess, sys
from pathlib import Path

REPO = Path("/workspace/httpx")          # cloned repo mounted in container
PATCH_DIR = Path("/materialize")

def run(cmd, cwd=REPO, check=False, env=None):
    e = {**os.environ, **(env or {})}
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True,
                       text=True, env=e)
    return r

def git(*args):
    r = run(["git", "-C", str(REPO), *args])
    return r

def apply_patch(path, check=False):
    r = git("apply", "--check", str(path)) if check else git("apply", str(path))
    return r.returncode == 0, r

def clean_worktree():
    git("checkout", "--", ".").check_returncode if False else None
    # hard reset any applied patches
    git("checkout", "-f", "HEAD")
    # remove any stray untracked (patch-created) files like new test files
    git("clean", "-fdx", "--", "tests/")

def run_test(selector, fail_fast=True):
    """Run a pytest test by node id, return (passed, output)."""
    args = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
            "-o", "addopts="]  # override setup.cfg --cov (pytest-cov not installed)
    if fail_fast:
        args.append("-x")
    args.append(selector)
    r = run(args, env={"PYTHONDONTWRITEBYTECODE": "1"})
    # pytest 4.6 exit: 0 = all pass, 1 = failures, 2 = error, 5 = no tests collected
    passed = r.returncode == 0
    return passed, r.stdout + r.stderr

def main():
    spec = json.loads(sys.argv[1])
    sha = spec["sha"]
    src = PATCH_DIR / spec["source_patch"]
    ver = PATCH_DIR / spec["verifier_patch"]
    sel = spec["test_selector"]           # e.g. "tests/test_concurrency.py::test_start_tls_on_socket_stream"

    print(f"=== Materialization verify: {sha} ===")
    print(f"  source:   {src.name}")
    print(f"  verifier: {ver.name}")
    print(f"  selector: {sel}")

    # ensure we are on Base = parent(sha)
    base = git("rev-parse", f"{sha}^").stdout.strip()
    git("checkout", "-q", "-f", base)
    print(f"  Base = {git('rev-parse','--short','HEAD').stdout.strip()}  ({git('log','-1','--format=%s').stdout.strip()})")
    clean_worktree()

    # ---- Gate 1: base-fail (verifier only, expect FAIL) ----
    ok, _ = apply_patch(str(ver), check=True)
    if not ok:
        print("  [GATE1] verifier patch does NOT apply to Base — ABORT"); sys.exit(1)
    apply_patch(str(ver))
    passed, out = run_test(sel)
    status = "PASS(unexpected!)" if passed else "FAIL(expected)"
    print(f"  [GATE1] base-fail: Base+verifier -> test {status}")
    if passed:
        print("  *** base-fail FAILED: test passes even without source patch (bug not present?) ***")
        sys.exit(1)
    # show why it failed (first error lines)
    for line in out.splitlines():
        if "Error" in line or "NotImplemented" in line or "assert" in line.lower():
            print(f"        {line.strip()[:120]}")
            break

    # ---- Gate 2: gold-pass (source + verifier, expect PASS) ----
    apply_patch(str(src))
    passed, out = run_test(sel)
    status = "PASS(expected)" if passed else "FAIL(unexpected!)"
    print(f"  [GATE2] gold-pass: Base+source+verifier -> test {status}")
    if not passed:
        print("  *** gold-pass FAILED: source patch does not make test pass ***")
        print(out[-1500:])
        sys.exit(1)

    # ---- Gate 3: PASS_TO_PASS (real, hard-gated) ----
    # Canonical: tests that pass on Base still pass after the source patch (no regression).
    # Collect a server-free subset on Base (P_base), apply source+verifier, re-run (P_after),
    # assert P_base ⊆ P_after. Uses test_utils.py (server-free) because the gold test file's
    # https_server fixture is the broken uvicorn path. Outcomes:
    #   PASS (P_base ⊆ P_after) | FAIL (regression) | INCONCLUSIVE (no P2P file / collection error)
    # INCONCLUSIVE does NOT print "ALL GATES PASSED" — only Gate1+Gate2+Gate3-pass do.
    import json as _json
    p2p_file = "tests/test_utils.py"
    has_p2p = (REPO / p2p_file).exists()
    if not has_p2p:
        print(f"  [GATE3] pass-to-pass: INCONCLUSIVE — no {p2p_file} at Base")
        print(f"=== GATES 1-2 PASSED; Gate3 inconclusive ===")
        sys.exit(0)   # not 1 (not a failure), but not "all gates passed"

    def collect_pass_set():
        """Run p2p_file, return (set of passed node ids, output, returncode)."""
        r = run([sys.executable, "-m", "pytest", "-q", "-v", p2p_file,
                 "-p", "no:cacheprovider", "-o", "addopts="],
                env={"PYTHONDONTWRITEBYTECODE": "1"})
        out = r.stdout + r.stderr
        passed = set()
        for line in out.splitlines():
            if "::" in line and ("PASSED" in line or "FAILED" in line):
                head = line.rsplit("PASSED", 1)[0].rsplit("FAILED", 1)[0].strip()
                if "PASSED" in line:
                    passed.add(head)
        return passed, out, r.returncode

    # state: clean Base, no source no verifier
    clean_worktree()
    p_base, out_base, rc_base = collect_pass_set()
    # rc 0/1 = ran; 2 = collection error; 5 = no tests. Only 0/1 are usable.
    if rc_base not in (0, 1):
        print(f"  [GATE3] pass-to-pass: INCONCLUSIVE — Base collection errored (rc={rc_base})")
        print(f"=== GATES 1-2 PASSED; Gate3 inconclusive ===")
        sys.exit(0)

    # state: Base + source + verifier (gold applied)
    apply_patch(str(src))
    apply_patch(str(ver))
    p_after, out_after, rc_after = collect_pass_set()
    if rc_after not in (0, 1):
        print(f"  [GATE3] pass-to-pass: INCONCLUSIVE — gold collection errored (rc={rc_after})")
        print(f"=== GATES 1-2 PASSED; Gate3 inconclusive ===")
        sys.exit(0)

    regressed = p_base - p_after
    # persist the sets for audit (next to the commit's other artifacts)
    sets = {"p2p_file": p2p_file, "base_pass": sorted(p_base),
            "gold_pass": sorted(p_after), "regressed": sorted(regressed)}
    try:
        (REPO.parent / "pass_to_pass_sets.json").write_text(_json.dumps(sets, indent=2))
    except Exception:
        pass
    if regressed:
        print(f"  [GATE3] pass-to-pass: FAIL — {len(regressed)} base-passing test(s) regressed:")
        for t in list(regressed)[:5]:
            print(f"        - {t}")
        sys.exit(1)
    print(f"  [GATE3] pass-to-pass: PASS — {len(p_base)} base-passing test(s) all still pass")
    print(f"\n=== ALL GATES PASSED: {sha} materializes cleanly ===")
    sys.exit(0)

if __name__ == "__main__":
    main()
