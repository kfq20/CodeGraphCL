# Task — httpx: non-ASCII filenames in multipart uploads are incorrectly encoded

## Symptom (external behavior)

When building a multipart form-data request with a filename containing non-ASCII characters
(e.g. `näme`) or special characters (backslash, double-quote, control characters), the
Content-Disposition header parameter values are encoded using URL percent-encoding
(`urllib.parse.quote`), which produces different output than the HTML5 form encoding
specification requires. This causes servers to misinterpret the filename.

For example, a filename `näme` should produce `filename="näme"` (UTF-8 bytes in the header),
but the current code percent-encodes the non-ASCII bytes. A backslash in the filename should
be escaped as `\\`, but the current code leaves it unescaped. Control characters (0x00-0x1F)
should be percent-encoded as `%XX`, but the current code passes them through.

## Reproduction

Call the internal header-formatting function with a filename like `näme` and check the output
bytes. The output does not match what an HTML5 form submission would produce. The same
discrepancy exists for filenames with backslashes, double-quotes, or control characters.

## Acceptance

Header parameters in multipart Content-Disposition must be encoded per the HTML5 form
encoding specification: non-ASCII characters are passed through as UTF-8 bytes, backslashes
are escaped (`\` -> `\\`), double-quotes are percent-encoded (`"` -> `%22`), and control
characters (0x00-0x1F, except 0x1B) are percent-encoded as `%XX`. The parameter value is
wrapped in double-quotes. Both string and bytes input must be supported.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the multipart encoding module.

When done, output a one-line summary of what you changed.
