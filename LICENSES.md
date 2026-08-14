# CodeGraphCL-v1 License Inventory

CodeGraphCL itself is MIT-licensed. The benchmark tasks derive from the following open-source
repositories, each under their own license. The benchmark does NOT redistribute source code
from these repositories — it references commits by SHA and provides patches (diffs) that are
applied against the user's own clone. Patches are derivative works under the same license as the
original.

## Source repositories

| repo | upstream | license | notes |
|---|---|---|---|
| ripgrep | BurntSushi/ripgrep | Unlicense OR MIT (dual) | patches are MIT |
| fastify | fastify/fastify | MIT | Copyright (c) 2016-2018 The Fastify Team |
| clap | clap-rs/clap | MIT OR Apache-2.0 (dual) | patches are MIT or Apache-2.0 |
| httpx | encode/httpx | BSD-3-Clause | patches are BSD-3-Clause |

## Viper (pending)

| repo | upstream | license | notes |
|---|---|---|---|
| viper | spf13/viper | Apache-2.0 | Go; not yet built into the benchmark |

## CodeGraphCL harness

The CodeGraphCL tooling (codegraphcl/ package, Dockerfiles, protocols) is MIT-licensed.

## Disclaimer

The benchmark references real commits from real open-source repositories. Users must clone the
repositories themselves (the benchmark provides SHAs and patches, not full source). The
benchmark's patches are derivative works of the upstream code and are distributed under the same
license as the upstream repository. No warranty is provided.
