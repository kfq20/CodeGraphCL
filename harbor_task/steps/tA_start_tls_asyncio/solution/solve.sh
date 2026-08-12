#!/usr/bin/env bash
# Oracle solver: apply the gold source patch. Used for the free sanity run
# (oracle must score 1.0). Agent never sees this.
set -euo pipefail
cd "${HARBOR_WORKDIR:-/workspace/httpx}"
git apply /solution/gold_source.patch
echo "gold source patch applied"
