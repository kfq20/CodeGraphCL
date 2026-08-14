# Task — viper: a custom mapstructure decode hook cannot be set as a default on a Viper instance

## Symptom (external behavior)

`Viper` ships a fixed default decode-hook chain (string-to-time-duration, weak string-to-slice) used
by `Unmarshal` / `UnmarshalKey` / `UnmarshalExact`. There is no way to supply a custom decode hook
that applies by default to every decode on a given `Viper` instance. Callers that need, for example,
a string-to-`map[string]string` hook (so a JSON-encoded config value decodes into a map field) have
no per-instance option and must pass a decoder-config option on every call, which is easy to forget.

## Reproduction

```
// build a decode hook that turns a JSON string into a map[string]string
hook := /* a composed decode hook incl. string-to-map */
v := NewWithOptions(/* the option that sets this hook as the instance default */)
v.Set("credentials", `{"foo":"bar"}`)
var C struct{ Credentials map[string]string }
v.Unmarshal(&C)
// C.Credentials == nil (expected {"foo":"bar"})
```

The option that would carry the hook onto the instance does not exist, so the hook is never applied
and the string value is not decoded into the map field.

## Acceptance

A new option must let the caller set a default decode hook on a `Viper` instance. When set, that
hook is used by the decoder configuration for `Unmarshal`, `UnmarshalKey`, and `UnmarshalExact`
unless overridden by a per-call decoder option. A nil hook must be ignored (no-op). When no hook is
set, the existing default hook chain is used unchanged.

## Constraints

- Do NOT create or modify any `*_test.go` file — the verifier applies its own tests after you finish.
- The fix adds a new option and wires it into the shared decoder-config builder used by all three
  Unmarshal entry points.

When done, output a one-line summary of what you changed.
