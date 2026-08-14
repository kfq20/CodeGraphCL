# Task — viper: UnmarshalExact drops env-backed struct fields when AutomaticEnv is on

## Symptom (external behavior)

`UnmarshalExact` decodes the config into a struct and errors on unused fields, but when
`AutomaticEnv()` is enabled and an env-key replacer maps struct-field paths to environment
variables, the env-backed fields come back as zero values. Only fields explicitly set via `Set`
populate; every field whose value should come from an environment variable is missing. The cause
is that `UnmarshalExact` decodes from the static all-settings map, which does not consult the
env-var layer for struct-field keys.

## Reproduction

```
t.Setenv("NAME", "Steve")
v := New()
v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
v.AutomaticEnv()
v.Set("port", 1234)
var config Configuration  // has Name string, Port int, ...
v.UnmarshalExact(&config)
// config.Name == "" (expected "Steve"), config.Port == 1234 (ok)
```

## Acceptance

`UnmarshalExact` must populate env-backed struct fields when `AutomaticEnv` is enabled, while
still erroring on unused fields. The struct-field keys must be derived from the destination struct
and fed into the env-aware settings lookup, so each field is decoded the same way `v.Get(<key>)`
would return it. Existing decode behavior for non-env settings is unchanged.

## Constraints

- Do NOT create or modify any `*_test.go` file — the verifier applies its own tests after you finish.
- The fix belongs in the `UnmarshalExact` method's decode-source selection.

When done, output a one-line summary of what you changed.
