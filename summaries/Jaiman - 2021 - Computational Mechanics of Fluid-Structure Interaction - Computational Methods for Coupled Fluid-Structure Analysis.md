---

## Jaiman 2022 — Computational mechanics of FSI: coupled fluid-structure methods

**Full citation:** Jaiman, R. K., Joshi, V. Computational Mechanics of Fluid-Structure Interaction: Computational Methods for Coupled Fluid-Structure Analysis. Springer Nature Singapore, 2022. ISBN: 978-981-16-5354-4 (print), 978-981-16-5355-1 (eBook). DOI: https://doi.org/10.1007/978-981-16-5355-1

**BibTeX key suggestion:** jaiman2022

**Discretisation (fluid):** FE (stabilised Petrov-Galerkin / variational multiscale, P2/P1 or P2 elements on unstructured triangular/tetrahedral meshes in ALE frame)

**Discretisation (solid):** FE (Lagrangian; linear elastic and St. Venant-Kirchhoff nonlinear; P2 elements)

**Coupling structure:** quasi-monolithic (Chapter 6 primary formulation); monolithic and partitioned also described

**Mesh motion treatment:** outside Newton vector — ALE mesh equation is decoupled from the coupled fluid-structure system and solved explicitly at the start of each time step via explicit extrapolation of structural position; mesh displacement then used to update the fluid domain before the single quasi-monolithic solve

**Nonlinear solver:** Newton (Newton-Raphson linearisation used for the monolithic/partitioned treatments in Ch. 5); the quasi-monolithic scheme (Ch. 6) avoids nonlinear iterations entirely by explicit treatment of the convective velocity and interface position, giving a single linear solve per time step

**Preconditioner / linearisation:** approximate Jacobian (linearisation via explicit extrapolation of ALE convective velocity and structural deformation in the quasi-monolithic scheme; Newton-Raphson linearisation in the fully monolithic treatment); no block preconditioner described

**Test cases:**
- 2D and 3D FSI benchmarks (Turek-Hron flag, cylinder with flexible tail)
- Flapping dynamics of a flexible foil / inverted elastic flag
- Vortex-induced vibration of offshore risers and flexible cylinders
- Two-phase FSI: wave-structure interaction, flexible riser with internal two-phase flow
- Flexible multibody FSI: bat-wing inspired flapping, floater-mooring-riser system

**Code released?** Not stated (research codes at UBC Computational Multiphysics Lab and NUS FSIG; no public repository identified)

**One-paragraph summary (under 120 words):** This graduate-level textbook presents a comprehensive variational finite element framework for FSI, covering continuum mechanics foundations, ALE formulation, stabilised FE methods, and both partitioned and monolithic coupling strategies. Chapter 6, the methodological centrepiece, develops a quasi-monolithic ALE-FE scheme that assembles fluid and structural equations into a single block system but decouples the ALE mesh update and the interface position via second-order explicit extrapolation, eliminating the need for nonlinear iterations per time step. The book also covers two-phase FSI (Allen-Cahn phase field), flexible multibody dynamics, turbulence modelling (LES/DDES), and non-matching interface methods. Discretisation throughout is finite element; no cell-centred finite volume or JFNK solvers are discussed.

**Relevance classification:** textbook

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** The quasi-monolithic strategy in Ch. 6 is closely related in spirit to the approach being developed (explicit interface/ALE treatment to avoid nonlinear iterations, single block-system solve per time step), but is entirely FE-based whereas the present work uses cell-centred FV. The book explicitly contrasts its approach with "finite-volume discretization for the fluid equations in combination with a finite-element discretization for the structural equations" (p. 124, §6.2.2), noting that it applies FE throughout — a useful negative citation. No JFNK or block preconditioners are described.

---
