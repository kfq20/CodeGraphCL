# Task — viper: Unmarshal does not populate env-backed fields when AutomaticEnv is on

## Symptom (external behavior)

When `AutomaticEnv()` is enabled and an env-key replacer maps struct-field paths to environment
variables (e.g. `"port"` -> `PORT`, `"authentication.secret"` -> `SECRET`), calling `Unmarshal`
into a struct does NOT populate the fields from the environment. The struct comes back with zero
values for env-backed fields, even though `v.Get("port")` would return the env value directly.
The cause is that `Unmarshal` decodes from the static all-settings map, which does not consult the
env-var layer for struct-field keys the way the keyed getter does.

## Reproduction

```
t.Setenv("PORT", "1313")
v := New()
v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
v.AutomaticEnv()
var config struct { Port int `mapstructure:"port"` }
v.Unmarshal(&config)
// config.Port == 0, expected 1313
```

## Acceptance

`Unmarshal` must populate env-backed struct fields when `AutomaticEnv` is enabled. The struct-field
keys must be derived from the destination struct and fed into the settings lookup that consults the
env layer, so that a field whose value is provided by an environment variable is decoded the same
way `v.Get(<key>)` would return it. The existing decode behavior for non-env settings is unchanged.

## Constraints

- Do NOT create or modify any `*_test.go` file — the verifier applies its own tests after you finish.
- The fix belongs in the `Unmarshal` method's decode-source selection.

When done, output a one-line summary of what you changed.
