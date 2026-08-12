# ripgrep c3 materialization

**Node:** c3 = `14f4957b3d` (ignore: fix filtering searching subdir or .ignore in parent dir)
**Base:** `14f4957b3d^` = f722268 (ripgrep 14.1.1, rust-version 1.88)

## Executable Task Gate

| gate | status | evidence |
|---|---|---|
| base-fail | ✅ | 4 tests FAIL on base: `r829_2747`, `r829_2778`, `r829_2836`, `r829_2933` |
| gold-pass | ✅ | after c3 source patch: 6/6 pass (the 4 above + 2 PASS_TO_PASS) |
| PASS_TO_PASS | ✅ (partial) | `r829_original`, `r829_2731` pass on BOTH base and gold (c2-era fixes, protected) |
| near-miss | TODO | need >=2 |

**FAIL_TO_PASS** = {r829_2747, r829_2778, r829_2836, r829_2933}
**PASS_TO_PASS (within the c3 test block)** = {r829_original, r829_2731}

## How to run (this host)

```bash
# host: checkout base into a pool worktree (container has NO git — rust:slim doesn't ship it)
cp -a repos/ripgrep-full/. /tmp/cgcl_box_pool/<ep>/work/     # ripgrep-full at c3 base
cd /tmp/cgcl_box_pool/<ep>/work && git apply <c3_verifier.patch>   # host git
# container: build + test (test target is `integration`, NOT `regression` — c3-era Cargo.toml
# declares [[test]] name="integration" path="tests/tests.rs"; regression.rs is a mod inside it)
docker exec cgcl-rg-box bash -c 'cd /pool/<ep>/work && cargo test --test integration r829'
```

## Environment notes
- image `codegraphcl-ripgrep:rust` (rust:1.88-slim, NO apt layer — deb.debian.org is ~85s/pkg
  on this host and builds died on timeout; base already has cargo/rustc/cc/gcc).
- container box `cgcl-rg-box`: CARGO_HOME=/cargo-cache (NOT /usr/local/cargo — bind-mounting
  there clobbers the base's cargo binary), CARGO_TARGET_DIR=/target, both host-bind-mounted
  so the build cache persists (build 3.4s warm, test 0.07s).
- `repos/ripgrep-full` is a FULL clone (the blob-filter clone triggers network fetch on
  checkout and TLS is broken here).
