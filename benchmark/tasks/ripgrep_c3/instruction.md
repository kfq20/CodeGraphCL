# Task — ripgrep: parent `.ignore` not matched when searching a subdirectory

## Symptom (external behavior)

When a `.ignore` file sits in a parent directory and ripgrep is invoked on a *subdirectory*
(possibly given as `./subdir`), the `.ignore` patterns that should match are not applied
correctly. Files that the parent `.ignore` is supposed to exclude still appear in results.

## Reproduction

Given this tree:
```
.                (cwd)
├── .ignore      contains: rust/target
├── rust/
│   ├── source.rs          (contains "needle")
│   └── target/
│       └── out.html       (contains "needle")
```

Running `rg --files-with-matches needle rust` (or `./rust`) should list `rust/source.rs`
**and exclude** `rust/target/out.html`, because the parent `.ignore` says `rust/target`.
Currently the target file is NOT excluded — the `.ignore` fails to apply.

## Acceptance

Fix the search so a parent `.ignore`'s patterns apply correctly when the search root is a
subdirectory (both `rust` and `./rust` forms). Do NOT break the case where the search root is
`.` itself. Existing regression tests must keep passing.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix should be in the ignore-crate path-handling for subdirectory search.

When done, output a one-line summary of what you changed.
