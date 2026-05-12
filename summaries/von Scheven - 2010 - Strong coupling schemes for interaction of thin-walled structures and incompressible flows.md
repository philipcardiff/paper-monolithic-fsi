---

## von Scheven 2010 — Strong coupling for thin-walled FSI

**Full citation:** von Scheven, M., Ramm, E. Strong coupling schemes for interaction of thin-walled structures and incompressible flows. International Journal for Numerical Methods in Engineering, 87:214-231, 2011. DOI: 10.1002/nme.3033

**BibTeX key suggestion:** vonscheven2010

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** Newton-Krylov / fixed-point

**Preconditioner / linearisation:** approximate Jacobian

**Test cases:** - 2D membrane roof model problem; - 3D membrane roof in aerodynamic flow; - 3D foil in wind

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper compares strong partitioned coupling schemes for FSI between incompressible ALE flow and thin-walled structures. Both fields use finite elements; the fluid uses SUPG/PSPG stabilization and the structure uses nonlinear shell finite elements. The coupled interface problem is solved by block Gauss-Seidel with Aitken relaxation, by a coarse-grid predictor followed by fine-grid iteration, and by an interface Newton-Krylov method with GMRES and finite-difference Jacobian-vector products. The coarse-grid predictor reduces wall time for the membrane model, while Newton-Krylov sharply reduces coupling iterations but is not fastest because each iteration is expensive.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "Different partitioned strong coupling approaches are presented and compared" (p.1); "a Newton-Krylov approach" (p.1); "Jacobian is not required explicitly" (p.10).

**Notes for the authors:** Closest in spirit for Newton-Krylov FSI coupling, but it is partitioned interface coupling with FE/FE discretisation, not quasi-monolithic cell-centred FV; no block preconditioner is described.

---
