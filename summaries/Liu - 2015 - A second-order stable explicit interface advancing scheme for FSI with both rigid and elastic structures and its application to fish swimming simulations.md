---

## Liu 2015 — Second-order explicit interface FSI scheme

**Full citation:** Liu, J. A second-order stable explicit interface advancing scheme for FSI with both rigid and elastic structures and its application to fish swimming simulations. Computers & Fluids, N/A(N/A):N/A, 2015. DOI: 10.1016/j.compfluid.2015.06.002

**BibTeX key suggestion:** liu2015

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** outside Newton vector

**Nonlinear solver:** explicit

**Preconditioner / linearisation:** N/A

**Test cases:** 
- analytic manufactured FSI solution for temporal and spatial convergence
- soft-coated rigid cylinder floating in a fluid tank
- Turek-Hron FSI3 benchmark
- planar articulated fish swimming simulations

**Code released?** MATLAB/iFEM-derived code not stated as released; manufactured-solution script at http://www.math.nus.edu.sg/~matlj/manusolu2.m; fish swimming movie at www.math.nus.edu.sg/~matlj/fishswim.avi

**One-paragraph summary (under 120 words):** This paper presents a second-order ALE finite-element FSI scheme for rigid and elastic structures using a combined-field formulation. Fluid velocity, pressure, and structure velocity are solved in a coupled linear system each time step, while interface and mesh positions are advanced explicitly by extrapolation, removing mesh position from the coupled unknowns. The paper proves an energy stability inequality for the explicit interface treatment, verifies second-order temporal and high-order spatial convergence with manufactured and reference solutions, computes the Turek-Hron FSI3 benchmark, and applies the method to articulated fish swimming. It uses direct linear solves in MATLAB rather than Newton-Krylov, PETSc, or finite volume discretisation.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "we take the monolithic approach" (p.6); "removed the mesh position from the list of unknown variables" (p.6).

**Notes for the authors:** Close in spirit because it is a monolithic ALE FSI method with explicit interface/mesh advancement outside the coupled solve, but it is FE-based, uses semi-implicit linearisation and direct MATLAB solves, and explicitly states that iterative preconditioners are planned future work rather than used here.

---
