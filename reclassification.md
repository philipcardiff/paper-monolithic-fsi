# Reclassification of "closest prior work in spirit" summaries

Re-evaluated against the tightened rubric for the quasi-monolithic cell-centred FV / JFNK / block-preconditioned FSI paper.

---

## cardiff2026 — Cardiff 2026

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** Solid-mechanics-only paper (cell-centred FV solid + JFNK + approximate Jacobian preconditioner). Not FSI specifically — the Turek–Hron FSI3 case uses a segregated PIMPLE fluid solver with partitioned interface quasi-Newton coupling, so it does not exercise a monolithic FSI residual. The author's own summary note states "Do not cite this as monolithic FSI prior work". It is methodological background for the FV-JFNK component but does not qualify under any FSI-specific bucket.
**Confidence:** high

---

## cerquaglia2019 — Cerquaglia 2019

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** Fully partitioned PFEM (fluid) + FE (solid) with IQN-ILS interface coupling — neither FV nor monolithic. Does not match FV-but-partitioned (no FV) and does not match FE-precedent (not monolithic). Closest in motivation (added-mass) only.
**Confidence:** high

---

## degroote2009 — Degroote 2009

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** FE/FE monolithic Newton-Raphson with exact Jacobian and direct sparse solver (ADINA). No Krylov solver, no block preconditioner; therefore fails the FE-precedent criterion of "Newton-Krylov or block preconditioning". Used here purely as a partitioned-vs-monolithic comparison benchmark.
**Confidence:** medium

---

## eken2016 — Eken 2016

**Original classification:** closest prior work in spirit
**New classification:** closest prior work in spirit (tight)
**Justification:** Hits all four core traits — vertex-centred (side-centred) FV fluid, FE solid, fully monolithic coupling including mesh DOFs, inexact Newton with FGMRES, and an explicit upper-triangular right block preconditioner that replaces the zero pressure block with a scaled Laplacian, plus RAS/ILU subdomain solves via PETSc. Falls short of "directly competing" only because the FV is staggered/vertex-centred (not cell-centred) and the solid is FE rather than FV.
**Confidence:** high

---

## franci2016 — Franci 2016

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** FE/PFEM unified Lagrangian formulation with a two-step Gauss-Seidel pressure–velocity iteration. Monolithic in structure but the nonlinear solver is fixed-point/Gauss-Seidel, not Newton-type, so it fails the FE-precedent criterion.
**Confidence:** high

---

## giannopapa2008 — Giannopapa 2008

**Original classification:** closest prior work in spirit
**New classification:** Eulerian-one-continuum FV FSI
**Justification:** Cell-centred FV unified one-continuum formulation with PISO velocity–pressure coupling; treats fluid and solid through a single continuum with no body-fitted fluid–solid mesh distinction. The validation here is in fact a transient cantilever beam (solid-only) but the paper sits squarely in the unified one-continuum FV family.
**Confidence:** high

---

## giannopapa2007 — Giannopapa 2007

**Original classification:** closest prior work in spirit
**New classification:** Eulerian-one-continuum FV FSI
**Justification:** Explicitly Eulerian (no mesh motion), cell-centred FV unified continuum approach with PISO coupling; interface is internal to the computational domain with no exchange — the defining feature of the Eulerian-one-continuum bucket.
**Confidence:** high

---

## greenshields1999 — Greenshields 1999

**Original classification:** closest prior work in spirit
**New classification:** FV-but-partitioned
**Justification:** Cell-centred FV for both fluid and solid in FOAM with PISO and a partitioned strong-coupling outer loop (separate fluid and solid solves with under-relaxation). The summary explicitly notes Section 4 shows a partitioned strong-coupling algorithm despite the abstract's "implicit" language.
**Confidence:** high

---

## idelsohn2009 — Idelsohn 2009

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** FE/PFEM ALE-based with pressure segregation via static condensation and fixed-point/projection iteration; an algorithmic precedent for added-mass treatment via approximate pressure/interface operators, but neither FV, Newton-Krylov, nor block-preconditioned.
**Confidence:** high

---

## liu2014 — Liu 2014

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** FE quasi-monolithic combined-field with explicit interface advancement and a single linear solve per step (no Newton iteration). Fails Newton-type criterion and is FE rather than FV; the summary explicitly notes "no Newton-Raphson iteration is used".
**Confidence:** high

---

## lozovskiy2019 — Lozovskiy 2019

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** Monolithic FE method using lagged geometric/advection terms (semi-implicit linearisation) solved with MUMPS direct factorisation. No Newton-Krylov, no block preconditioner — fails FE-precedent rubric. Analysis paper focused on energy stability.
**Confidence:** high

---

## liu2015 — Liu 2015

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** FE monolithic combined-field with explicit interface/mesh advancement and direct linear solves in MATLAB; no Newton iteration and no block preconditioning. Summary explicitly notes iterative preconditioners are future work.
**Confidence:** high

---

## michler2004 — Michler 2004

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** One-dimensional space–time DG fluid coupled to a single-DOF spring-mass piston; conceptual partitioned-vs-monolithic comparison rather than a method paper for higher-dimensional FSI. No Newton-Krylov or block preconditioner discussed.
**Confidence:** high

---

## malan2012 — Malan 2012

**Original classification:** closest prior work in spirit
**New classification:** FV-but-partitioned
**Justification:** Vertex-centred FV for both fluid and solid, but the FSI coupling is explicitly partitioned/block-Jacobi via dual-time interface iterations — the summary quote "the method above represents a block-Jacobi method" makes this unambiguous. LU-SGS-GMRES is internal to each block solve, not a monolithic preconditioner.
**Confidence:** high

---

## lozovskiy2015 — Lozovskiy 2015

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** FE monolithic ALE with extrapolated geometry and linearised inertia — one linear solve per step using a sparse direct factorisation. Not FV, no Newton-Krylov, no block preconditioner; iterative preconditioned solvers explicitly left as future work.
**Confidence:** high

---

## malan2013 — Malan 2013

**Original classification:** closest prior work in spirit
**New classification:** FV-but-partitioned
**Justification:** Vertex-centred FV/FV with strongly coupled partitioned dual-time iteration; summary explicitly identifies the FSI-level method as block-Jacobi. "Fully-coupled" in the title refers to strong coupling within partitioned iteration, not a monolithic Newton solve.
**Confidence:** high

---

## schott2018b — Schott 2018

**Original classification:** closest prior work in spirit
**New classification:** FE precedent for block-preconditioned Newton-Krylov FSI
**Justification:** FE/FE CutFEM hybrid Eulerian–ALE monolithic FSI with full Newton-Raphson and an approximate-Jacobian linearisation; meets the FE-precedent criterion of FE + monolithic + Newton-type with approximate-Jacobian construction, though no explicit block preconditioner is reported. FE counterpart in spirit to the new paper's monolithic FV strategy.
**Confidence:** medium

---

## schott2019 — Schott 2019

**Original classification:** closest prior work in spirit
**New classification:** FE precedent for block-preconditioned Newton-Krylov FSI
**Justification:** Journal version of the 2018 preprint: FE/FE CutFEM monolithic FSI with Newton-Raphson, approximate Jacobian, Nitsche coupling, and mesh DOFs inside the Newton vector. FE precedent for the new paper, though it remains FE rather than FV and does not describe a block preconditioner.
**Confidence:** medium

---

## mayr2015 — Mayr 2016

**Original classification:** (newly added — was missing a summary)
**New classification:** FE precedent for block-preconditioned Newton-Krylov FSI
**Justification:** FE/FE monolithic FSI with full Newton linearisation of a block Jacobian (structure, fluid, ALE sub-blocks plus mortar projection P), solved by GMRES with per-field ILU(0) preconditioning ("an ILU(0) preconditioner for each field … solved using a GMRES procedure", p. B52). Mesh DOFs are inside the Newton vector. A clean FE counterpart to the new paper's block-preconditioned monolithic JFNK strategy.
**Confidence:** high

---

## ryzhakov2010 — Ryzhakov 2010

**Original classification:** closest prior work in spirit
**New classification:** FE precedent for block-preconditioned Newton-Krylov FSI
**Justification:** PFEM/FE monolithic Lagrangian FSI solved by Newton iteration with a matrix-free, diagonally preconditioned CG inner solver after a global pressure condensation. The matrix-free Krylov inner solver puts this firmly in the FE-precedent bucket as an early FE analogue of a Newton-Krylov FSI approach.
**Confidence:** medium

---

## vonscheven2010 — von Scheven 2010

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** Partitioned FE/FE FSI with an interface-level Newton-Krylov scheme (matrix-free Jacobian-vector products at the interface) compared against block Gauss-Seidel/Aitken. Because coupling is partitioned, not monolithic, it does not satisfy the FE-precedent rubric (which requires monolithic/quasi-monolithic).
**Confidence:** medium

---

## walhorn2005 — Walhorn 2005

**Original classification:** closest prior work in spirit
**New classification:** background
**Justification:** Monolithic space–time FE method assembled as a single block system but solved by Picard iteration (3–4 iters/slab). Picard is explicitly excluded from the Newton-type criterion, and no block preconditioner is described; the explicit block matrix structure alone is not block preconditioning.
**Confidence:** high

---

## Summary

| Bucket | Count |
|---|---|
| directly competing prior work | 0 |
| closest prior work in spirit (tight) | 1 |
| FE precedent | 4 |
| FV-but-partitioned | 3 |
| FV-but-unified-SIMPLE | 0 |
| Eulerian-one-continuum | 2 |
| added-mass / FSI stability theory | 0 |
| background | 12 |
| not relevant | 0 |
