# Task — viper: Sub() does not propagate the custom key delimiter to the sub-viper

## Symptom (external behavior)

`Viper.Sub(key)` extracts a sub-configuration into a new `Viper` instance. When the parent was
created with a custom key delimiter (e.g. `NewWithOptions(KeyDelimiter("::"))`), the sub-viper
does NOT inherit that delimiter. Consequently, keyed lookups on the sub-viper that rely on the
custom delimiter fail: a path like `"steve@hacker.com::created"` is not split on `"::"` and the
value comes back as `nil`, even though it is present in the parent's config.

## Reproduction

```
v := NewWithOptions(KeyDelimiter("::"))
v.SetConfigType("yaml")
v.unmarshalReader(strings.NewReader(yamlExampleWithDot), v.config)
subv := v.Sub("emails")
subv.Get("steve@hacker.com::created")  // returns nil — should return "01/02/03"
```

On the parent, the same lookup works because the delimiter is honored.

## Acceptance

The sub-viper returned by `Sub()` must inherit the parent's key delimiter. After the fix, the
reproduction's `subv.Get("steve@hacker.com::created")` returns the stored value. Other inherited
fields (automaticEnvApplied, envPrefix, envKeyReplacer) must continue to be propagated as before.

## Constraints

- Do NOT create or modify any `*_test.go` file — the verifier applies its own tests after you finish.
- The fix belongs in the sub-viper construction path inside `Sub()`.

When done, output a one-line summary of what you changed.
