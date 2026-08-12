# R2 Milestone — First Executable, Intervenable Task Node

> Status as of this round. Written to the standard the review demanded: **no over-claiming**,
> gates named precisely, edge strength stated honestly.

## Where the project actually stands

| Gate | Status | Evidence |
|---|---|---|
| **Candidate Supply Gate** (R1) | ✅ passed | 2469 co-change commits → 102 motif-grade segments across 5 repos |
| **Semantic Dependency Gate** (R2 audit) | ✅ passed, 2 families | ripgrep `c2→c3→c4` (Update chain, c3's message explicitly revises c2's code); httpx `T_A→T_B→T_C` (Parity then Update) |
| **Executable Task Gate** (R2 materialization) | ✅ passed for **httpx T_A** | base-fail / gold-pass / PASS_TO_PASS + near-miss all verified in Docker |
| **Causal Dependency Gate** | ⏳ in progress | T_A intervention arms (reset/correct/irrelevant/wrong) running |

**Honest headline:** we have gone from "102 metadata candidates" to **one node proven to be a
behaviorally-reliable, executable task**, plus a running intervention harness. That is the
step the review asked for. We have NOT yet shown that history produces a measurable
difference — that is the arm currently executing.

## Corrections applied from review (all six)

1. **Join labels removed.** httpx is `Parity → Update → Stale`, ripgrep is `Update chain +
   Stale/Scoped-Negative`. Neither is Join: in both, the second node *subsumes/revises* the
   first rather than being a second independent source. True Join needs two non-includable,
   non-substitutable atoms.
2. **"Required" downgraded to "candidate beneficial".** T_B's Base *already contains* T_A's
   code — a Reset agent can re-derive the contract by reading the tree. Snapshot isolation
   stops file-state carry, not knowledge sedimented into later code. So experience should cut
   *cost*, not gate success.
3. **Language-dependency claim retracted.** R1's "Go can't produce motifs" is now stated as
   *"file-granularity mining has different observability across repository organizations"* —
   a miner limitation, not a language finding.
4. **Test-shape requirement dropped.** "The test must be parametrized across backends" is no
   longer a consumer decision. The verifier checks behavior; an agent that implements
   correctly without refactoring the test still passes.
5. **ripgrep atom de-leaked.** Removed `take_while(!is_absolute_parent).last()` and the
   `./ → prefix → /` ordering. Now states the *principle* (strip must avoid both duplication
   and over-stripping, respect component boundaries, cover relative/absolute/`.` cases) and
   leaves the implementation to the agent.
6. **Hard-negative redesigned.** No more obviously-wrong "never strip". Now a *scope-plausible
   but inapplicable* real invariant (e.g. the global-gitignore relative-to-CWD rule applied to
   a path-stripping target) — tests scope judgment, not absurdity rejection.

## What was actually built and verified

### httpx T_A = `1872ae873b` (Add `ConcurrencyBackend.start_tls()`)
- `Base = parent(T_A) = a4b93b9`; source patch (`concurrency/*.py`, `dispatch/*.py`) and
  verifier patch (`tests/test_concurrency.py`) split from the commit.
- **GATE1 base-fail:** `Base + verifier` → FAIL, and the failure is *behavioral*
  (`assert stream.is_connection_dropped() is False` after a missing `start_tls`), not a
  collection/import error. This was the specific thing the review insisted on.
- **GATE2 gold-pass:** `Base + source + verifier` → PASS.
- **GATE3 PASS_TO_PASS:** full test file, 0 regressions.
- **Near-miss anti-hardcoding gate:** a `start_tls` that exists with the correct signature but
  returns the plain stream (no TLS upgrade) **FAILS** at
  `assert get_extra_info("cipher") is not None`. So the verifier tests behavior, not method
  existence. A stub cannot pass.

### The verifier is the project's own test
Rather than hand-rolling assertions, the verifier runs
`tests/test_concurrency.py::test_start_tls_on_socket_stream` — the regression test the httpx
authors wrote for this commit. The near-miss gate proves it is behavioral. Hand-writing our
own would have duplicated it and risked being weaker.

### Oracle end-to-end
Full episode pipeline (prep → solve → inject-verifier → score) returns **reward=1.0** with the
gold patch. Verifier tests are injected *after* the solver phase, so the agent never sees the
gold assertions (harbor verifier-isolation lesson).

## Environment findings (this host is hostile; recorded so it isn't re-derived)

| Problem | Resolution |
|---|---|
| pytest 4.6 breaks on Python 3.10 AST (`lineno missing from alias`) | must use `python:3.7-slim` — Docker isn't optional here |
| pytest-asyncio 0.9 imports `_pytest.python.transfer_markers`, removed in pytest 4.5 | pin **pytest 4.6.11 + pytest-asyncio 0.10.0** |
| `tests/conftest.py` needs trustme + uvicorn (+cffi/cryptography/click/websockets/httptools/pycparser) | pre-download py37 wheels on host, mount `/wheels`, install `--no-index --no-deps` |
| `setup.cfg` has `addopts = --cov=...`, pytest-cov absent | run pytest with `-o addopts=` |
| **docker bind-mount target must be EMPTY** (`bindfs: mountpoint is not empty`) | never mount a populated dir; mount empty dirs, `cp -a` inside the container |
| **`docker run`/`exec` stdout is silently dropped** | every phase redirects to a file under the shared `/pool` mount; host reads it after ~1–2 s sync |
| host shell pre-expands `>` inside double-quoted `docker exec bash -c "..."` | single-quote the container-side body |
| `--dangerously-skip-permissions` refused under root | use `--allowedTools Read,Write,Edit,Bash,Glob,Grep,LS` |
| container pip network unreliable | offline wheels only |

Recorded in `harbor_task/materialize/ENV_RECIPE.md`.

## Intervention design (running)

T_A is an **anchor** (no real producer upstream), so its four arms test the *harness*, not a
real edge. The atoms are constructed (proposal §7.2):

| condition | prefix |
|---|---|
| reset | none |
| correct | the real `ConcurrencyBackend.start_tls` contract |
| irrelevant | length-matched true-but-unrelated project facts (certifi/chardet/URL parsing) |
| wrong | scope-plausible but inapplicable: "mutate the stream in place and return the same object" (this is the *stale* shape T_C later revises) |

Metrics collected per episode: reward, wall-clock, input/output tokens, tool_uses,
assistant_turns. **Because T_A is an anchor and Reset may well saturate, the expected signal
is cost, not pass-rate.** If no metric separates, the honest reading is that this target is
too easy to carry experience dependence — which is a finding, not a failure to hide.

## What is NOT yet established

- **No causal claim.** Intervention arms are running; nothing is concluded.
- **T_B/T_C not materialized.** T_B's `https_server` fixture (old conftest + uvicorn) fails to
  start on its base — separate diagnosis needed. T_B is where the *real* edge lives, so this
  is the most important next step.
- **ripgrep not materialized.** No Rust toolchain on this host (`cargo` absent). Its audit
  stands at L3 (semantic) only.
- **N is tiny.** Whatever the first arms show, 3–5 episodes per condition is a smoke test, not
  a result.

## Next

1. Finish T_A arms; report reward **and** cost metrics; do not over-read a saturated Reset.
2. Diagnose T_B's `https_server` startup (this unblocks the first *real* edge measurement).
3. Then T_C (Update) + the Stale-history arm — the strongest CL test in the family.

## Update — T_B Executable Task Gate PASSED (after unblock)

The review's chosen path worked: **abandon the unstable upstream uvicorn/pytest-trio
fixtures; use a hermetic behavioral verifier** (`trio.run` + a stdlib `ssl` TLS server in a
thread, no uvicorn, no pytest-trio). This sidesteps the `https_server` fixture hang entirely.

T_B = `38a136833f` (Add `start_tls` to Trio backend). Base = `e5d0ad2` (T_A's code already
present: `ConcurrencyBackend.start_tls` abstract stub in `base.py:122`, asyncio impl present;
`TrioBackend` has no `start_tls`).

**Verified gates:**
- **base-fail:** reward=0, and the failure is behavioral — `TrioBackend.start_tls exists`
  passes (the abstract method is there), but calling it raises `NotImplementedError` from
  `base.py:129`. Clean "declared but not implemented" semantics, not a collection error.
- **gold-pass:** reward=1, 6/6 behavioral checks — real TLS cipher
  (`TLS_AES_256_GCM_SHA384`) after `start_tls`, real HTTP 200 over the upgraded stream.
- **near-miss:** a `start_tls` that returns the plain stream without upgrading → reward=0
  (the plain stream hits a TLS-only server → `Connection reset by peer`). Verifier is
  anti-hardcoding.

**This is the node with a real edge.** T_A→T_B: the contract T_A established lives in the
code tree (`base.py` stub + `asyncio.py` impl), NOT in the prompt. A Reset agent must read
the tree to find it; a Correct agent gets it directly. That is exactly the
**beneficial-not-required** setup the review specified. T_B's instruction is minimal (no
signature, no `loop.start_tls` hint, no cipher behavior leaked) — the contract is in the code.

**Intervention running:** 4 arms (reset/correct/irrelevant/wrong) on T_B. Token metrics now
read from the `result` event (macaron's per-assistant-event usage is all zeros — an endpoint
quirk; real usage is in the final `result` event: input/output/cache-read). T_A's earlier
token numbers were wrong (under-counted); T_B uses the fixed parser.
