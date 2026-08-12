"""`codegraphcl prompt-preview <edge.yaml>` + `codegraphcl intervene <edge.yaml> --n 1`.

prompt-preview: build the 4 condition prompts (reset/correct/irrelevant/wrong or stale)
from the edge's target task's instruction + atoms, and verify:
  - non-reset prefixes non-empty
  - 4 distinct prompt_sha256
  - instruction_sha256 identical across conditions
  - condition name does NOT appear in prompt text, episode id, or workdir path
  - save prefix_chars/prefix_sha256/prompt_sha256

intervene: run N agent episodes per condition, opaque ep_NNNNNN ids, condition only in an
agent-invisible manifest. Uses the sentinel-poll _container_exec from materialize for the
verifier; the agent (claude -p) runs on the host (macaron endpoint) with --allowedTools.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .config import load_task, ROOT, BENCH, _load_yaml, validate_against_schema


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _extract_atom(atoms_text: str, name: str) -> str:
    o, c = f"<!-- ATOM:{name} -->", f"<!-- /ATOM:{name} -->"
    i = atoms_text.find(o)
    if i < 0: return ""
    i += len(o)
    j = atoms_text.find(c, i)
    return atoms_text[i:j].strip() if j > 0 else ""


def _build_prompt(cfg: dict, td: Path, condition: str, container_workdir: str) -> tuple[str, dict]:
    """Build the prompt for a condition. Returns (prompt_text, manifest_fields)."""
    instr = (td / cfg["instruction"]["path"]).read_text().strip()
    atoms_path = td / "atoms.md"
    atoms = atoms_path.read_text() if atoms_path.exists() else ""
    # condition name -> atom name (edge may map e.g. stale->wrong)
    prefix = "" if condition == "reset" else _extract_atom(atoms, condition)
    if condition != "reset" and not prefix:
        raise ValueError(f"condition '{condition}' produced empty prefix — atom missing")
    docker_hint = (
        "You are working in the repository at your current directory. To run the project's "
        "tests (in the prepared container env, not on the host), use:\n"
        f"  docker exec cgcl-mat-box bash -c 'cd {container_workdir} && ...'\n"
        "Do NOT modify files under tests/ — the verifier applies its own tests after you finish. "
        "When done, output a one-line summary."
    )
    prompt = f"{prefix}\n\n---\n\n{instr}\n\n---\n{docker_hint}" if prefix else f"{instr}\n\n---\n{docker_hint}"
    return prompt, {
        "condition": condition,
        "prefix_chars": len(prefix),
        "prefix_sha256": _sha(prefix),
        "instruction_sha256": _sha(instr),
        "prompt_sha256": _sha(prompt),
        "container_workdir": container_workdir,
    }


def cmd_prompt_preview(edge_yaml: str) -> int:
    ep = Path(edge_yaml)
    if not ep.exists():
        print(f"no edge file: {ep}"); return 1
    ecfg = _load_yaml(ep)
    errs = validate_against_schema(ecfg, "edge")
    if errs:
        print("edge schema errors:"); [print(f"  {e}") for e in errs]; return 1
    # the edge's `to` task is the target; conditions map to atom names in that task's atoms.md
    target_id = ecfg["to"]
    td = BENCH / "tasks" / target_id
    if not (td / "task.yaml").exists():
        print(f"target task {target_id} not found"); return 1
    cfg = load_task(td)
    # conditions: reset + the 3 named in edge.yaml (correct/irrelevant/stale)
    cond_map = ecfg.get("conditions", {})
    conditions = ["reset", cond_map.get("correct") or "correct",
                  cond_map.get("irrelevant") or "irrelevant",
                  cond_map.get("stale") or "wrong"]
    container_workdir = f"/pool/<ep>/work"  # placeholder; intervene sets the real ep id
    print(f"=== prompt-preview: {ep.name} (target {target_id}) ===")
    manifests = {}
    prompts = {}
    for c in conditions:
        prompt, m = _build_prompt(cfg, td, c, container_workdir)
        prompts[c] = prompt
        manifests[c] = m
        print(f"  {c:12} prefix={m['prefix_chars']:4}c  prompt_sha={m['prompt_sha256'][:12]}  "
              f"instr_sha={m['instruction_sha256'][:12]}")
    # checks
    ok = True
    # 1. non-reset non-empty
    for c in conditions[1:]:
        if manifests[c]["prefix_chars"] == 0:
            print(f"FAIL: {c} empty prefix"); ok = False
    # 2. 4 distinct prompt hashes
    phashes = {c: manifests[c]["prompt_sha256"] for c in conditions}
    if len(set(phashes.values())) != 4:
        print(f"FAIL: prompt hashes not distinct"); ok = False
    # 3. instruction hash identical
    ishas = {c: manifests[c]["instruction_sha256"] for c in conditions}
    if len(set(ishas.values())) != 1:
        print(f"FAIL: instruction hashes differ"); ok = False
    # 4. condition name not in prompt text (whole-word match, not substring — 'correctly'
    #    is not the condition 'correct')
    import re as _re
    for c in conditions:
        if c == "reset":
            continue
        # whole-word, case-insensitive
        if _re.search(r'\b' + _re.escape(c) + r'\b', prompts[c], _re.IGNORECASE):
            print(f"FAIL: condition word '{c}' appears in prompt"); ok = False
    print(f"\nprompt-preview: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def _find_container(image: str) -> str | None:
    r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=20)
    for name in r.stdout.splitlines():
        name = name.strip()
        if not name: continue
        ri = subprocess.run(["docker", "inspect", "-f", "{{.Config.Image}}", name],
                           capture_output=True, text=True, timeout=15)
        cimg = ri.stdout.strip()
        if cimg == image or cimg.startswith(image) or image in cimg:
            return name
    return None


def cmd_intervene(edge_yaml: str, n: int = 1, seed: int = 42, conditions: list[str] | None = None) -> int:
    ep = Path(edge_yaml)
    ecfg = _load_yaml(ep)
    target_id = ecfg["to"]
    td = BENCH / "tasks" / target_id
    cfg = load_task(td)
    if conditions is None or conditions == ["reset,correct,irrelevant,wrong"]:
        cond_map = ecfg.get("conditions", {})
        conditions = ["reset", cond_map.get("correct") or "correct",
                      cond_map.get("irrelevant") or "irrelevant",
                      cond_map.get("stale") or "wrong"]
    image = cfg["environment"]["image"]
    cname = _find_container(image)
    if not cname:
        print(f"no running container for {image}"); return 1
    # block-randomized plan
    import random
    random.seed(seed)
    plan = []
    i = 0
    for b in range(n):
        order = conditions[:]; random.shuffle(order)
        for c in order:
            plan.append((f"ep_{i:06d}", c, b)); i += 1
    pool_host = Path(os.environ.get("CGCL_POOL", "/tmp/cgcl_box_pool"))
    results_csv = ROOT / "runs" / f"intervene_{Path(edge_yaml).stem}_seed{seed}" / "results.csv"
    results_csv.parent.mkdir(parents=True, exist_ok=True)
    if not results_csv.exists():
        results_csv.write_text("episode_id,condition,block,reward,outcome,elapsed_sec,input_tokens,"
                              "output_tokens,cache_read_tokens,tool_uses,assistant_turns,prefix_chars,prompt_sha256\n")
    print(f"=== intervene {ep.name}: N={n} seed={seed} container={cname} ===")
    for epid, cond, block in plan:
        print(f"--- {epid} (block {block}, cond={cond}) ---")
        rc = _run_episode(cfg, td, epid, cond, cname, pool_host)
        # read the episode's agent_meta + reward.
        # reward.txt lives in work/.logs/verifier/ (HARBOR_LOGS_DIR=container_work/.logs)
        ep_host = pool_host / epid
        reward = "ERR"
        rfile = ep_host / "work" / ".logs" / "verifier" / "reward.txt"
        if not rfile.exists():
            # fallback: also check ep_host/logs/verifier (older layout)
            rfile = ep_host / "logs" / "verifier" / "reward.txt"
        if rfile.exists():
            reward = rfile.read_text().strip()
        meta = ep_host / "out" / "agent_meta.txt"
        elapsed = _grep(meta, "elapsed_sec=") or "NA"
        intok = _grep(meta, "input_tokens=") or "NA"
        outtok = _grep(meta, "output_tokens=") or "NA"
        cr = _grep(meta, "cache_read_tokens=") or "NA"
        tools = _grep(meta, "tool_uses=") or "NA"
        turns = _grep(meta, "assistant_turns=") or "NA"
        man = ep_host / "out" / "manifest.json"
        pchars = "NA"; psha = "NA"
        if man.exists():
            m = json.loads(man.read_text())
            pchars = m.get("prefix_chars", "NA")
            psha = m.get("prompt_sha256", "NA")[:12] if m.get("prompt_sha256") else "NA"
        arc = _grep(meta, "rc=") or "NA"
        if reward == "ERR": outcome = "infra_fail"
        elif arc == "124" and reward in ("1","0"): outcome = "timeout_solved" if reward=="1" else "timeout_failed"
        elif reward == "1": outcome = "solved"
        elif reward == "0": outcome = "agent_fail"
        else: outcome = "infra_fail"
        results_csv.write_text(results_csv.read_text() +
            f"{epid},{cond},{block},{reward},{outcome},{elapsed},{intok},{outtok},{cr},{tools},{turns},{pchars},{psha}\n")
        print(f"  -> reward={reward} outcome={outcome} elapsed={elapsed}")
    print(f"\nresults: {results_csv}")
    return 0


def _grep(path: Path, key: str) -> str:
    if not path.exists(): return ""
    for line in path.read_text().splitlines():
        if key in line:
            return line.split("=", 1)[1].strip()
    return ""


def _run_episode(cfg, td, epid, cond, cname, pool_host) -> int:
    """One agent episode: prep base -> agent edits -> inject verifier -> score."""
    from .materialize import _local_clone, _git, _container_exec
    clone = _local_clone(cfg)
    if not clone:
        print("no clone"); return 1
    ep_host = pool_host / epid
    if ep_host.exists(): shutil.rmtree(ep_host)
    work = ep_host / "work"; work.mkdir(parents=True)
    out = ep_host / "out"; out.mkdir()
    (ep_host / "logs" / "verifier").mkdir(parents=True)
    container_work = f"/pool/{epid}/work"
    shutil.copytree(clone, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
    shutil.copytree(clone / ".git", work / ".git", dirs_exist_ok=True)
    _git(["checkout", "-q", "-f", cfg["repository"]["base_commit"]], work)
    _git(["clean", "-fdxq", "--", "tests/"], work)
    # stage verifier assets
    vdir = td / "verifier"
    if vdir.exists():
        (work / "verifier").mkdir(exist_ok=True)
        for f in vdir.iterdir():
            if f.is_file(): shutil.copy2(f, work / "verifier" / f.name)
    # build prompt + manifest
    try:
        prompt, mfields = _build_prompt(cfg, td, cond, container_work)
    except ValueError as e:
        print(f"  {e}"); return 1
    mfields.update({"episode_id": epid, "model": os.environ.get("CGCL_MODEL", "macaron-v1-coding-venti"),
                    "base_url": os.environ.get("ANTHROPIC_BASE_URL", "https://mintcn.macaron.xin"),
                    "base_commit": cfg["repository"]["base_commit"]})
    (out / "manifest.json").write_text(json.dumps(mfields, indent=2))
    (out / "prompt.txt").write_text(prompt)
    # agent phase: claude on host, cwd = work
    export = (f"ANTHROPIC_BASE_URL={os.environ.get('ANTHROPIC_BASE_URL','https://mintcn.macaron.xin')} "
              f"ANTHROPIC_AUTH_TOKEN={os.environ.get('ANTHROPIC_AUTH_TOKEN','')}")
    allow = "--allowedTools Read,Write,Edit,Bash,Glob,Grep,LS"
    start = time.time()
    agent_cmd = (f"{export} timeout 600 claude -p {repr(prompt)} --output-format stream-json "
                 f"--verbose {allow}")
    # run claude on HOST (not container) — it edits files in `work` (host path)
    with open(out / "agent.jsonl", "w") as af, open(out / "agent.stderr", "w") as ef:
        r = subprocess.run(agent_cmd, shell=True, cwd=str(work), stdout=af, stderr=ef, timeout=620)
    rc = r.returncode
    elapsed = int(time.time() - start)
    # parse usage from result event
    _parse_usage(out / "agent.jsonl", out / "agent_meta.txt")
    with open(out / "agent_meta.txt", "a") as f:
        f.write(f"rc={rc}\nelapsed_sec={elapsed}\ncondition={cond}\n")
    # inject verifier patch (if any) — applied on host
    vpatch_rel = cfg.get("patches", {}).get("verifier")
    if vpatch_rel:
        _git(["apply", str(td / vpatch_rel)], work)
        time.sleep(1.0)
    # score via container (sentinel poll)
    vcmd = cfg["verifier"]["command"]
    vtimeout = cfg["verifier"]["timeout_sec"]
    env_prefix = (f"HARBOR_WORKDIR={container_work} HARBOR_TESTS_DIR={container_work}/verifier "
                  f"HARBOR_LOGS_DIR={container_work}/.logs ")
    # clear stale reward
    rf = work / ".logs" / "verifier" / "reward.txt"
    rf.parent.mkdir(parents=True, exist_ok=True)
    if rf.exists(): rf.write_text("")
    rc_v, out_v = _container_exec(cname, env_prefix + vcmd,
                                  [(str(work), container_work)], container_work, timeout=vtimeout)
    (out / "verify.log").write_text(out_v)
    return rc_v


def _parse_usage(jsonl: Path, meta: Path) -> None:
    tools = turns = in_t = out_t = cr = 0
    try:
        for l in jsonl.read_text().splitlines():
            try: ev = json.loads(l)
            except: continue
            t = ev.get("type")
            if t == "assistant":
                turns += 1
                for c in ev.get("message", {}).get("content", []):
                    if c.get("type") == "tool_use": tools += 1
            elif t == "result":
                u = ev.get("usage", {}) or {}
                in_t = u.get("input_tokens", 0); out_t = u.get("output_tokens", 0)
                cr = u.get("cache_read_input_tokens", 0)
    except Exception:
        pass
    with open(meta, "w") as f:
        f.write(f"input_tokens={in_t}\noutput_tokens={out_t}\ncache_read_tokens={cr}\n"
                f"tool_uses={tools}\nassistant_turns={turns}\n")
