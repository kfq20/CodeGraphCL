# Task — fastify: a JSON response with an explicit charset has its content-type clobbered

## Symptom (external behavior)

When a handler sends a JSON response and the content type already includes a charset (for
example, the full media type with a charset parameter), the reply logic does not recognize it
as a JSON content type — it only matches the exact, bare JSON media type — so the JSON
serialization branch is skipped and the content type is mishandled.

Worse, when the logic does try to set the default content type for a JSON response, it
unconditionally overwrites the content type even if the caller already supplied a charset,
dropping the caller's chosen charset in favor of the framework default.

## Reproduction

Send a JSON response where the content type is the JSON media type plus a charset parameter.
The reply does not take the JSON path (the charset-suffixed form is not recognized), and the
caller's charset is clobbered when the default content type is applied.

## Acceptance

Treat a content type as a JSON content type when the bare JSON media type appears anywhere in
the content-type string (not just as an exact match), so the JSON serialization branch is taken
for charset-suffixed JSON content types too. When applying the framework's default content type,
do not clobber a charset the caller already set — only set the default when no charset is
present.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's content-type / serialization handling.

When done, output a one-line summary of what you changed.
