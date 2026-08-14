# fastify clean_schema_id carrier-ablation atoms (Phase 3.1)

Length-matched short/long pairs for the 5-condition carrier ablation. short pair and long pair
each token-matched within 5%; same sentence structure, paragraph count, technical density; only
semantic content differs. Read when CGCL_ATOMS_FILE=atoms_ablation.md; original atoms.md untouched.

provenance: commit c9141a071d0f (shared-schema snapshot-copy convention).

<!-- ATOM:reset -->
<!-- /ATOM:reset -->

<!-- ATOM:correct_short -->
Project context (from prior work on this codebase, provenance: commit c9141a071d0f): a shared schema registered on an instance lives in an internal store and is read back as a snapshot copy, so a caller that transforms it for another purpose must work on the returned snapshot, not the stored original, which stays intact.
<!-- /ATOM:correct_short -->

<!-- ATOM:irrelevant_short -->
Project context (from prior work on this codebase, provenance: commit c9141a071d0f): a hook registered on an instance lives in an internal list and is read back in definition order, so a caller that chains it for another purpose must work on the ordered list, not the stored original, which stays intact.
<!-- /ATOM:irrelevant_short -->

<!-- ATOM:correct_long -->
Project context (from prior work on this codebase, provenance: commit c9141a071d0f): a shared schema registered on an instance lives in an internal store and is read back as a snapshot copy, so a caller that transforms it for another purpose must work on the returned snapshot, not the stored original, which stays intact. The snapshot discipline is recognized when the accessor returns a fresh copy of the stored map; the caller then mutates that copy instead of the internal object, so the instance and a previously-returned snapshot stay decoupled. This was established for the schema store and is meant to carry over: any sibling code path that pulls a stored schema out for reuse or transformation should honor the identical snapshot discipline, so that a schema read once stays intact no matter how many later reads reuse it. Applying the snapshot discipline uniformly is the intended invariant; a code path that mutates the stored original directly breaks that invariant and leaves the schema un-retrievable in its original form.
<!-- /ATOM:correct_long -->

<!-- ATOM:irrelevant_long -->
Project context (from prior work on this codebase, provenance: commit c9141a071d0f): a hook registered on an instance lives in an internal list and is read back in definition order, so a caller that chains it for another purpose must work on the ordered list, not the stored original, which stays intact. The ordering discipline is recognized when the accessor returns the list in its stored order; the caller then appends to that list instead of reordering the internal object, so the instance and a previously-returned list stay decoupled. This was established for the hook store and is meant to carry over: any sibling code path that pulls a stored hook out for reuse or transformation should honor the identical ordering discipline, so that a hook read once stays intact no matter how many later reads reuse it. Applying the ordering discipline uniformly is the intended invariant; a code path that mutates the stored original directly breaks that invariant and leaves the hook un-retrievable in its original form.
<!-- /ATOM:irrelevant_long -->
