# httpx-2019 materialization environment recipe

Verified-working recipe for running the SWE-bench-style base-fail/gold-pass gate on 2019-era
httpx tasks inside Docker on this fuse-overlayfs / containerized-docker host.

## Image
`codegraphcl-httpx-2019:mat` (Dockerfile `harbor_task/environment/Dockerfile`, target `materialize`).
- `python:3.7-slim` (3.7 is REQUIRED — pytest 4.6 assertion-rewrite breaks on Python 3.10+ AST).
- baked deps: certifi, chardet==3, h11==0.8, h2==3, hstspreload, idna==2, rfc3986==1,
  pytest==4.6.11, pytest-asyncio==0.10.0 (NOT 0.9 — 0.9 imports removed `_pytest.python.transfer_markers`),
  trio, uvloop.

## Runtime-only deps (mounted as wheels, offline install)
`tests/conftest.py` needs trustme + uvicorn (+ their transitive deps). Container pip is flaky
on this host, so these are pre-downloaded as py37 wheels and mounted at `/wheels`, installed
with `--no-index --no-deps`:

```
/tmp/cgcl_wheels/  (host)  ->  /wheels (container, ro)
  cffi-1.14.6-cp37-cp37m-manylinux1_x86_64.whl
  click-7.1.2-py2.py3-none-any.whl
  cryptography-3.4.8-cp36-abi3-manylinux_2_24_x86_64.whl
  httptools-0.1.2-cp37-cp37m-manylinux1_x86_64.whl
  pycparser-2.21-py2.py3-none-any.whl
  trustme-1.0.0-py3-none-any.whl
  uvicorn-0.11.8-py3-none-any.whl
  uvloop-0.14.0-cp37-cp37m-manylinux2010_x86_64.whl
  websockets-8.1-cp37-cp37m-manylinux2010_x86_64.whl
```

## The stdout-loss workaround (THIS HOST)
`docker run`/`docker exec` stdout is silently dropped on this containerized-docker host.
ALWAYS redirect container output to a mounted file and read it from the host:
`bash -c 'exec > /out/log 2>&1; ...'` then `cat /tmp/cgcl_out/log`.

## pytest addopts override
`setup.cfg` has `addopts = --cov=...` (pytest-cov, not installed). Run pytest with
`-o addopts=` to override (avoids needing pytest-cov).

## Canonical run command
```bash
docker run --rm \
  -v "$REPO/httpx-full:/workspace/httpx" \
  -v "$TASK/materialize:/materialize" \
  -v /tmp/cgcl_wheels:/wheels:ro \
  -v /tmp/cgcl_out:/out -w /workspace/httpx \
  codegraphcl-httpx-2019:mat \
  bash -c 'exec > /out/tA_gates.log 2>&1
    pip install --quiet --no-index --no-deps /wheels/*.whl
    python3 /materialize/verify_materialization.py "$(cat /out/tA_spec.json)"
  '
```

## Result (T_A = 1872ae873b)
- GATE1 base-fail: PASS (behavior missing — start_tls absent)
- GATE2 gold-pass: PASS
- GATE3 pass-to-pass: PASS (0 regressions)
**T_A clears the Executable Task Gate.**
