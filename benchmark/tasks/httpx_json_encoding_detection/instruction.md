# Task — httpx: JSON responses with non-UTF-8 encoding fail to parse when no charset is declared

## Symptom (external behavior)

When a response has `Content-Type: application/json` (without an explicit charset) and the
JSON body is encoded in UTF-16 or UTF-32, calling `.json()` on the response raises a
`UnicodeDecodeError`. The method blindly assumes the content is UTF-8 and decodes it
accordingly, which fails for multi-byte encodings even though the encoding is determinable
from the byte content itself.

If the charset IS declared in the Content-Type header (e.g. `application/json; charset=utf-16`),
`.json()` works because the text property uses that charset. The bug only manifests when the
charset is absent and the content is non-UTF-8.

## Reproduction

Create a response with `content = json.dumps({"hello": "world"}).encode("utf-32-be")` and
`headers = {"Content-Type": "application/json"}` (no charset). Call `response.json()`. It
raises `UnicodeDecodeError` instead of returning the parsed dict.

## Acceptance

When the Content-Type charset is absent, `.json()` must detect the encoding from the raw
byte content (JSON content always starts with ASCII characters, so the byte pattern reveals
the encoding width and endianness) and decode accordingly. If detection fails, fall back
to the text property (which uses the declared charset or a default). The method must also
accept and forward `**kwargs` to the JSON decoder.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix spans the response model and a utility module.

When done, output a one-line summary of what you changed.
