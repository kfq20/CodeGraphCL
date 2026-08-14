#!/usr/bin/env bash
# Harbor verifier for clap_complete_fish_quote (fish env-completer path double-quoting).
# Runs the gold test `fish_env_completer_path_with_backslash` (snapshot in clap_complete/src/env/shells.rs).
# On base + verifier patch (new expectations), the old single-pass quoting produces a different
# snapshot -> mismatch -> FAILS. After gold (two-pass quoting functions), output matches -> PASSES.
#
# Anti-hardcoding: near-miss variants (single-pass for completer / skip $-escape) re-fail.
#
# Runs in codegraphcl-ripgrep:rust. Test target is the `clap_complete` lib (inline tests in mod tests).
# Requires --features unstable-dynamic (the fish tests are #[cfg(all(unix, feature = "unstable-dynamic"))]).
set -uo pipefail
workspace="${HARBOR_WORKDIR:-$PWD}"
logs_dir="${HARBOR_LOGS_DIR:-/logs}"
mkdir -p "$logs_dir/verifier"

cd "$workspace" || { printf 0 > "$logs_dir/verifier/reward.txt"; exit 1; }
OUTPUT=$(cargo test -p clap_complete --features unstable-dynamic --lib fish_env_completer_path_with_backslash 2>&1)
RC=$?
echo "$OUTPUT" > "$logs_dir/verifier/test-stdout.txt"
if [ "$RC" -eq 0 ]; then
  printf 1 > "$logs_dir/verifier/reward.txt"
else
  printf 0 > "$logs_dir/verifier/reward.txt"
fi
cat "$logs_dir/verifier/reward.txt"
exit 0
