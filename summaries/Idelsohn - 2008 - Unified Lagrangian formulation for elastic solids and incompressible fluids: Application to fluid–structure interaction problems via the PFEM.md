---

## Idelsohn 2008 — Unified Lagrangian PFEM formulation for FSI problems

**Full citation:** Idelsohn, S.R., Marti, J., Limache, A., Oñate, E. Unified Lagrangian formulation for elastic solids and incompressible fluids: Application to fluid–structure interaction problems via the PFEM. Computer Methods in Applied Mechanics and Engineering, 197(19–20):1762–1776, 2008. DOI: 10.1016/j.cma.2007.06.004

**BibTeX key suggestion:** idelsohn2008

**Discretisation (fluid):** particle / FE (PFEM — meshless finite element method with extended Delaunay tessellation)

**Discretisation (solid):** unified single continuum (same PFEM particle/FE framework; solid mesh regenerated only once and nodes moved without re-meshing)

**Coupling structure:** unified one-continuum

**Mesh motion treatment:** Lagrangian — all nodes (fluid and solid) are material points that move with the continuum; mesh is regenerated at each time step via extended Delaunay tessellation

**Nonlinear solver:** fixed-point (fractional-step / implicit time integration solved iteratively within each time step; no explicit Newton or Krylov method described)

**Preconditioner / linearisation:** N/A (system assembled and solved in matrix form per time step; Finite Calculus (FIC) stabilisation used for pressure; no block preconditioner described)

**Test cases:**
- Cantilever beam under suddenly applied end shear stress (pure structural validation, comparison with analytical solution)
- Collapse of a water column with a rigid obstacle (comparison with Koshizuka experiments)
- Collapse of a water column with a flexible elastic obstacle (comparison with Walhorn et al. [19])
- High elastic bar struck by a lateral wave (large deformation FSI)
- Elastic cube falling/floating in a water container; dragging of an elastic plate with free-surface waves

**Code released?** Not stated (research code at CIMNE, Barcelona; http://www.cimne.com referenced but no public repository given)

**One-paragraph summary (under 120 words):** This paper presents a unified Lagrangian finite element framework in which both incompressible (or quasi-incompressible) Newtonian fluids and hypo-elastic solids are described by a single constitutive equation, differing only in material parameters. The entire fluid–solid domain is treated as one continuum and discretised with the Particle Finite Element Method (PFEM), which rebuilds the mesh at every time step using an extended Delaunay tessellation and identifies free surfaces via Alpha Shape. A fractional-step implicit time integration is used. The approach eliminates explicit fluid–solid interface coupling conditions and handles large free-surface deformations, wave breaking, and floating/submerged bodies naturally. It is not relevant to cell-centred FV, JFNK, or block-preconditioned Newton-Krylov FSI.

**Relevance classification:** background

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** The method is fully Lagrangian (PFEM) rather than Eulerian, and is entirely FE/particle-based with no FV, no Newton-Krylov, and no block preconditioner. It is methodologically distant from the target paper. Could be cited briefly as a contrasting unified-continuum approach that avoids explicit fluid–solid interface coupling entirely.

---
