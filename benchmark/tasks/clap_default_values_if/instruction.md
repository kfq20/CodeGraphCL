# Task — clap: a conditional default can only supply one value

## Symptom (external behavior)

An argument can be configured so that it falls back to a default only when some *other*
argument is present (optionally, present with a particular value). That conditional fallback
can supply exactly **one** value.

This breaks down for arguments that accept several values at once. There is no way to express
"when `--opt` is `value`, this argument should fall back to `df1` **and** `df2`". The
unconditional side of the builder already has both shapes — one that takes a single fallback
and one that takes a whole list of fallbacks — but the conditional side only has the
single-value shape, so multi-value arguments cannot be given a conditional fallback at all.

## Reproduction

Build an app with an argument that takes two values and give it a conditional fallback list of
two entries, keyed on another argument being present with a given value. Run the app supplying
only that other argument. There is no builder call that accepts a list of conditional
fallbacks, and even the storage behind the existing conditional fallback holds a single entry,
so at most one value could ever be applied.

## Acceptance

Make it possible to attach a *list* of conditional fallback values to an argument, keyed on
another argument's presence/value — mirroring the naming and shape of the existing
unconditional list-valued fallback. A batch form that registers several such conditions in one
call should exist too, mirroring the existing batch form of the single-value conditional
fallback. When the condition fires, **all** of the listed values must reach the parsed
matches, in the order given. Existing single-value conditional fallback behavior (including
its reset/`None` behavior and its batch form) must keep working unchanged.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix belongs in the argument-builder default-value configuration surface, plus whatever
  the parser needs so the values actually land in the matches.

When done, output a one-line summary of what you changed.
