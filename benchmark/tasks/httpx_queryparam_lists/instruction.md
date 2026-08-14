# Task — httpx: passing a dict with list values to QueryParams raises TypeError

## Symptom (external behavior)

When constructing query parameters from a dict that has list or tuple values (e.g.
`{"tag": ["python", "dev"]}`), the constructor raises a `TypeError` because it tries to
coerce the entire list to a string. The expected behavior is to flatten list/tuple values
into multiple key-value pairs, producing `?tag=python&tag=dev` (the HTTP convention for
repeated query params).

## Reproduction

Construct query params with `QueryParams({"a": ["123", "456"], "b": 789})`. It raises
`TypeError` instead of producing a `QueryParams` with `a=123&a=456&b=789`. The same
issue occurs with tuple values `{"a": ("123", "456"), "b": 789}`.

## Acceptance

When a dict value is a list or tuple (but NOT a str or bytes, which are scalar), each item
must become a separate key-value pair. Scalar values (str, int, float, bool, None) remain
single pairs. The resulting `QueryParams` must preserve the order of keys and the order of
items within each list/tuple.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The flattening logic and the query param type definitions both need changes.

When done, output a one-line summary of what you changed.
