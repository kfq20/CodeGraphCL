# CodeGraphCL httpx-2019 task image — TWO targets.
#
# `materialize` (default, built first): python 3.7 + old httpx deps + pytest 4.6.
#   This is ALL that's needed for the Executable Task Gate (base-fail/gold-pass/PASS_TO_PASS).
#   No node, no claude — so npm-install slowness never blocks the Dependency Gate.
#
# `agent` (built later, AFTER materialize gate passes): adds node20 + claude-code for the
#   real Reset-vs-Stateful intervention experiment. fuse-overlayfs hosts can't run harbor's
#   bootstrap.sh in-container, so claude is pre-installed at build time (relay_sft pattern).
#
# Build:
#   docker build -t codegraphcl-httpx-2019:mat -f environment/Dockerfile --target materialize environment/
#   docker build -t codegraphcl-httpx-2019:agent -f environment/Dockerfile --target agent environment/

# ─────────────────────────────────────────────── materialize
FROM python:3.7-slim AS materialize

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      bash ca-certificates curl git jq procps ripgrep \
    && rm -rf /var/lib/apt/lists/*

# 2019 httpx runtime deps (pinned per setup.py at commit a4b93b9) + test deps.
# NOTE: pytest-asyncio 0.9.0 imports `_pytest.python.transfer_markers` which pytest removed
# in 4.5 — so plugin load fails on pytest 4.6. The compatible combo is pytest 4.6.11 +
# pytest-asyncio 0.10.0 (rewritten, no transfer_markers). Verified by import probe.
# trustme + uvicorn are required by the repo's tests/conftest.py (https_server fixture
# generates certs via trustme and serves via uvicorn). Bake them at build time so runtime
# needs no pip (container pip is flaky on this fuse-overlayfs host).
RUN python -m pip install --no-cache-dir \
      "certifi" "chardet==3.*" "h11==0.8.*" "h2==3.*" "hstspreload" \
      "idna==2.*" "rfc3986==1.*" \
      "pytest==4.6.11" "pytest-asyncio==0.10.0" "trio" \
      "trustme" "uvicorn" \
      uvloop

RUN mkdir -p /workspace
WORKDIR /workspace

# ─────────────────────────────────────────────── agent (built later, on top of materialize)
FROM materialize AS agent

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
      apt-get install -y --no-install-recommends nodejs && \
      rm -rf /var/lib/apt/lists/* && \
      npm install -g @anthropic-ai/claude-code && \
      bash -lc 'which claude && claude --version'
