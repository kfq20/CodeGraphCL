# CodeGraphCL Go task image (viper). golang:1.23 (full image — no slim tag exists for 1.23/1.24)
# ships go + gcc + git + ca-certificates. Module cache mounted at /pool/gomod so deps persist
# across episodes (first `go test` downloads ~1-2 min, subsequent <30s). Image stays generic; deps
# travel with the repo snapshot (go.mod in the worktree). Same DinD/host-applies-patch pattern as
# ripgrep/httpx/fastify.
FROM golang:1.23

ENV DEBIAN_FRONTEND=noninteractive \
    GOPATH=/go \
    GOMODCACHE=/pool/gomod \
    GOFLAGS=-mod=mod

# golang:1.23 (full) has git + ca-certificates + gcc. No apt layer (deb.debian.org unreachable on
# this fuse-overlayfs host; ~85s per package). viper needs no cgo for the touched packages; if a
# snapshot turns out to need extra libs, add them later.

RUN mkdir -p /workspace /pool/gomod
WORKDIR /workspace

# keep the container alive (cgcl-rg-box pattern)
CMD ["sleep", "infinity"]
