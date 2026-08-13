# Task — fastify: redirect clobbers a status code the caller set beforehand

## Symptom (external behavior)

When a handler sets a specific HTTP status code on the reply and then issues a redirect, the
redirect overwrites that status code with its own default (302) instead of honoring the code
the caller already chose. The explicitly-set code is lost.

Calling redirect with no explicit code argument should reuse the status code the caller set
earlier; calling redirect with an explicit code argument should use that one (overriding the
earlier set). Today both paths collapse to the redirect default, ignoring the earlier set.

## Reproduction

A route does `reply.code(307).redirect('/')`. The response comes back with status 302, not 307.
The 307 the caller chose before the redirect was discarded.

## Acceptance

Make redirect honor a status code the caller set before the redirect call, when the redirect
itself is given no explicit code. When the redirect IS given an explicit code, that code wins.
A handler that sets a code then redirects (no explicit code) must respond with the set code;
existing redirect behavior (redirect with an explicit code, or redirect with no prior set) must
keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply's redirect implementation.

When done, output a one-line summary of what you changed.
