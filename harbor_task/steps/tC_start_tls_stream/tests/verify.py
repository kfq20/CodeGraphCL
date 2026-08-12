"""Hermetic behavioral verifier for T_C (start_tls moved onto the stream; returns new stream).

T_C revises the contract: start_tls moves from the backend to the STREAM, signature
`stream.start_tls(hostname, ssl_context, timeout) -> new_stream`. The T_A/T_B shape
(`backend.start_tls(stream, ...)`, mutate in place) is STALE for T_C.

Hermetic (same as T_B): stdlib ssl TLS server in a thread + trio.run, no uvicorn/pytest-trio.
Checks:
  1. TCPStream (trio) exposes start_tls (the contract moved onto the stream);
  2. the returned object is a DIFFERENT stream (not self) — the "new stream" revision;
  3. plain stream has no cipher; after stream.start_tls the returned stream has a real cipher;
  4. an HTTP request over the upgraded stream returns real HTTP 200.

(2)+(3) are what a stale "mutate in place, return same" prior cannot fake: returning self
leaves the plain stream, no cipher; the verifier needs a real handshake on a new object.
Also catches a near-miss that leaves backend.start_tls (AttributeError on stream.start_tls).
"""
from __future__ import annotations
import os, socket, ssl, sys, threading, traceback

sys.path.insert(0, os.environ.get("CGCL_WORKDIR", "/pool/work"))
RESULTS = []
def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def make_cert(tmpdir):
    import trustme
    ca = trustme.CA(); cert = ca.issue_cert("127.0.0.1")
    pem = os.path.join(tmpdir, "cert.pem"); key = os.path.join(tmpdir, "key.pem")
    cert.cert_chain_pems[0].write_to_path(pem); cert.private_key_pem.write_to_path(key)
    return pem, key


class TLSEchoServer:
    def __init__(self, certfile, keyfile, port):
        self.certfile, self.keyfile, self.port = certfile, keyfile, port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", port)); self.sock.listen(5)
        self.stop = False
    def _serve(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(self.certfile, self.keyfile)
        self.sock.settimeout(0.5)
        while not self.stop:
            try: conn, _ = self.sock.accept()
            except (socket.timeout, OSError): continue
            try:
                tls = ctx.wrap_socket(conn, server_side=True)
                try: tls.recv(65536); tls.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nhi")
                finally:
                    try: tls.close()
                    except Exception: pass
            except Exception:
                try: conn.close()
                except Exception: pass
    def start(self): self.thread = threading.Thread(target=self._serve, daemon=True); self.thread.start()
    def close(self):
        self.stop = True
        try: self.sock.close()
        except Exception: pass


def main():
    import tempfile
    tmp = tempfile.mkdtemp(); port = 8444
    certfile, keyfile = make_cert(tmp)
    server = TLSEchoServer(certfile, keyfile, port); server.start()
    try:
        import trio
        from httpx.concurrency.trio import TrioBackend, TCPStream
        from httpx import SSLConfig, HTTPVersionConfig, TimeoutConfig
        check("import TrioBackend + TCPStream", True)
    except Exception as e:
        check("import TrioBackend + TCPStream", False, f"{type(e).__name__}: {e}")
        server.close(); return 1

    if not hasattr(TCPStream, "start_tls"):
        check("TCPStream.start_tls exists (contract moved to stream)", False, "method missing")
        server.close(); return 1
    check("TCPStream.start_tls exists (contract moved to stream)", True)

    st = {}
    async def scenario():
        backend = TrioBackend()
        ctx = SSLConfig().load_ssl_context_no_verify(HTTPVersionConfig())
        timeout = TimeoutConfig(5)
        stream = await backend.open_tcp_stream("127.0.0.1", port, None, timeout)
        try:
            def cipher_of(s):
                inner = getattr(s, "stream", None)
                return inner.cipher() if isinstance(inner, trio.SSLStream) else None
            st["plain_cipher"] = cipher_of(stream)
            st["plain_id"] = id(stream)
            upgraded = await stream.start_tls("127.0.0.1", ctx, timeout)
            st["upgraded_id"] = id(upgraded)
            st["upgraded_cipher"] = cipher_of(upgraded)
            await upgraded.write(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n", timeout)
            st["response"] = await upgraded.read(4096, timeout)
        finally:
            try: await stream.close()
            except Exception: pass

    try: trio.run(scenario)
    except Exception as e:
        check("scenario ran", False, f"{type(e).__name__}: {e}")
        traceback.print_exc(); server.close(); return 1
    check("scenario ran", True)

    check("plain stream has no cipher", st.get("plain_cipher") is None, f"got {st.get('plain_cipher')!r}")
    # the "new stream" revision: upgraded must be a different object than plain
    _is_new = st.get("upgraded_id") != st.get("plain_id")
    check("upgraded is a NEW stream (not mutate-in-place)", _is_new,
          "" if _is_new else "returned the same object (stale mutate-in-place shape)")
    check("upgraded stream has real cipher", st.get("upgraded_cipher") is not None,
          f"got {st.get('upgraded_cipher')!r}")
    resp = st.get("response") or b""
    check("HTTP 200 over upgraded stream", resp.startswith(b"HTTP/1.1 200 OK"), f"got {resp[:40]!r}")

    server.close()
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{npass}/{len(RESULTS)} checks passed")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
