# Task — ripgrep: line terminator is lost when replacing matches in CRLF mode

## Symptom (external behavior)

When the searcher is configured for CRLF line terminators AND a replacement is set, the printer
drops the line terminator from the output of each matched line. So a search that should print
`hello\nworld\r\n` instead prints `hello\nworld` (no trailing `\r\n`) — the last matched line is
missing its terminator.

Without a replacement the terminator is preserved correctly; only the replace path loses it. The
terminator must be preserved in both modes so the printed output matches the input's line endings.

## Reproduction

Search a two-line haystack `hello\nworld\r\n` for `.` (any char) with a CRLF line terminator and
`-r` set to `$0` (replace with the match itself — a no-op replace). Expected output:
`hello\nworld\r\n`. Actual (base): `hello\nworld` — the `\r\n` of the second line is gone.

## Acceptance

- When a replacement is in effect and the searcher uses CRLF (or any) line terminators, the line
  terminator that was trimmed from the end of the matched line before the regex ran must be
  re-appended to the output after the replacement is written.
- When no replacement is set, the existing behavior (terminator preserved) is unchanged.
- The fix must not double-append the terminator when none was present.

## Constraints

- Do NOT create or modify any test file or the inline test block — the verifier applies its own test after you finish.
- The fix belongs in the printer's replacement helper.

When done, output a one-line summary of what you changed.
