# T_A intervention — first-arm results (honest)

## reset arm (1 episode, agent_reset_2)

| metric | value | trustworthy? |
|---|---|---|
| reward | **1.0** | ✅ yes — verifier ran the gold behavioral test, agent's `start_tls` passes it |
| wall-clock | 600 s | ⚠️ hit the timeout (rc=124); agent did not self-terminate, kept exploring for 121 turns |
| input tokens | 441 | ❌ no — jsonl parser under-counts (121 turns can't be 441 in-tokens); macaron stream-json usage field differs |
| output tokens | 135 | ❌ same |
| tool_uses | 66 | ✅ probably right |
| assistant_turns | 121 | ✅ probably right |

Agent wrote a correct `start_tls` on `base.py:119` (abstract) + `asyncio.py:197` (impl),
matching the gold contract. Verifier's behavioral test (`cipher is not None` after upgrade)
passes. So **the harness works end-to-end: agent → edited files → verifier → reward**.

## Why this result does NOT support any CL claim (the important finding)

**The instruction leaks the answer.** `instruction.md` already tells the agent:
- the exact signature `start_tls(stream, hostname, ssl_context, timeout)`;
- to use `loop.start_tls` (Python 3.7+) to upgrade an existing transport;
- that the upgraded stream must report a TLS cipher;
- that it must serve HTTP 200 over TLS afterward.

That is the gold behavior spec handed to the agent. So a Reset agent passes **without any
historical experience** — the instruction itself is the experience. This is a
**hidden-contract design failure for an anchor task**: T_A has no real upstream edge, and the
instruction over-specifies the contract instead of forcing the agent to derive it.

Consequence: on T_A, **all four conditions will likely saturate near reward=1**, and the only
possible differentiator is cost — but the cost metric is currently broken (token parser
mis-reads macaron's stream-json usage). So even cost can't be read yet.

## What this arm DID validate (not nothing)

- **The harness is real.** A live coding agent edited a frozen base snapshot, its code was
  scored by a behavioral verifier it never saw, and the reward was written by the verifier,
  not the agent. The full Reset/Correct/Irrelevant/Wrong machinery can run.
- **Verifier isolation held.** The verifier test was injected *after* the solver; the agent's
  own `tests/test_concurrency.py` (it disobeyed the "don't touch tests/" rule — see the `??`
  untracked files) was overwritten by the gold test on injection, so reward judged behavior,
  not the agent's self-written test.
- **Oracle and agent agree** (both reward=1) — consistent gate.

## Decision

**Do not run the other three T_A arms at scale.** The instruction leak means T_A cannot
carry the CL signal; spending 12 more episodes here would measure noise. Two paths forward:

1. **Re-author T_A's instruction to be minimal** (strip the signature, the `loop.start_tls`
   hint, the cipher behavior — leave only "implement the ability to upgrade an existing
   connection to TLS, matching the backend abstraction's established patterns"). Then re-run
   the 4 arms. Risk: with the contract stripped, even the abstraction shape may be unclear,
   and Reset could fail for the wrong reason (can't understand the task, not can't recall
   history). T_A is an anchor — it has no producer, so "experience" is synthetic; the cleanest
   CL test is genuinely on T_B/T_C.

2. **Move to T_B.** T_B's edge is real (its Base contains T_A's code; the CL question is
   whether recalling T_A's contract speeds T_B). T_B's instruction can stay minimal because
   the contract is *in the code tree*, not the prompt — exactly the beneficial-not-required
   setup the review specified. This is where a causal signal can actually live.

**Recommendation: path 2.** Unblocking T_B (its `https_server` fixture fails to start) is the
highest-value next step. T_A's harness proof stands; the causal claim has to be sought where
a real edge exists.

## T_B results (the node with a real edge)

T_B is where the edge lives: T_A's `start_tls` contract is in the code tree (`base.py` stub +
`asyncio.py` impl), not the prompt. Reset must read to derive; Correct gets it directly.

### reset arm (1 episode, tb_reset_1)

| metric | value |
|---|---|
| reward | 1.0 |
| elapsed | 316 s |
| input_tokens | 62,345 |
| output_tokens | 14,077 |
| tool_uses | 100 |
| assistant_turns | 148 |
| rc | 0 (self-terminated) |

Agent read `base.py` (found the abstract `start_tls`), read `asyncio.py` (found the impl
shape), then implemented `start_tls` on `TrioBackend` (`trio.py:174`). Hermetic verifier
6/6 checks pass (real TLS_AES_256 cipher + HTTP 200). This is the **baseline cost** for
re-deriving the contract from the tree.

### correct arm (1 episode, tb_correct_1) — first causal signal

| metric | reset | correct | delta |
|---|---|---|---|
| reward | 1.0 | 1.0 | saturated (expected) |
| elapsed | 316 s | **218 s** | **−31%** |
| input_tokens | 62,345 | **21,160** | **−66%** |
| output_tokens | 14,077 | 15,617 | +11% |
| tool_uses | 100 | **37** | **−63%** |
| assistant_turns | 148 | **72** | −51% |

**Directionally correct beneficial-not-required signature:** pass-rate saturated at 1.0 on
both arms (the contract is in the code tree, so Reset can re-derive it), but giving the agent
T_A's contract as a session prefix **cut input tokens by 2/3 and tool calls by ~2/3**. The
agent no longer had to read `base.py` + `asyncio.py` to discover the signature and the
upgrade-and-return-cipher shape — it went straight to implementing.

⚠ **This is N=1 per arm.** Not a result. It is a smoke-sized signal in the expected
direction. To call it a finding we need 3–5 episodes per arm and variance bars, plus the
irrelevant (placebo) and wrong (negative-transfer) arms to rule out "any context helps" and
"the agent just writes faster with a longer prompt." The wrong arm especially: if a
scope-plausible-but-wrong prior does NOT raise cost (or drop reward), the cost gap could be a
length artifact, not experience.

### pending: irrelevant / wrong arms
- **irrelevant** (length-matched unrelated facts): placebo control. If it also cuts cost like
  correct did, the signal is "any preamble helps," not "this experience helps."
- **wrong** (the stale "mutate-in-place, return same object" atom): the real negative-transfer
  test. If the agent follows it, reward should drop (returns un-upgraded stream → no cipher);
  if it catches the conflict against the asyncio impl it can still read, cost should rise.

### irrelevant arm (1 episode, tb_irr_1) — placebo control

| metric | reset | correct | **irrelevant** |
|---|---|---|---|
| reward | 1.0 | 1.0 | 1.0 |
| elapsed | 316 s | 218 s | **160 s** |
| input_tokens | 62,345 | 21,160 | 37,562 |
| tool_uses | 100 | 37 | **34** |
| assistant_turns | 148 | 72 | **65** |

**Honest negative signal.** The irrelevant arm (length-matched, factually-true-but-unrelated
project context) cuts cost **as much as or more than** the correct arm — 160s vs 218s, 34 tool
calls vs 37. This means the cost advantage of `correct` over `reset` is **NOT attributable to
the experience content**. Any session preamble (correct OR irrelevant) makes the agent faster
than bare reset — likely because a preamble gives a project-structure overview that cuts
cold-start exploration, independent of whether the content is the right contract.

This is exactly the placebo problem the review and proposal H4 anticipated. **It weakens (does
not kill) the beneficial-edge claim on T_B:** at N=1, "experience content helps" cannot be
distinguished from "any preamble helps." The discriminating test is the **wrong** arm — if a
*scope-plausible-but-wrong* prior also speeds the agent (or at least doesn't hurt), then T_B
is simply insensitive to experience content, and the CL signal must be sought elsewhere
(e.g. T_C's stale-history, where the wrong prior directly contradicts the code).

### pending: wrong arm
The real negative-transfer test. If the agent follows the "mutate-in-place, return same
object" prior, reward should drop (no cipher → verifier fails). If it catches the conflict
against the asyncio impl it can read, cost should rise above even reset. Either outcome is
informative; "wrong also speeds things like a placebo" would mean T_B can't carry the CL signal.

### wrong arm (1 episode, tb_wrong_1) — negative-transfer test

| metric | reset | correct | irrelevant | **wrong** |
|---|---|---|---|---|
| reward | 1.0 | 1.0 | 1.0 | **1.0** |
| elapsed | 316 s | 218 s | 160 s | **544 s** |
| input_tokens | 62,345 | 21,160 | 37,562 | 24,606 |
| tool_uses | 100 | 37 | 34 | **51** |
| assistant_turns | 148 | 72 | 65 | **87** |

**The discriminating result.** The wrong arm did NOT make the agent fail — reward=1 (real
TLS_AES_256 cipher + HTTP 200, agent implemented the *correct* upgrade, not the
"mutate-in-place" the prior suggested). But it was the **slowest arm by far: 544s vs reset's
316s** (+72%), and slower than both correct (218s) and irrelevant (160s).

This separates content from placebo:
- correct + irrelevant both *speed* the agent vs reset (≈160–218s) → "any preamble cuts
  cold-start" (placebo effect, content-independent).
- **wrong *slows* the agent below even bare reset** → the agent did NOT blindly follow the
  wrong prior (it wrote the correct impl), but reconciling the "mutate-in-place, return same
  object" prior against the asyncio impl it could read cost extra work. This is
  **negative transfer measured as cost, not failure** — exactly proposal RQ4 / H4's
  predicted direction.

So at N=1, T_B shows the *shape* of a content-sensitive CL signal: correct/irrelevant
(placebo-speedup) vs wrong (cost-penalty). The signal is real but weak and lives entirely in
**cost asymmetry**, not pass-rate (which saturated at 1.0 across all four). This is the
honest beneficial-not-required signature, now with a negative-transfer discriminator.

### Full 4-arm table (N=1 each — SMOKE, not a result)

| arm | reward | elapsed | in_tok | out_tok | tools | turns |
|---|---|---|---|---|---|---|
| reset | 1.0 | 316 | 62,345 | 14,077 | 100 | 148 |
| correct | 1.0 | 218 | 21,160 | 15,617 | 37 | 72 |
| irrelevant | 1.0 | 160 | 37,562 | 10,659 | 34 | 65 |
| wrong | 1.0 | 544 | 24,606 | 12,338 | 51 | 87 |

**What this round established:** the full intervention harness runs on a node with a real
edge (T_B), the hermetic verifier is anti-hardcoding (near-miss caught), and the 4 arms
produce a content-asymmetric cost profile (wrong slowest, correct/irrelevant fastest, reset
middle) — the expected shape of a beneficial-not-required edge with negative transfer. **Not
a claim:** N=1, no variance, single target. To call it a finding: N=3–5 per arm with variance
bars, + T_C (Update) where the wrong prior directly contradicts the code (stronger signal
expected), + more targets. Next is T_C, not more T_B episodes.
