# reset-only probe retry — ripgrep c2->c3 (reward-path fix did NOT clear the infra_fail)

ep_000000 reset: reward=ERR outcome=infra_fail 600s, 91 tools, 119 turns, 29.5k in-tok.

The agent DID work (91 tool calls) and the verifier's cargo ran (verify.log shows RC=101, the 4
c3 regression tests fail on the agent's edit). But reward.txt is never written to the host, and
NOT to the container either — `/pool/ep_000000/work/.logs/verifier/` does not exist in the
container, and `/logs/verifier/` (the test.sh default) is also empty.

The test.sh reward-path fix (binary 0/1) is correct but NOT the root cause: test.sh's writes
to `$logs_dir/verifier/` under `$HARBOR_LOGS_DIR` are not landing at all under the intervene
_container_exec wrapper for the cargo-based rg test.sh, even though the same mechanism works
for the tap-based fastify test.sh. The cargo build/verify appears to interact badly with the
fuse-bind + sentinel-poll in a way not yet diagnosed (likely heavier cargo I/O or a cwd/env
propagation difference specific to the rust container). Deep intervene/fuse-sync bug, out of
scope to fully diagnose this session.

# Decision (per reviewer "fix or explicitly abandon"): ABANDON the c2->c3 intervene for now.
The NODE itself (ripgrep_c3) materializes 4/4 cleanly (mat_c3_reg: base_fail/gold_pass/
pass_to_pass/near_miss all passed — that code path writes reward via a different, working
mechanism). So the c3 node is usable for the bank; only the c2->c3 EDGE's causal screening is
blocked by the intervene infra bug. Recorded honestly as: 1 reset-only probe, infra-failed,
intervene/fuse-sync issue, not a clean feasibility read.
