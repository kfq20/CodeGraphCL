# Task — ripgrep: whitelisted hidden file not found when search root is `.` or `./`

## Symptom (external behavior)

A parent `.ignore` uses a negation pattern to whitelist a hidden file (e.g. `!.foo.txt`).
When ripgrep lists files (`--files`) and the search root is the current directory given as
`.`, `./`, or a subdirectory, the whitelisted hidden file is NOT included — it should be.

## Reproduction

Given this tree (cwd is the parent):
```
.                (cwd)
├── .ignore      contains: !.foo.txt
└── subdir/
    └── .foo.txt      (exists)
```

Running `rg --files`, `rg --files .`, `rg --files ./` should each list `subdir/.foo.txt`
(or `./subdir/.foo.txt`). Currently the file is missing from results — the parent
whitelist is not honored for hidden files when the search root is `.` / `./`.

## Acceptance

Fix the search so a parent `.ignore`'s negation whitelist applies to hidden files when the
search root is `.`, `./`, or a subdirectory. Existing regression tests must keep passing.

## Constraints

- Do NOT create or modify files under `tests/` — the verifier applies its own tests after you finish.
- The fix is in the ignore-crate path handling for parent gitignore matching.

When done, output a one-line summary of what you changed.
