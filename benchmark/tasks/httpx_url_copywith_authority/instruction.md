# Task — httpx: URL.copy_with does not update host, port, username, or password

## Symptom (external behavior)

Calling `copy_with()` with `host=`, `port=`, `username=`, or `password=` keyword arguments
does not update the URL's authority component. The resulting URL retains the old host, port,
and credentials — the individual component kwargs are silently ignored.

## Reproduction

Create a URL like `URL("https://example.org")`. Call `url.copy_with(username="user",
password="pass", port=444, host="example.net")`. The resulting URL is still
`https://example.org` — none of the components were applied. The `str(new)` does not
reflect the new host/port/credentials.

## Acceptance

When `copy_with()` receives any of `username`, `password`, `host`, or `port`, it must
compose them (with the existing values as defaults for any not specified) into the
authority component string in the standard format: `[user[:pass]@]host[:port]`. The
composed authority is then passed to the underlying URI builder. The resulting URL must
reflect all specified components in both its attributes and its string representation.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the URL model's copy method.

When done, output a one-line summary of what you changed.
