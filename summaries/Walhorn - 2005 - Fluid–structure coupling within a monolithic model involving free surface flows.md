---

## Walhorn 2005 — Monolithic FSI with free surface flows via space-time FE

**Full citation:** Walhorn, E., Kölke, A., Hübner, B., Dinkler, D. Fluid–structure coupling within a monolithic model involving free surface flows. Computers and Structures, 83(2100–2111), 2005. DOI: 10.1016/j.compstruc.2005.03.010

**BibTeX key suggestion:** walhorn2005

**Discretisation (fluid):** FE (stabilised space–time, Galerkin/least-squares)

**Discretisation (solid):** FE (stabilised space–time, mixed-hybrid)

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector (space–time ALE mesh adapts within each time slab; mesh velocity incorporated via geometrically non-linear space–time formulation satisfying the GCL automatically)

**Nonlinear solver:** Picard

**Preconditioner / linearisation:** N/A (Picard iteration on the monolithic block system; no preconditioner discussion)

**Test cases:**
- Breaking dam (free surface, moving mesh, comparison with Martin & Moyce and Hansbo experiments)
- Breaking dam captured with level set method (fixed mesh, comparison with moving-mesh result)
- Hydrostatic pressure in a one-dimensional two-fluid channel (manufactured solution, convergence study)
- Rising bubble with surface tension (two-fluid, level set, topology change)
- Breaking dam impacting a rigid obstacle, then an elastic wall (FSI with free surface, comparison with VOF/FV results)

**Code released?** Not stated

**One-paragraph summary (under 120 words):** This paper presents a fully monolithic space–time finite element method for FSI problems involving free surfaces and two-fluid flows. Both fluid (incompressible Navier–Stokes, GLS-stabilised) and solid (geometrically non-linear elastic, mixed-hybrid) domains are discretised with time-discontinuous Galerkin space–time slabs; the coupled system assembled in a single block matrix (Fig. 6) is solved by Picard iteration, converging in 3–4 steps per time slab. Free surfaces and immiscible fluid interfaces are tracked via a level set method with modified (extended) ansatz functions to represent strong/weak discontinuities at cut elements. The method naturally satisfies the GCL and achieves second-order temporal accuracy. Relevance to the target paper: an early FE-based monolithic FSI formulation with explicit block structure, though the nonlinear solver is Picard rather than Newton-Krylov.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "The article presents a monolithic approach to solve fluid–structure interaction problems with free surface flows and strong coupling in a single system of equations." (p. 2101); "The monolithic formulation of fluid, structure, and coupling conditions in a single equation system, shown in Fig. 6 without pressure, allows the analysis of the coupled system. This applies because the equation system describes the behavior of the fully coupled system in the current space–time slab. The highly non-linear system is solved by a Picard iteration scheme." (p. 2103)

**Notes for the authors:** The nonlinear solver is Picard (3–4 iterations claimed sufficient), not Newton or JFNK, so there is no Jacobian or preconditioner discussion. The block structure in Fig. 6 (K_F, B, B^T, K_S sub-blocks with interface traction unknowns t) is directly comparable to the block system targeted by the approximate block preconditioner in the present paper. The paper also covers two-fluid/free-surface physics via level set with extended FE basis functions — a feature not present in the target paper but worth acknowledging if free-surface extensions are discussed.

---
