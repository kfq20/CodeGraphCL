# Task — fastify: a plugin prefix ending with '/' produces double-slash route URLs

## Symptom (external behavior)

When a plugin is registered with a prefix that ends with a '/' (e.g. `'/v1/'`) and a route
inside that plugin uses a path starting with '/' (e.g. `'/route'`), the combined URL becomes
`'/v1//route'` — a double slash. Incoming requests to the intended `'/v1/route'` don't match
the route (the router sees a different path), so the route is treated as not found.

The same problem occurs for nested plugins: a sub-plugin registered inside the trailing-slash
plugin with its own trailing-slash prefix (e.g. `'/inner/'`) inherits a double slash in the
combined prefix, so all routes inside the nested plugin also fail to match.

## Reproduction

Register a plugin with prefix `'/v1/'`. Inside it, add a `GET '/route'` handler. Also register
a nested sub-plugin with prefix `'/inner/'` containing a `GET '/route2'` handler. Inject a
request to `'/v1/route'` and `'/v1/inner/route2'`. On base, neither route matches (the URLs
registered are `'/v1//route'` and `'/v1//inner//route2'`), so the responses are 404. After the
fix, both routes match and return their expected payloads.

## Acceptance

When an enclosing plugin's prefix ends with '/', the leading '/' must be stripped from a route
path that starts with '/', so the combined URL has a single slash at the join point. The same
normalization must apply to a nested plugin's prefix when combined with the parent's trailing
slash. Routes that don't start with '/' (relative to a trailing-slash prefix) and routes under
a prefix without a trailing slash must keep working unchanged.

## Constraints

- Do NOT create or modify files under `test/` — the verifier applies its own tests after you finish.
- The fix belongs in the route-prefix construction and the route path construction.

When done, output a one-line summary of what you changed.
