# Task — httpx: assigning Client.headers / Client.cookies stores raw input instead of converting

## Symptom (external behavior)

`Client` exposes `headers` and `cookies` attributes that are constructed from the constructor
arguments by wrapping them in `Headers(...)` / `Cookies(...)` so the stored value is always a
normalized model object. But after construction, assigning to these attributes — e.g.
`client.headers = {"a": "b"}` or `client.cookies = some_cookiejar` — overwrites the attribute with
the raw input verbatim (a plain `dict`, or a raw `CookieJar`). The stored value is then NOT a
`Headers` / `Cookies` instance, so downstream code that relies on the model API (case-insensitive
header lookup, cookiejar extraction) breaks.

## Reproduction

```
client = Client()
client.headers = {"a": "b"}
isinstance(client.headers, Headers)  # False — a raw dict was stored
client.headers["A"]                  # KeyError — dict is case-sensitive, not a Headers
```

Assigning a `CookieJar` to `client.cookies` similarly leaves a raw `CookieJar` instead of a
`Cookies` model, so the request path that reads cookies does not see them.

## Acceptance

Assigning to `Client.headers` must convert the value to a `Headers` instance; assigning to
`Client.cookies` must convert the value to a `Cookies` instance. Reading the attribute must return
the normalized model object. Constructor behavior is unchanged. The conversion must apply on every
assignment, not only at construction time.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the client's attribute access for headers and cookies.

When done, output a one-line summary of what you changed.
