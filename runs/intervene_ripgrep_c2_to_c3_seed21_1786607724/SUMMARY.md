# reset-only feasibility probe — ripgrep c2->c3 (consumer c3)

ep_000000 reset: reward=ERR outcome=infra_fail 600s 71 tool_uses 102 turns.

The agent DID edit dir.rs (34 strip_prefix/over matches) but the verifier's reward.txt was
not written to the host — test.sh ran cargo (verify.log shows RC=101, 4 c3 tests failed) but
the printf-to-reward.txt step did not land on the host via the fuse bind (the .logs/verifier/
dir was created at 08:05 but is empty). An intervene/verifier reward-path flake, not a clean
read. Recorded as infra_fail.

Combined with the prior c3->c4 reset probe (reward=1 timeout_solved 600s, the wall band), the
ripgrep revision edges sit at/above the feasibility ceiling — reset either infra-fails or
solves-at-the-wall. None of the probed single/revision edges landed in the clean CL-readable
band.
