# clap_error_newline experience atoms (clap_error_help_newline -> clap_error_newline edge)

The producer (2eb69def4ecb, "fix(error): Ensure trailing newline without help") established the
invariant that every clap error message must terminate with a trailing newline, and fixed the
help/subcommand formatting path where a branch omitted it. The consumer (a72e5726f872,
"fix(error): Ensure newline on value_of_t not found") is LITERALLY the audit follow-up — its
commit message reads "Found this when auditing for cases related to #2787", where #2787 is the
issue the producer fixed.

This is the strongest textual evidence of a real experience dependency in the bank: the producer
established both the invariant AND the audit habit; the consumer applies them to a second site.

provenance:
  producer_sha: 2eb69def4ecb   # producer-era: errors must end with a trailing newline; the help
                               # path had a branch that omitted it -> ensure every branch terminates
  consumer_sha: a72e5726f872   # consumer: the same invariant violated at the argument-not-found site
  audit: correct atom contains ONLY producer-era knowledge (the invariant + "audit the other
    branches"). It does NOT name the value_of_t / argument-not-found site — that is the consumer's
    discovery and naming it would be hindsight leakage (blocked by Separability S4).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct -->
Project context (from prior work on this codebase, provenance: commit 2eb69def4): every error
message this library produces must terminate with a trailing newline — downstream code prints
errors directly and relies on them being line-terminated. A recent fix uncovered that the
error-formatting code has several independent branches, and one of them fell through without
emitting the terminating newline. The lesson recorded at the time: when touching error
formatting, do not assume the common path covers every case — each branch that can produce a
finished message must terminate it itself, and the other branches are worth auditing for the
same omission.
<!-- /ATOM:correct -->

<!-- ATOM:wrong -->
Project context (from prior work on this codebase, provenance: an earlier convention in this
codebase): error messages are returned as bare strings without a trailing newline — line
termination is the caller's responsibility, not the library's. The formatting code deliberately
emits the message body only, so that callers embedding an error mid-sentence (in a log line, a
JSON field, a wrapped error) do not have to strip a stray newline. Do not append terminating
newlines inside the error formatter.
<!-- /ATOM:wrong -->

<!-- ATOM:irrelevant -->
Project context (from prior work on this codebase): this library's builder API centers on `App`
and `Arg`; subcommands are registered with `.subcommand()`, parsing produces an `ArgMatches`,
and settings are toggled via `AppSettings`. The derive API mirrors the builder through
`#[derive(Parser)]` attributes. These are real project facts about the public API surfaces.
<!-- /ATOM:irrelevant -->

provenance_note: the WRONG atom is scope-plausible rather than absurd — "the library returns bare
messages, the caller terminates lines" is a real convention in many CLI libraries (and was
arguably clap's own earlier behavior, which is why the producer commit was needed). An agent that
follows it will decline to append the newline and fail the verifier.
