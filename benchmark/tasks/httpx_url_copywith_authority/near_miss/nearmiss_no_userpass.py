"""Near-miss A for httpx_url_copywith_authority: build authority host:port but forget userpass.

The gold copy_with() composes authority = host + ":port" + "user:pass@". This near-miss builds
host:port but skips the username/password prefix. Plausible "host:port is the common case,
credentials are rare" — but the test passes username/password. Caught: getattr(new, "username")
is None != "username", str(new) missing the userpass@ prefix.

Distinct from B: A drops userpass, B drops port.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_no_userpass.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """            authority = host
            if port is not None:
                authority += f":{port}"
            if username is not None:
                userpass = username
                if password is not None:
                    userpass += f":{password}"
                authority = f"{userpass}@{authority}"

            kwargs["authority"] = authority"""

NEW = """            # NEAR-MISS A: host:port only, forget userpass
            authority = host
            if port is not None:
                authority += f":{port}"

            kwargs["authority"] = authority"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "models.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: authority composition block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (host:port only, forget userpass) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
