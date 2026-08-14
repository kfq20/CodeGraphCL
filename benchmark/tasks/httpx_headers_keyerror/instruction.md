# Task — httpx: deleting a non-existent header silently no-ops instead of raising KeyError

## Symptom (external behavior)

`Headers` behaves like a `typing.MutableMapping[str, str]`, but deleting a key through the mapping
interface does not match the mapping contract: deleting a key that is not present silently does
nothing, whereas a standard mapping (such as `dict`) raises `KeyError` for an absent key. Code that
relies on deleting a header to surface a missing-header condition (e.g. redirect middleware that
strips headers) therefore cannot detect when the header was already absent, and bugs that drop a
required header go unnoticed.

## Reproduction

Construct `headers = Headers({"foo": "bar"})` and delete the absent key `"baz"` via the mapping
interface. On the current code this returns normally with no error. The expected behavior — matching
`dict` semantics — is to raise `KeyError`.

## Acceptance

Deleting a header that is not present must raise `KeyError`, matching the standard mapping contract.
When the key is present, the existing behavior (remove all entries with that key) is unchanged.
Callers that previously deleted a possibly-absent header must be updated so they no longer rely on
silent deletion — they should tolerate a missing key explicitly.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the `Headers` mapping implementation; redirect middleware that strips headers
  must also be adjusted so it does not break when the header is now correctly reported as absent.

When done, output a one-line summary of what you changed.
