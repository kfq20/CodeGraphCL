"""Phase 5 stream runner: run Reset vs Stateful on a stream of tasks.

Reset: each task gets a fresh claude session (no history from prior tasks in the stream).
Stateful: tasks share one continuous claude session (the agent sees prior conversation history).

This is different from intervene (which runs single-edge episodes with experience atoms).
Here we run actual task sequences (streams) measuring whether the agent naturally acquires
and applies experience across tasks within one session.

Usage:
  python3 -m codegraphcl run-stream --stream-id <id> --model <model> --condition <reset|stateful> [--seed 42]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmark"


def _load_task(task_id: str) -> dict:
    """Load a task.yaml and return its config."""
    import yaml
    td = BENCH / "tasks" / task_id
    cfg = yaml.safe_load((td / "task.yaml").read_text())
    return cfg, td


def _find_container(image: str) -> str:
    """Find a running container matching the image."""
    r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=20)
    for name in r.stdout.splitlines():
        name = name.strip()
        if not name: continue
        ri = subprocess.run(["docker", "inspect", "-f", "{{.Config.Image}}", name], capture_output=True, text=True, timeout=15)
        cimg = ri.stdout.strip()
        if cimg == image or cimg.startswith(image) or image in cimg:
            return name
    return ""


def _resolve_pool(cname: str) -> str:
    """Find the host dir that container `cname` binds at /pool."""
    env_pool = os.environ.get("CGCL_POOL")
    if env_pool:
        return env_pool
    import os.path as _op
    import uuid as _uuid
    if cname:
        cands = []
        for d in ["/tmp/cgcl_box_pool", "/tmp/cgcl_fs_pool", "/tmp/cgcl_httpx_pool", "/tmp/cgcl_mat_pool"]:
            if _op.isdir(d) and os.access(d, os.W_OK): cands.append(d)
        vepfs = "/vePFS-Mindverse/user/intern/fanqi/cgcl_pools"
        if _op.isdir(vepfs):
            for sub in ("fs", "rg", "httpx", "mat", "viper"):
                d = f"{vepfs}/{sub}"
                if _op.isdir(d) and os.access(d, os.W_OK): cands.append(d)
        if cands:
            probe = f".poolprobe_{_uuid.uuid4().hex[:8]}"
            try:
                subprocess.run(["docker", "exec", cname, "bash", "-c", f"touch /pool/{probe}; sync"],
                               capture_output=True, text=True, timeout=20)
            except Exception: pass
            time.sleep(0.5)
            for d in cands:
                if _op.exists(f"{d}/{probe}"):
                    try: os.remove(f"{d}/{probe}")
                    except Exception: pass
                    return d
    return "/tmp/cgcl_box_pool"


_BUILD_CACHE_DIRS = ("node_modules", "target", ".venv", "venv", "__pypackages__")


def _rematerialize_shared_work(cfg, work, cache_root):
    """Replace the shared stateful work tree with THIS task's repo at base_commit.

    The shared cwd path is constant across the whole stream (so --resume keeps working),
    but the code tree is fully swapped per task: we blow away all contents (tracked files,
    .git, untracked agent edits, staged verifier/) and re-copy from the task's own clone,
    then checkout base_commit. Build caches (node_modules/target/...) are saved to and
    restored from a per-repo side cache (keyed by repo+base_commit), so single-repo streams
    reuse their install across tasks and avoid a cold npm/cargo install every swap.
    """
    from .materialize import _local_clone, _git
    clone = _local_clone(cfg)
    if not clone:
        return False
    repo_url = cfg.get("repository", {}).get("url", "")
    repo_name = repo_url.rstrip("/").split("/")[-1] if repo_url else "anon"
    base = cfg["repository"]["base_commit"]
    cache_slot = cache_root / f"{repo_name}_{base[:10]}"
    cache_slot.mkdir(parents=True, exist_ok=True)

    # ensure the shared cwd exists (first task of a stream: work may not exist yet)
    work.mkdir(parents=True, exist_ok=True)
    # 1) save build caches currently in the work tree to the side cache
    for d in _BUILD_CACHE_DIRS:
        wd = work / d
        if wd.exists() and wd.is_dir() and not wd.is_symlink():
            cslot = cache_slot / d
            if cslot.exists():
                shutil.rmtree(cslot, ignore_errors=True)
            try:
                shutil.move(str(wd), str(cslot))
            except Exception:
                pass
    # 2) wipe everything else under the shared cwd (tracked files, .git, agent edits, ...)
    # IMPORTANT: handle symlinks explicitly — a symlink-to-dir (e.g. ripgrep's HomebrewFormula
    # -> pkg/brew) reports is_dir()==True, so shutil.rmtree would follow it and wipe the LINK
    # TARGET, leaving a dangling symlink that breaks the re-copy (Errno 17). Unlink symlinks
    # in place instead; only rmtree real directories.
    for p in list(work.iterdir()):
        if p.is_symlink():
            try: p.unlink()
            except Exception: pass
        elif p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            try: p.unlink()
            except Exception: pass
    # 3) re-copy this task's repo (tracked tree + .git)
    shutil.copytree(clone, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
    shutil.copytree(clone / ".git", work / ".git", dirs_exist_ok=True)
    _git(["checkout", "-q", "-f", base], work)
    _git(["clean", "-fdxq", "--", "tests/"], work)
    # 4) restore build caches from the side cache into the fresh work tree
    for d in _BUILD_CACHE_DIRS:
        cslot = cache_slot / d
        if cslot.exists() and cslot.is_dir():
            try:
                shutil.move(str(cslot), str(work / d))
            except Exception:
                pass
    return True


def _run_task_episode(cfg, td, cname, pool_host, model, stream_id, task_idx, condition,
                      prev_session_id=None, shared_work=None, cache_root=None,
                      out_root=None) -> dict:
    """Run one task as a claude agent episode. Returns result dict.

    Reset: fresh session, per-task work dir.
    Stateful: ONE shared cwd (shared_work) for the whole stream. The code tree is
              rematerialized to each task's own repo+base_commit before its agent runs
              (session carries, code edits do NOT). --resume works because cwd is constant.
              Build caches are preserved across swaps via cache_root (per repo+base_commit).
    """
    from .materialize import _local_clone, _git, _container_exec
    clone = _local_clone(cfg)
    if not clone:
        return {"reward": "ERR", "outcome": "infra_fail", "error": "no clone"}

    if condition == "stateful" and shared_work is not None:
        # shared cwd for the whole stream — rematerialize to THIS task's repo+base
        if not _rematerialize_shared_work(cfg, shared_work, cache_root):
            return {"reward": "ERR", "outcome": "infra_fail", "error": "no clone"}
        work = shared_work
        # shared_work lives under the /stateful shared mount, so the container sees it at
        # /stateful/<stream>/work (every repo container has /stateful bind-mounted in).
        st_root = Path(os.environ.get("CGCL_STATEFUL_ROOT", "/vePFS-Mindverse/user/intern/fanqi/cgcl_stateful"))
        if str(work).startswith(str(st_root)):
            container_work = "/stateful" + str(work).replace(str(st_root), "", 1)
        else:
            container_work = f"/pool/{stream_id}_shared/work"
        # per-task out dir lives under the namespaced out root created by cmd_run_stream
        out = out_root / f"t{task_idx:02d}"; out.mkdir()
    else:
        epid = f"{stream_id}_t{task_idx:02d}"
        ep_host = pool_host / epid
        if ep_host.exists():
            shutil.rmtree(ep_host)
        work = ep_host / "work"; work.mkdir(parents=True)
        out = ep_host / "out"; out.mkdir()
        container_work = f"/pool/{epid}/work"
        shutil.copytree(clone, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
        shutil.copytree(clone / ".git", work / ".git", dirs_exist_ok=True)
        _git(["checkout", "-q", "-f", cfg["repository"]["base_commit"]], work)
        _git(["clean", "-fdxq", "--", "tests/"], work)

    # NOTE: verifier/ is deliberately NOT staged here. It is injected AFTER the agent phase
    # (see "inject verifier" below) so the agent cannot read verifier/test.sh comments that
    # leak the gold mechanism or anti-hardcoding axes. This matches harbor's isolation
    # (agent phase sees no /tests; verifier phase gets its own tests).

    # build prompt
    instr = (td / cfg["instruction"]["path"]).read_text().strip()
    docker_hint = (
        "You are working in the repository at your current directory. To run the project's "
        "tests (in the prepared container env, not on the host), use:\n"
        f"  docker exec {cname} bash -c 'cd {container_work} && ...'\n"
        "Do NOT modify files under tests/ — the verifier applies its own tests after you finish. "
        "When done, output a one-line summary."
    )
    prompt = f"{instr}\n\n---\n{docker_hint}"

    (out / "manifest.json").write_text(json.dumps({
        "stream_id": stream_id, "task_idx": task_idx, "task_id": cfg.get("task_id", ""),
        "condition": condition, "model": model,
        "prev_session_id": prev_session_id or "",
        "base_commit": cfg["repository"]["base_commit"],
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()[:12],
    }, indent=2))
    (out / "prompt.txt").write_text(prompt)

    # agent phase
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://mintcn.macaron.xin")
    auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
    export = f"ANTHROPIC_BASE_URL={base_url} ANTHROPIC_AUTH_TOKEN={auth_token}"
    allow = "--allowedTools Read,Write,Edit,Bash,Glob,Grep,LS"
    prompt_file = out / "prompt.txt"

    resume_flag = ""
    session_id_out = ""
    if condition == "stateful" and prev_session_id:
        resume_flag = f"--resume {prev_session_id}"
    elif condition == "stateful":
        # first task in a stateful stream — start a new session
        pass

    start = time.time()
    # Use -s KILL: claude ignores SIGTERM on endpoint hangs, so a soft timeout leaves zombie
    # processes that block the batch. SIGKILL is the only thing that reliably reaps them.
    agent_cmd = (f"{export} timeout -s KILL 600 claude -p --model {model} --output-format stream-json "
                 f"--verbose {allow} {resume_flag} < {prompt_file}")
    try:
        with open(out / "agent.jsonl", "w") as af, open(out / "agent.stderr", "w") as ef:
            r = subprocess.run(agent_cmd, shell=True, cwd=str(work), stdout=af, stderr=ef, timeout=620)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        # outer backstop: kill the whole process group if inner timeout -s KILL somehow missed
        rc = 137
    elapsed = int(time.time() - start)

    # extract session_id from agent.jsonl (first system event)
    session_id = ""
    try:
        for line in (out / "agent.jsonl").read_text().splitlines():
            d = json.loads(line)
            if d.get("type") == "system" and d.get("session_id"):
                session_id = d["session_id"]
                break
    except Exception:
        pass

    # parse usage
    tools = turns = in_t = out_t = cr = 0
    try:
        for line in (out / "agent.jsonl").read_text().splitlines():
            d = json.loads(line)
            if d.get("type") == "result":
                u = d.get("usage", d.get("modelUsage", {}))
                in_t = u.get("input_tokens", u.get("inputTokens", 0))
                out_t = u.get("output_tokens", u.get("outputTokens", 0))
                cr = u.get("cache_read_input_tokens", u.get("cacheReadInputTokens", 0))
            if d.get("type") == "assistant":
                turns += 1
                tc = d.get("message", {}).get("content", [])
                if isinstance(tc, list):
                    tools += sum(1 for c in tc if isinstance(c, dict) and c.get("type") == "tool_use")
    except Exception:
        pass

    (out / "agent_meta.txt").write_text(
        f"rc={rc}\nelapsed_sec={elapsed}\ncondition={condition}\ntask_id={cfg.get('task_id','')}\n"
        f"session_id={session_id}\ninput_tokens={in_t}\noutput_tokens={out_t}\n"
        f"cache_read_tokens={cr}\ntool_uses={tools}\nassistant_turns={turns}\n")

    # inject verifier + score — stage verifier AFTER the agent phase so the agent could
    # not read verifier/test.sh (which leaks the gold mechanism in comments).
    vdir = td / "verifier"
    if vdir.exists():
        (work / "verifier").mkdir(exist_ok=True)
        for f in vdir.iterdir():
            if f.is_file(): shutil.copy2(f, work / "verifier" / f.name)
    vpatch_rel = cfg.get("patches", {}).get("verifier")
    if vpatch_rel:
        _git(["apply", str(td / vpatch_rel)], work)
        time.sleep(1.0)
    vcmd = cfg["verifier"]["command"]
    vtimeout = cfg["verifier"]["timeout_sec"]
    cargo_target = os.environ.get("CGCL_CARGO_TARGET_DIR", "/pool/.cargo_target")
    env_prefix = (f"HARBOR_WORKDIR={container_work} HARBOR_TESTS_DIR={container_work}/verifier "
                  f"HARBOR_LOGS_DIR={container_work}/.logs CARGO_TARGET_DIR={cargo_target} ")
    rf = work / ".logs" / "verifier" / "reward.txt"
    rf.parent.mkdir(parents=True, exist_ok=True)
    if rf.exists(): rf.write_text("")
    rc_v, _ = _container_exec(cname, env_prefix + vcmd,
                              [(str(work), container_work)], container_work, timeout=vtimeout)
    (out / "verify.log").write_text("")
    reward = "ERR"
    if rf.exists():
        reward = rf.read_text().strip()

    # classify outcome
    if reward == "ERR": outcome = "infra_fail"
    elif rc == 124 and reward in ("1", "0"): outcome = "timeout_solved" if reward == "1" else "timeout_failed"
    elif reward == "1": outcome = "solved"
    elif reward == "0": outcome = "agent_fail"
    else: outcome = "infra_fail"

    return {
        "task_id": cfg.get("task_id", ""), "reward": reward, "outcome": outcome,
        "elapsed_sec": elapsed, "input_tokens": in_t, "output_tokens": out_t,
        "cache_read_tokens": cr, "tool_uses": tools, "assistant_turns": turns,
        "rc": rc, "session_id": session_id,
    }


def cmd_run_stream(args):
    """Run a stream of tasks in Reset or Stateful mode."""
    # load stream
    stream_file = None
    for d in [BENCH / "streams" / "diagnostic", BENCH / "streams" / "integrated"]:
        for f in d.glob("*.jsonl"):
            for line in f.read_text().strip().splitlines():
                s = json.loads(line)
                if s.get("stream_id") == args.stream_id:
                    stream_file = f
                    stream = s
                    break
    if not stream_file:
        print(f"stream {args.stream_id} not found"); return 1

    task_ids = stream["task_ids"]
    motif = stream.get("motif", stream.get("motifs_used", ["unknown"])[0] if "motifs_used" in stream else "unknown")
    print(f"=== run-stream: {args.stream_id} ({motif}) ===")
    print(f"  model={args.model} condition={args.condition} tasks={task_ids}")

    results = []
    prev_session = None

    # For stateful: ONE shared cwd for the whole stream (so --resume keeps working; claude
    # sessions are keyed by cwd). The shared cwd lives under the /stateful shared mount,
    # which is bind-mounted into EVERY repo container — so a multi-repo stream can run
    # each task's verifier in its own toolchain container while keeping the session on a
    # constant host path. The code tree is rematerialized to each task's repo+base_commit.
    shared_work = None
    cache_root = None
    out_root = None
    if args.condition == "stateful":
        st_root = Path(os.environ.get("CGCL_STATEFUL_ROOT",
                                        "/vePFS-Mindverse/user/intern/fanqi/cgcl_stateful"))
        # namespace by stream+model+seed so concurrent/sequential runs of the same stream
        # under different models don't clobber each other's shared cwd or out dirs
        ns = f"{args.stream_id}__{args.model.replace('/', '_')}__seed{args.seed}"
        shared_host = st_root / ns
        if shared_host.exists():
            shutil.rmtree(shared_host)
        shared_work = shared_host / "work"
        shared_work.mkdir(parents=True)
        out_root = st_root / f"{ns}_out"
        if out_root.exists():
            shutil.rmtree(out_root)
        out_root.mkdir(parents=True)
        # per-repo build-cache dir (shared across streams; cache slots are keyed by repo+base)
        cache_root = st_root / "_buildcache"
        cache_root.mkdir(parents=True, exist_ok=True)
        print(f"  stateful shared work: {shared_work}")

    for idx, tid in enumerate(task_ids):
        cfg, td = _load_task(tid)
        cname = _find_container(cfg["environment"]["image"])
        if not cname:
            print(f"  no container for {cfg['environment']['image']}"); return 1
        pool_host = Path(_resolve_pool(cname))

        print(f"  [{idx+1}/{len(task_ids)}] {tid} (cond={args.condition})...", end="", flush=True)
        r = _run_task_episode(cfg, td, cname, pool_host, args.model, args.stream_id, idx,
                              args.condition, prev_session_id=prev_session,
                              shared_work=shared_work, cache_root=cache_root,
                              out_root=out_root)
        results.append(r)

        # for stateful: carry the session_id forward
        if args.condition == "stateful" and r.get("session_id"):
            prev_session = r["session_id"]

        print(f" reward={r['reward']} outcome={r['outcome']} elapsed={r['elapsed_sec']}s turns={r['assistant_turns']}")

    # write results CSV
    run_dir = ROOT / "runs" / f"phase5_{args.stream_id}_{args.model}_{args.condition}_seed{args.seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    csv_path = run_dir / "results.csv"
    with csv_path.open("w") as f:
        f.write("task_idx,task_id,reward,outcome,elapsed_sec,input_tokens,output_tokens,cache_read_tokens,tool_uses,assistant_turns,session_id\n")
        for idx, r in enumerate(results):
            f.write(f"{idx},{r['task_id']},{r['reward']},{r['outcome']},{r['elapsed_sec']},"
                    f"{r['input_tokens']},{r['output_tokens']},{r['cache_read_tokens']},"
                    f"{r['tool_uses']},{r['assistant_turns']},{r.get('session_id','')}\n")

    solved = sum(1 for r in results if r["reward"] == "1")
    print(f"\n  results: {solved}/{len(results)} solved -> {csv_path}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stream-id", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--condition", required=True, choices=["reset", "stateful"])
    ap.add_argument("--seed", type=int, default=42)
    sys.exit(cmd_run_stream(ap.parse_args()))
