"""Hermetic behavioral verifier for T_B (TrioBackend.start_tls).

Why hermetic: the gold test for this commit depends on the repo's `https_server` pytest
fixture (uvicorn `TestServer` + `serve_in_thread`) and on `pytest.mark.trio` (pytest-trio).
Both are unreliable in this pinned 2019 environment — the fixture's `server.started` never
flips, so the gold test hangs rather than failing cleanly, which breaks base-fail semantics.
Rather than fight upstream fixture/plugin versions, this verifier stands up its own minimal
TLS server (stdlib ssl + socket in a thread) and drives the agent's code with `trio.run`.

What it checks (behavior, not shape):
  1. TrioBackend exposes start_tls at all;
  2. a plain TCP stream opened via the backend has NO cipher;
  3. after start_tls, the SAME logical connection reports a real TLS cipher;
  4. an HTTP request written over the upgraded stream returns a real HTTP 200 response.

(3)+(4) are what a stub cannot fake: the cipher must come from a real handshake with a real
cert, and the server only answers over TLS.

Exit 0 = pass. Non-zero = fail. Writes a PASS/FAIL line per check.
"""
from __future__ import annotations

import os
import socket
import ssl
import sys
import threading
import traceback

sys.path.insert(0, os.environ.get("CGCL_WORKDIR", "/pool/work"))

RESULTS = []
def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


# ---------------------------------------------------------------- minimal TLS server
def make_cert(tmpdir):
    """Generate a self-signed cert with trustme (already installed for conftest)."""
    import trustme
    ca = trustme.CA()
    cert = ca.issue_cert("127.0.0.1")
    pem = os.path.join(tmpdir, "cert.pem")
    key = os.path.join(tmpdir, "key.pem")
    cert.cert_chain_pems[0].write_to_path(pem)
    cert.private_key_pem.write_to_path(key)
    return pem, key


class TLSEchoServer:
    """Serves plain TCP first; the client upgrades to TLS; then answers a minimal HTTP 200."""
    def __init__(self, certfile, keyfile, port):
        self.certfile, self.keyfile, self.port = certfile, keyfile, port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", port))
        self.sock.listen(5)
        self.thread = None
        self.stop = False

    def _serve(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(self.certfile, self.keyfile)
        self.sock.settimeout(0.5)
        while not self.stop:
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                # The client connects in the clear, then performs a TLS handshake on the
                # same socket (that's exactly what start_tls must do).
                tls = ctx.wrap_socket(conn, server_side=True)
                try:
                    tls.recv(65536)
                    tls.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nhi")
                finally:
                    try: tls.close()
                    except Exception: pass
            except Exception:
                try: conn.close()
                except Exception: pass

    def start(self):
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def close(self):
        self.stop = True
        try: self.sock.close()
        except Exception: pass


# ---------------------------------------------------------------- the behavioral test
def main():
    import tempfile
    tmp = tempfile.mkdtemp()
    port = 8443
    certfile, keyfile = make_cert(tmp)
    server = TLSEchoServer(certfile, keyfile, port)
    server.start()

    try:
        import trio
        from httpx.concurrency.trio import TrioBackend
        from httpx import SSLConfig, HTTPVersionConfig, TimeoutConfig
        check("import TrioBackend", True)
    except Exception as e:
        check("import TrioBackend", False, f"{type(e).__name__}: {e}")
        server.close(); return 1

    if not hasattr(TrioBackend, "start_tls"):
        check("TrioBackend.start_tls exists", False, "method missing")
        server.close(); return 1
    check("TrioBackend.start_tls exists", True)

    state = {}

    async def scenario():
        backend = TrioBackend()
        ctx = SSLConfig().load_ssl_context_no_verify(HTTPVersionConfig())
        timeout = TimeoutConfig(5)
        stream = await backend.open_tcp_stream("127.0.0.1", port, None, timeout)
        try:
            def cipher_of(s):
                inner = getattr(s, "stream", None)
                return inner.cipher() if isinstance(inner, trio.SSLStream) else None

            state["plain_cipher"] = cipher_of(stream)
            upgraded = await backend.start_tls(stream, "127.0.0.1", ctx, timeout)
            state["tls_cipher"] = cipher_of(upgraded)
            await upgraded.write(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n", timeout)
            state["response"] = await upgraded.read(4096, timeout)
        finally:
            try: await stream.close()
            except Exception: pass

    try:
        trio.run(scenario)
    except Exception as e:
        check("scenario ran", False, f"{type(e).__name__}: {e}")
        traceback.print_exc()
        server.close(); return 1
    check("scenario ran", True)

    check("plain stream has no cipher", state.get("plain_cipher") is None,
          f"got {state.get('plain_cipher')!r}")
    check("after start_tls: real cipher present", state.get("tls_cipher") is not None,
          f"got {state.get('tls_cipher')!r}")
    resp = state.get("response") or b""
    check("HTTP 200 over upgraded stream", resp.startswith(b"HTTP/1.1 200 OK"),
          f"got {resp[:40]!r}")

    server.close()
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{npass}/{len(RESULTS)} checks passed")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
