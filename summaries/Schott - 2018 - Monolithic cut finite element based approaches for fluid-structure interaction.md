---

## Schott 2018 — Monolithic cut FEM FSI approaches

**Full citation:** Schott, B., Ager, C., Wall, W. A. Monolithic cut finite element based approaches for fluid-structure interaction. International Journal for Numerical Methods in Engineering, 00:1-43, 2018. DOI: 10.1002/nme.6072

**BibTeX key suggestion:** schott2018

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** Eulerian no mesh motion for fixed-grid CutFEM approaches; outside Newton vector for ALE/moving fluid mesh parts

**Nonlinear solver:** Newton

**Preconditioner / linearisation:** approximate Jacobian / block preconditioner / multigrid

**Test cases:** 
- Pulsating flow over a bending flexible 3D flap
- Flow-excited impermeable fluid container in a flexible housing
- Vibration of a flexible structure / flag in vortex-shedding flow

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper develops monolithic finite element FSI formulations based on CutFEM, Nitsche coupling, and ghost-penalty stabilization. The solid is treated in a Lagrangian finite element setting, while the fluid is handled using fitted ALE, fixed-grid unfitted CutFEM, hybrid ALE/CutFEM, and fluid-domain-decomposition variants. Fully discrete nonlinear systems are solved with Newton-Raphson-like iterations; the linearized coupled systems are solved using preconditioned GMRES with generic block Gauss-Seidel decoupling and subproblem preconditioners. The work targets large structural motion, nonmatching fluid-solid interfaces, and moving cut domains, with numerical demonstrations on 2D and 3D flexible-structure benchmarks.

**Relevance classification:** FE precedent for block-preconditioned Newton-Krylov FSI

**Direct quote(s) supporting the classification:** "A monolithic solution procedure for the non-linear coupled fluid-structure system is proposed" (p.26); "a preconditioned GMRES solver is utilized" (p.31); "generic block Gauss-Seidel iterations are used for decoupling the subproblems" (p.31).

**Notes for the authors:** Strongly relevant as monolithic FE/CutFEM FSI with Newton-like nonlinear solves and block-preconditioned GMRES, but not cell-centred FV, not OpenFOAM/solids4foam/PETSc, and not Jacobian-free; the paper appears to assemble linearized matrices and treats some geometry/interface-normal terms in a fixed-point fashion.

---
