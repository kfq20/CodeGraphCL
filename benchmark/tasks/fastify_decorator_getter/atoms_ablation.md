# fastify decorator_getter carrier-ablation atoms (Phase 3.1)

Length-matched short/long pairs for the 5-condition carrier ablation (reset, correct_short,
irrelevant_short, correct_long, irrelevant_long). The short pair and long pair are each
token-matched within 5%; same sentence structure, paragraph count, and technical density;
only the semantic content differs between correct and irrelevant. This file is read when
CGCL_ATOMS_FILE=atoms_ablation.md is set — the original atoms.md is untouched (anti-tampering).

provenance: commit c1aac3cd85 (the decorate getter/setter convention).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct_short -->
Project context (from prior work on this codebase, provenance: commit c1aac3cd85): a decorator that carries accessor functions is configured with those accessors, not as a plain value, and every decoration entry point that takes a config object should honor the same accessor shape so decorators stay consistent.
<!-- /ATOM:correct_short -->

<!-- ATOM:irrelevant_short -->
Project context (from prior work on this codebase, provenance: commit c1aac3cd85): a route handler that returns a payload is registered with its method and path, and every request entry point that takes a handler function should honor the same routing shape so handlers stay consistent.
<!-- /ATOM:irrelevant_short -->

<!-- ATOM:correct_long -->
Project context (from prior work on this codebase, provenance: commit c1aac3cd85): a decorator that carries accessor functions is configured with those accessors, not as a plain value, and every decoration entry point that takes a config object should honor the same accessor shape so decorators stay consistent. The accessor form is recognized when the config object supplies the named accessor functions; the property is then bound through those accessors instead of being written as a stored value. This was established for the primary decoration entry point and is meant to carry over: any sibling decoration entry point that also accepts a config object should recognize the identical accessor form, so that a decorator written once behaves the same way no matter which surface it is attached to. Applying the accessor recognition uniformly is the intended invariant; a decoration surface that silently ignores the accessor form and stores only a plain value breaks that uniformity and leaves the decorator mis-bound on that surface.
<!-- /ATOM:correct_long -->

<!-- ATOM:irrelevant_long -->
Project context (from prior work on this codebase, provenance: commit c1aac3cd85): a route handler that returns a payload is registered with its method and path, and every request entry point that takes a handler function should honor the same routing shape so handlers stay consistent. The handler form is recognized when the registration supplies the named method and path; the route is then bound through that registration instead of being written as a stored callback. This was established for the primary routing entry point and is meant to carry over: any sibling request entry point that also accepts a handler function should recognize the identical routing form, so that a handler written once behaves the same way no matter which surface it is attached to. Applying the routing recognition uniformly is the intended invariant; a request surface that silently ignores the routing form and stores only a stored callback breaks that uniformity and leaves the handler mis-bound on that surface.
<!-- /ATOM:irrelevant_long -->
