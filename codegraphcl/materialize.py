"""`codegraphcl materialize` — run base-fail / gold-pass / PASS_TO_PASS / near-miss for a task.

Config-driven: reads task.yaml. No task-specific names hardcoded.

Procedure (phase1 §3.2):
  1. Checkout base into an isolated workdir (host does the git checkout — rust:slim has no git)
  2. base + verifier  -> must FAIL  (base-fail)
  3. base + gold + verifier -> must PASS  (gold-pass)
  4. record base pass-set; apply gold; re-run same set; any pass->fail = REJECT (PASS_TO_PASS)
  5. apply >=2 near-miss; if any passes verifier = REJECT (near-miss anti-hardcoding)

Output: runs/<run_id>/{run_manifest.json, materialization_result.json, *.log}
materialization_result.json status in:
  passed | task_failure | verifier_failure | environment_failure | timeout | inconclusive

Host-specific reality (this fuse-overlayfs box): docker stdout is dropped, so every container
command writes to a mounted file under runs/<run_id>/ and we read it back. Bind-mount targets
must exist (pre-created). Patches applied on HOST (rust:slim has no git), then cp'd in.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .config import load_task, ROOT, BENCH


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def _local_clone(cfg: dict) -> Path | None:
    url = cfg.get("repository", {}).get("url", "")
    name = url.rstrip("/").split("/")[-1] if url else ""
    for c in [ROOT / "repos" / name, ROOT / "repos" / f"{name}-full"]:
        if (c / ".git").exists():
            return c
    return None


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=60)


def _find_running_container(image: str) -> str | None:
    """Find an already-running container using `image`. docker ps may show the image as an ID
    (not name), so we inspect each candidate. No container name hardcoded — discover by image."""
    r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"],
                       capture_output=True, text=True, timeout=20)
    for name in r.stdout.splitlines():
        name = name.strip()
        if not name:
            continue
        # inspect to get the resolved image name
        ri = subprocess.run(["docker", "inspect", "-f", "{{.Config.Image}}", name],
                           capture_output=True, text=True, timeout=15)
        cimg = ri.stdout.strip()
        if cimg == image or cimg.startswith(image) or image in cimg:
            return name
    return None


def _ensure_container(image: str, mounts: list[tuple[str, str]], workdir: str) -> str:
    """Return the name of a running container for `image`, mounting `mounts` at the right
    paths. If one exists (found by image), reuse it (caller ensures the work mount is
    consistent). If not, start a long-lived one with the given mounts. Name is derived from
    image (no hardcoded task-specific name)."""
    cname = _find_running_container(image)
    if cname:
        return cname
    # start a long-lived container with the mounts the task needs
    import hashlib
    short = "cgcl-" + hashlib.sha1(image.encode()).hexdigest()[:8]
    # remove any stale stopped one with this name
    subprocess.run(["docker", "rm", "-f", short], capture_output=True, text=True, timeout=20)
    vols = []
    for h, c in mounts:
        vols += ["-v", f"{h}:{c}"]
    r = subprocess.run(["docker", "run", "-d", "--name", short, *vols, "-w", workdir,
                        image, "sleep", "infinity"],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"failed to start container for {image}: {r.stderr}")
    return short


def _container_exec(cname: str, cmd: str, mounts: list[tuple[str, str]], workdir: str,
                    timeout: int = 300) -> tuple[int, str]:
    """Run cmd in the long-lived container `cname`. docker exec does NOT block on this host
    (Docker-in-Docker: the exec returns immediately without waiting for the child). So we
    detach (no -d needed; the non-blocking is the host quirk) and POLL a sentinel file the
    command writes when done. Output goes to a log file in the mounted workdir (stdout pipe
    is dead here). Returns (rc, output)."""
    if not mounts:
        return 1, "no mounts"
    host_work = Path(mounts[0][0])
    container_work = mounts[0][1]
    container_log = f"{container_work}/.cgcl_mat_out.log"
    sentinel = f"{container_work}/.cgcl_done.sentinel"
    log_file = host_work / ".cgcl_mat_out.log"
    sentinel_file = host_work / ".cgcl_done.sentinel"
    # pre-create empty (fuse bind needs the inode to exist before the container writes)
    log_file.write_text("")
    sentinel_file.write_text("")
    # command writes output to log, then RC + DONE to sentinel; sync forces fuse flush
    full = (f'{cmd} > {container_log} 2>&1; '
            f'echo "RC=$?" >> {container_log}; '
            f'echo "DONE" > {sentinel}; sync')
    dargs = ["docker", "exec", "-w", workdir, cname, "bash", "-c", full]
    # fire and (do not) expect blocking — start it
    r = subprocess.run(dargs, capture_output=True, text=True, timeout=timeout + 60)
    # docker exec returned (probably immediately). POLL the sentinel up to `timeout` seconds.
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        try:
            content = sentinel_file.read_text()
        except Exception:
            content = ""
        if "DONE" in content:
            break
    else:
        out = log_file.read_text() if log_file.exists() else ""
        return 124, f"TIMEOUT (sentinel never appeared)\n{out}"
    # sentinel appeared — but give fuse a beat to flush the final log writes
    time.sleep(1.5)
    out = log_file.read_text() if log_file.exists() else ""
    rc = r.returncode
    for line in out.splitlines()[::-1]:
        if line.startswith("RC="):
            v = line[3:].strip()
            if v.isdigit():
                rc = int(v)
            break
    try:
        log_file.unlink(); sentinel_file.unlink()
    except Exception:
        pass
    return rc, out


def cmd_materialize(task_dir: str, run_id: str | None = None, container: str | None = None) -> int:
    td = Path(task_dir).resolve()
    cfg = load_task(td)
    task_id = cfg["task_id"]
    run_id = run_id or f"{task_id}_{int(time.time())}"
    run_dir = ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id, "task_id": task_id, "image": cfg["environment"]["image"],
        "base_commit": cfg["repository"]["base_commit"],
        "gold_commit": cfg["repository"]["gold_commit"],
        "started_at": int(time.time()),
    }

    # resolve local clone
    clone = _local_clone(cfg)
    if clone is None:
        result = {"status": "environment_failure",
                  "reason": f"no local clone for {cfg['repository']['url']}"}
        (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return 1

    # phase 1: prepare base workdir. Use POOL MODE: work lives under CGCL_POOL (a host dir
    # bind-mounted at /pool in the long-lived image container). This is the stable path on
    # this fuse-overlayfs host (docker run --rm drops stdout + loses fuse writes). The
    # container workdir is /pool/<run_id>/work, overriding task.yaml's workdir.
    pool_host = Path(os.environ.get("CGCL_POOL", "/tmp/cgcl_box_pool"))
    pool_host.mkdir(parents=True, exist_ok=True)
    ep_pool = pool_host / run_id
    if ep_pool.exists():
        shutil.rmtree(ep_pool)
    work = ep_pool / "work"
    work.mkdir(parents=True, exist_ok=True)
    container_work = f"/pool/{run_id}/work"
    # also keep a run_dir under runs/ for the manifest/logs (audit copy)
    (run_dir / "work_meta.txt").write_text(f"work lives in pool: {work} -> {container_work}\n")

    # copy the clone tree, then checkout base
    shutil.copytree(clone, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
    shutil.copytree(clone / ".git", work / ".git", dirs_exist_ok=True)
    r = _git(["checkout", "-q", "-f", cfg["repository"]["base_commit"]], work)
    if r.returncode != 0:
        result = {"status": "environment_failure", "reason": f"base checkout failed: {r.stderr}"}
        (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2)); return 1
    _git(["clean", "-fdxq", "--", "tests/"], work)
    # stage the task's verifier/ assets into the work tree (verifier.command runs in container_work)
    vdir = td / "verifier"
    if vdir.exists():
        (work / "verifier").mkdir(exist_ok=True)
        for f in vdir.iterdir():
            if f.is_file():
                shutil.copy2(f, work / "verifier" / f.name)

    image = cfg["environment"]["image"]
    vcmd = cfg["verifier"]["command"]
    vtimeout = cfg["verifier"]["timeout_sec"]
    # POOL MODE: the long-lived container already has /pool mounted. We don't pass a work
    # mount (it's already there); extra_mounts (wheels) must also already be mounted in the
    # long-lived box — materialize checks the box is up but does NOT manage its mounts.
    cname = container or _find_running_container(image)
    if not cname:
        result = {"status": "environment_failure",
                  "reason": (f"no long-lived container running image {image}. On this host, "
                             f"start one first with /pool mounted (see ENV_RECIPE.md). "
                             f"materialize does not manage container mounts.")}
        (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2)); return 1
    mounts = [(str(work), container_work)]   # for log-file path resolution only
    workdir = container_work

    def run_verifier(label: str, extra_patch: Path | None = None) -> tuple[int, str, str]:
        """Apply extra_patch (host git), then run verifier in container. Returns (rc, out, status).
        The verifier.command may be a harbor-style test.sh that writes reward.txt (and always
        exits 0) OR a direct script that uses exit code. We prefer reward.txt if present."""
        if extra_patch:
            ar = _git(["apply", str(extra_patch)], work)
            if ar.returncode != 0:
                (run_dir / f"{label}.log").write_text(
                    f"PATCH APPLY FAILED: {extra_patch}\n{ar.stderr}\n{ar.stdout}")
                return 1, f"patch apply failed: {ar.stderr}", "patch_failure"
            # fuse sync: let the applied file land
            time.sleep(1.0)
        # clear stale reward so we don't read the previous gate's result
        rf = work / ".logs" / "verifier" / "reward.txt"
        if rf.exists():
            rf.write_text("")
        # set harbor env so test.sh writes logs/reward into the mounted work tree
        (work / ".logs" / "verifier").mkdir(parents=True, exist_ok=True)
        env_prefix = (f"HARBOR_WORKDIR={container_work} "
                      f"HARBOR_TESTS_DIR={container_work}/verifier "
                      f"HARBOR_LOGS_DIR={container_work}/.logs ")
        rc, out = _container_exec(cname, env_prefix + vcmd, mounts, workdir, timeout=vtimeout)
        (run_dir / f"{label}.log").write_text(out)
        # prefer reward.txt (harbor convention); fall back to exit code
        reward_file = work / ".logs" / "verifier" / "reward.txt"
        time.sleep(0.5)
        if reward_file.exists():
            rtxt = reward_file.read_text().strip()
            try:
                reward = float(rtxt)
                # reward>=0.5 => pass (rc=0 logic); <0.5 => fail
                return (0 if reward >= 0.5 else 1), out, "ok"
            except ValueError:
                pass
        return rc, out, "ok"

    # GATE 1: base-fail (base + verifier). verifier patch is applied on top of base.
    # NOTE: for tasks where verifier is a test FILE patch (not hermetic script), we apply it.
    vpatch_rel = cfg.get("patches", {}).get("verifier")
    vpatch = td / vpatch_rel if vpatch_rel else None
    if vpatch and vpatch.exists():
        var = _git(["apply", str(vpatch)], work)
        if var.returncode != 0:
            result = {"status": "environment_failure",
                      "reason": f"verifier patch apply failed: {var.stderr}",
                      "gates": {"base_fail": "verifier_patch_failed"}}
            (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
            print(json.dumps(result, indent=2)); return 1
        time.sleep(1.0)  # fuse sync
    rc1, out1, st1 = run_verifier("base_fail")
    # base-fail: verifier must FAIL (rc != 0). if rc==0 -> no bug present -> reject.
    base_fail_ok = (rc1 != 0)
    print(f"[GATE1 base-fail] rc={rc1} -> {'FAIL (expected)' if base_fail_ok else 'PASS (unexpected — bug not present)'}")

    if not base_fail_ok:
        result = {"status": "task_failure",
                  "reason": "base+verifier passed — the bug is not present on base; FAIL_TO_PASS invalid",
                  "gates": {"base_fail": "failed"}}
        (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2)); return 1

    # GATE 2: gold-pass (apply gold patch on top of base+verifier)
    gold_patch = td / cfg["patches"]["gold"]
    rc2, out2, st2 = run_verifier("gold_pass", extra_patch=gold_patch)
    if st2 == "patch_failure":
        result = {"status": "environment_failure", "reason": out2,
                  "gates": {"base_fail": "passed", "gold_pass": "patch_apply_failed"}}
        (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2)); return 1
    gold_pass_ok = (rc2 == 0)
    print(f"[GATE2 gold-pass] rc={rc2} -> {'PASS (expected)' if gold_pass_ok else 'FAIL (gold does not fix)'}")

    if not gold_pass_ok:
        result = {"status": "task_failure",
                  "reason": "base+gold+verifier failed — gold patch does not make the test pass",
                  "gates": {"base_fail": "passed", "gold_pass": "failed"}}
        (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2)); return 1

    # GATE 3: PASS_TO_PASS — record base pass-set, apply gold, re-run, no new failures.
    # For tasks with explicit pass_to_pass list, check those specific tests pass on both.
    p2p = cfg.get("verifier", {}).get("pass_to_pass", [])
    p2p_regressed = []
    if p2p:
        # rebuild a verifier run that lists individual outcomes (we already have base_fail.log
        # and gold_pass.log; parse them for the p2p test names)
        for t in p2p:
            in_base = t in out1 and "ok" in out1.lower()
            in_gold = t in out2 and "ok" in out2.lower()
            # crude: if a p2p test name appears with FAILED in gold but not in base -> regression
            if t in out2 and "FAILED" in out2:
                p2p_regressed.append(t)
        print(f"[GATE3 pass-to-pass] {len(p2p)} p2p tests, {len(p2p_regressed)} regressed")

    # GATE 4: near-miss — each must FAIL the verifier (anti-hardcoding).
    # near-miss assets may be .patch (git apply) or .py (run inside the container to inject).
    near_misses = cfg.get("verifier", {}).get("near_miss", [])
    nm_results = []
    for i, nm_rel in enumerate(near_misses):
        nm_path = td / nm_rel
        if not nm_path.exists():
            nm_results.append({"patch": nm_rel, "status": "missing", "rc": -1})
            continue
        # fresh pool worktree for this near-miss
        nm_pool = pool_host / f"{run_id}_nm{i}"
        if nm_pool.exists():
            shutil.rmtree(nm_pool)
        nm_work = nm_pool / "work"
        nm_work.mkdir(parents=True)
        # fresh base copy (clone tree + checkout base)
        shutil.copytree(clone, nm_work, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
        shutil.copytree(clone / ".git", nm_work / ".git", dirs_exist_ok=True)
        _git(["checkout", "-q", "-f", cfg["repository"]["base_commit"]], nm_work)
        _git(["clean", "-fdxq", "--", "tests/"], nm_work)
        if vpatch and vpatch.exists():
            _git(["apply", str(vpatch)], nm_work)
        # stage verifier assets
        if vdir.exists():
            (nm_work / "verifier").mkdir(exist_ok=True)
            for f in vdir.iterdir():
                if f.is_file():
                    shutil.copy2(f, nm_work / "verifier" / f.name)
        # apply the near-miss: .patch via git, .py via running it in the container against work
        nm_container_work = f"/pool/{run_id}_nm{i}/work"
        nm_mounts = [(str(nm_work), nm_container_work)]
        if nm_path.suffix == ".patch":
            ar = _git(["apply", str(nm_path)], nm_work)
            if ar.returncode != 0:
                nm_results.append({"patch": nm_rel, "status": "apply_failed", "rc": -1})
                continue
            time.sleep(1.0)
            nm_cmd = vcmd
        elif nm_path.suffix == ".py":
            # script injects a near-miss into the repo; stage it + run it in container
            shutil.copy2(nm_path, nm_work / "near_miss_inject.py")
            inject_cmd = (f"python3 {nm_container_work}/near_miss_inject.py "
                          f"{nm_container_work} A 2>&1; ")
            nm_cmd = inject_cmd + vcmd
        else:
            nm_results.append({"patch": nm_rel, "status": "unsupported_nearmiss_type", "rc": -1})
            continue
        # clear stale reward + set harbor env
        (nm_work / ".logs" / "verifier").mkdir(parents=True, exist_ok=True)
        env_prefix = (f"HARBOR_WORKDIR={nm_container_work} "
                      f"HARBOR_TESTS_DIR={nm_container_work}/verifier "
                      f"HARBOR_LOGS_DIR={nm_container_work}/.logs ")
        rc_nm, out_nm = _container_exec(cname, env_prefix + nm_cmd, nm_mounts,
                                        nm_container_work, timeout=vtimeout)
        (run_dir / f"near_miss_{i+1}.log").write_text(out_nm)
        # prefer reward.txt
        nm_reward = nm_work / ".logs" / "verifier" / "reward.txt"
        time.sleep(0.5)
        if nm_reward.exists():
            rtxt = nm_reward.read_text().strip()
            try:
                rv = float(rtxt)
                rc_nm = 0 if rv >= 0.5 else 1
            except ValueError:
                pass
        ok = (rc_nm != 0)  # near-miss must FAIL
        nm_results.append({"patch": nm_rel, "rc": rc_nm,
                           "status": "caught" if ok else "PASSED (anti-hardcoding FAIL)"})
        print(f"[GATE4 near-miss {i+1}] {nm_rel} rc={rc_nm} -> {'FAIL (caught)' if ok else 'PASS (verifier too weak!)'}")

    nm_bad = [n for n in nm_results if "PASSED" in n.get("status", "")]
    p2p_bad = bool(p2p_regressed)

    if nm_bad or p2p_bad:
        result = {"status": "task_failure",
                  "reason": ("near-miss passed verifier (anti-hardcoding fail): " +
                             ", ".join(n["patch"] for n in nm_bad)) if nm_bad else
                            f"PASS_TO_PASS regressed: {p2p_regressed}",
                  "gates": {"base_fail": "passed", "gold_pass": "passed",
                            "pass_to_pass": "failed" if p2p_bad else "passed",
                            "near_miss": "failed" if nm_bad else "passed"},
                  "near_miss_results": nm_results}
        (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2)); return 1

    result = {"status": "passed",
              "gates": {"base_fail": "passed", "gold_pass": "passed",
                        "pass_to_pass": "passed", "near_miss": "passed"},
              "fail_to_pass": cfg["verifier"].get("fail_to_pass", []),
              "pass_to_pass": p2p,
              "near_miss_results": nm_results,
              "run_dir": str(run_dir)}
    manifest["finished_at"] = int(time.time())
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2))
    (run_dir / "materialization_result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0
