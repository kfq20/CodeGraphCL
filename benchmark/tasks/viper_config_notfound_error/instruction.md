# Task — viper: ReadInConfig returns the wrong error type when the config file does not exist

## Symptom (external behavior)

When `SetConfigFile` points at a path that does not exist on the configured filesystem, calling
`ReadInConfig` does NOT return a `ConfigFileNotFoundError`. Instead it falls through to the raw
file-read error (a path/os error), whose concrete type is not `ConfigFileNotFoundError`. Callers
that check the error type with `errors.As` / `assert.IsType` against `ConfigFileNotFoundError` to
distinguish "config missing" from "config malformed" therefore misclassify the missing-file case.

## Reproduction

```
v := New()
v.SetConfigFile("does-not-exist.yaml")
err := v.ReadInConfig()
// err is a path/os error from ReadFile, not a ConfigFileNotFoundError
assert.IsType(t, ConfigFileNotFoundError{}, err)  // FAILS
```

## Acceptance

When the configured config file does not exist, `ReadInConfig` must return a
`ConfigFileNotFoundError` (with the file name set). When the file exists but cannot be read for
another reason, the existing behavior (return the underlying read error) is unchanged. The default
value still loads after a missing-config error, as before.

## Constraints

- Do NOT create or modify any `*_test.go` file — the verifier applies its own tests after you finish.
- The fix belongs in the `ReadInConfig` file-resolution / read path, before the read is attempted.

When done, output a one-line summary of what you changed.
