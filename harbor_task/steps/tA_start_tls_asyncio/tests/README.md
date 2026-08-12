# T_A verifier

The verifier is the **gold commit's own regression test**:
`tests/test_concurrency.py::test_start_tls_on_socket_stream` (added by 1872ae873b).

## Why not a hand-written verify.py?

That test is already behavioral, not structural. It asserts:

```python
assert stream.stream_writer.get_extra_info("cipher", default=None) is None      # before
stream = await backend.start_tls(stream, "127.0.0.1", ctx, timeout)
assert stream.stream_writer.get_extra_info("cipher", default=None) is not None  # after: REAL cipher
await stream.write(b"GET / HTTP/1.1\r\n\r\n")
assert (await stream.read(8192, timeout)).startswith(b"HTTP/1.1 200 OK\r\n")     # real HTTP over TLS
```

**Proven anti-hardcoding** by the near-miss gate (`materialize/verify_nearmiss.py`):
a `start_tls` that exists with the right signature but returns the plain stream
unchanged FAILS at the `cipher is not None` assertion. A method-existence check
would have wrongly passed it.

So the honest verifier is the project's own test — writing our own would duplicate it
and risk being weaker. `test.sh` runs it and writes reward.txt.

## Host plumbing baked into test.sh
- `/wheels` offline install (container pip unreliable on this fuse-overlayfs host)
- `-o addopts=` to override setup.cfg's `--cov` (pytest-cov not installed)
- output to file (docker stdout is dropped on this host)
