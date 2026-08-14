# Task — httpx: boolean query parameters render as Python strings instead of lowercase

## Symptom (external behavior)

When constructing query parameters from a dict, boolean values are rendered using Python's
default `str()` representation: `True` -> `"True"`, `False` -> `"False"`. This produces
query strings like `?a=True` instead of the expected `?a=true` (lowercase). Web frameworks
and HTTP conventions expect lowercase `true`/`false` for boolean query params.

Similarly, `None` values render as the string `"None"` instead of an empty string, producing
`?a=None` instead of `?a=`.

## Reproduction

Construct query params with `QueryParams({"a": True})` and check `str(q)`. It returns
`"a=True"` instead of `"a=true"`. Construct with `{"a": None}` and it returns `"a=None"`
instead of `"a="`. Float and int values work correctly via `str()`.

## Acceptance

Boolean values must be coerced to lowercase strings: `True` -> `"true"`, `False` -> `"false"`.
`None` must be coerced to an empty string `""`. Int and float values use `str()` as before.
This coercion must apply to all query param values, whether the source is a dict, a list of
tuples, or a string.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The coercion utility and the query param construction both need changes.

When done, output a one-line summary of what you changed.
