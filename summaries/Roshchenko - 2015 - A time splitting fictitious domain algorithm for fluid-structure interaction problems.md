---

## Roshchenko 2015 — Time-splitting fictitious domain FEM for FSI

**Full citation:** Roshchenko, A., Minev, P. D., Finlay, W. H. A time splitting fictitious domain algorithm for fluid-structure interaction problems. Journal of Fluids and Structures, 58:109–126, 2015. DOI: 10.1016/j.jfluidstructs.2015.07.006

**BibTeX key suggestion:** roshchenko2015

**Discretisation (fluid):** FE (P2–P1 Taylor–Hood on fixed Eulerian grid)

**Discretisation (solid):** FE (P2 isoparametric on Lagrangian mesh; deformation gradient via P2 elements)

**Coupling structure:** immersed / fictitious domain (mixed Eulerian–Lagrangian; solid submerged in extended fluid domain)

**Mesh motion treatment:** Eulerian no mesh motion (fluid on fixed Eulerian grid; solid tracked on separate Lagrangian grid advected by flow)

**Nonlinear solver:** fixed-point / semi-implicit (one iteration of the implicit scheme per time step; operator-splitting with method of characteristics for advection)

**Preconditioner / linearisation:** N/A (operator splitting yields constant, symmetric positive definite matrices assembled once; rotational incremental pressure-correction scheme; no Newton or block-preconditioned Krylov solve)

**Test cases:**
- Deformation of an elastic wall driven by a time-dependent periodic flow (2-D, compared with Zhao et al. 2008)
- Solid disc motion in a lid-driven cavity (2-D, compared with Zhao et al. 2008 and Sugiyama et al. 2011)
- Elastic wall deformation in a lid-driven cavity (2-D, compared with Richter and Wick 2010 ALE/fully Eulerian reference)
- 3-D rhythmically expanding pulmonary alveolus attached to a rigid cylindrical duct (two acinar generations z'=6 and z'=8)

**Code released?** Not stated

**One-paragraph summary (under 120 words):** This paper develops a mixed Eulerian–Lagrangian finite element fictitious domain method for incompressible fluid interacting with a hyperelastic incompressible solid. A single velocity field is defined over the entire domain; the fluid equations are solved on a fixed Eulerian FE grid, while solid deformation is tracked on an overlapping Lagrangian mesh. Elastic stresses are smoothed onto the Lagrangian mesh via Zienkiewicz–Zhu patch recovery and transferred to the Eulerian grid as a distributed body force. An operator-splitting time-stepping scheme decouples velocity from pressure and yields constant, symmetric positive definite matrices, avoiding Newton–Raphson or Uzawa iterations. The method is validated in 2-D and applied to 3-D alveolar respiratory flow.

**Relevance classification:** background

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** The key distinguishing feature relative to the target paper is that this method avoids all nonlinear (Newton/JFNK) solves by using a semi-implicit operator-splitting strategy that produces constant SPD matrices — explicitly trading spatial accuracy near the interface and time-step restrictions for solver simplicity. The paper explicitly notes this tradeoff (p. 111): "The relative ease of solving the present matrix problems come at a cost of possible time step restrictions due to the specific time-splitting algorithms mentioned above and sub-optimal spatial convergence rates in the vicinity of the fluid–structure interface inherent to the immersed methods." Uses FE not FV; immersed/fictitious domain not ALE; no block preconditioning.

---
