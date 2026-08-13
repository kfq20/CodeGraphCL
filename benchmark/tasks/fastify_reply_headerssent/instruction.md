# Task — fastify: sending a stream after writing headers manually crashes

## Symptom (external behavior)

When a handler writes response headers manually (via the underlying response object's
write-headers method) and then sends a stream as the reply body, the send step throws an error
because it tries to set headers again on a response whose headers have already been sent. The
manual header write and the framework's own header-setting step collide.

Sending a stream without a prior manual header write works fine; only the combination of
manual-headers-then-stream crashes.

## Reproduction

In a route handler, call the underlying response's write-headers method to set custom headers,
then send a readable stream as the reply. The send throws an error about headers already sent
(or setting a header after they were sent), and the response is broken.

## Acceptance

When sending a reply body after headers have already been written manually, the framework must
not attempt to set headers again; it should proceed with sending the body (and may warn that
manual header writes should be avoided in this mode). Sending a stream without prior manual
headers must keep working exactly as before.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the reply send implementation.

When done, output a one-line summary of what you changed.
