# T_A workdir

The agent works on a checkout of httpx at **Base = parent(1872ae873b) = a4b93b9**.
The repo is mounted at /workspace/httpx.

**Tests are NOT in the workdir** — the verifier patch (tests/test_concurrency.py) is
injected only in the verification phase, after the agent finishes. This prevents the
agent from reading the gold assertions (harbor verifier-isolation lesson: a shared
/tests dir leaks gold strings and fakes a pass).
