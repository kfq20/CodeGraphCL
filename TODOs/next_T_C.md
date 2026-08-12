# Next: T_C materialization + intervention

T_B is done (N=3): **negative transfer confirmed (wrong 0/3), no positive transfer (correct
≈ reset/irrelevant, no cost benefit)**. Per the review decision rule, stop T_B and move to
T_C — the strongest CL test in the family.

## T_C = `644e8fc5b6` (Make start_tls a method on streams & return a new stream)

**Contract revision (Update motif):** `backend.start_tls(stream, hostname, ssl_context, timeout)`
→ `stream.start_tls(hostname, ssl_context, timeout)`, returns a NEW stream (not mutate-in-place).
The T_A/T_B "backend owns start_tls, mutate in place" atom is **stale** for T_C.

**Why T_C is the strongest CL test:** the stale-history prior directly contradicts the code
the agent must write. In T_B, the wrong prior ("defer handshake") was about an
implementation detail the agent could override by reading. In T_C, the stale prior is about
the **contract location itself** — if the agent follows the old "backend.start_tls" shape,
it won't even have a `stream.start_tls` for the verifier to call. Expected: stronger
negative transfer (stale arm fails harder) + the correct arm (revised contract) should
finally separate from reset, because the revision is non-trivial to derive by reading.

## What's already prepared
- `harbor_task/materialize/tC_source.patch` (225 lines, httpx/ only)
- `harbor_task/materialize/tC_verifier.patch` (64 lines, tests/ — but depends on the broken
  https_server fixture, so T_C also needs a HERMETIC verifier, not the gold test)
- `harbor_task/steps/tC_start_tls_stream/instruction.md` (minimal — contract in code tree)
- `harbor_task/steps/tC_start_tls_stream/solution/gold_source.patch`

## TODO for the next agent (in order)
1. **Hermetic verifier for T_C** — extend `steps/tB_start_tls_trio/tests/verify.py` to call
   `stream.start_tls(hostname, ssl_context, timeout)` instead of `backend.start_tls(stream,
   ...)`. Must work on both asyncio and trio streams (or just one — pick trio to match T_B).
   Base-fail: T_C base has `backend.start_tls` but no `stream.start_tls` → calling
   `stream.start_tls` raises AttributeError. Gold-pass: T_C source moves it onto the stream.
   Near-miss: a `stream.start_tls` that mutates self in place (doesn't return new stream) —
   should fail the "new stream" behavioral check.
2. **Oracle + base-fail/gold-pass/near-miss** in Docker (reuse run_tb_episode pattern —
   probably copy to run_tc_episode.sh with T_C base sha `644e8fc5b6^`).
3. **T_C experience atoms** (`tC_experience_atoms.md`):
   - reset: none
   - correct: the REVISED contract (start_tls on stream, returns new stream)
   - irrelevant: length-matched unrelated facts (reuse T_B's irrelevant, stripped)
   - **wrong/stale**: the OLD T_A/T_B contract ("backend owns start_tls; pass stream in,
     mutate in place, return same stream") — this is genuinely stale for T_C, surface-plausible.
4. **N=3 block-randomized, opaque IDs** (run_tb_batch.sh pattern). Go/No-Go:
   - stale arm fails + correct separates from reset → T_C passes Causal Gate (full)
   - stale fails but correct still doesn't beat reset → negative transfer only (like T_B)
   - nothing separates → T_B/T_C family too weak; retarget to a harder node (ripgrep with
     Rust toolchain, or a different httpx segment)

## Host notes (carry forward)
- fuse-overlayfs: bind-mount targets MUST be empty; `cp -a` inside container; box→host file
  sync needs ~2s sleep + pre-created subdirs.
- docker stdout dropped — write to /pool/<ep>/out/*.log, read from host.
- single-quote docker exec bodies (host pre-expands `>` in double quotes).
- root can't use --dangerously-skip-permissions → --allowedTools.
- macaron per-assistant usage is all zeros → read real tokens from `result` event.
- Long-lived container `cgcl-mat-box` provides py3.7+deps; claude runs on host.
