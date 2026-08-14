"""Near-miss B for httpx_url_copywith_authority: build authority userpass@host but forget port.

The gold copy_with() composes authority = host + ":port" + "user:pass@". This near-miss builds
userpass@host but skips the ":port" suffix. Plausible "host is the main part, port is optional"
— but the test passes port=444. Caught: getattr(new, "port") is 443 != 444, str(new) missing
the :444 suffix.

Distinct from A: B drops port, A drops userpass.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_no_port.py <repo_dir>
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

NEW = """            # NEAR-MISS B: userpass@host only, forget port
            authority = host
            if username is not None:
                userpass = username
                if password is not None:
                    userpass += f":{password}"
                authority = f"{userpass}@{authority}"

            kwargs["authority"] = authority"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "models.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: authority composition block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (userpass@host only, forget port) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
