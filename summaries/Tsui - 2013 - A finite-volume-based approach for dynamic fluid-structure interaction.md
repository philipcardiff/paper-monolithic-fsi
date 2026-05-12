---

## Tsui 2013 — FV approach for dynamic FSI

**Full citation:** Tsui, Y.-Y., Huang, Y.-C., Huang, C.-L., and Lin, S.-W. A Finite-Volume-Based Approach for Dynamic Fluid-Structure Interaction. Numerical Heat Transfer, Part B: Fundamentals: An International Journal of Computation and Methodology, 64(4):326-349, 2013. DOI: 10.1080/10407790.2013.806691

**BibTeX key suggestion:** tsui2013

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** vertex-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** PISO

**Preconditioner / linearisation:** pressure-correction splitting / momentum interpolation

**Test cases:** 
- cantilever beam under end load and distributed loads
- vertical elastic plate in channel flow
- square cylinder with a flexible plate attached downstream

**Code released?** not stated

**One-paragraph summary (under 120 words):** Tsui et al. present a finite-volume framework for dynamic FSI that uses cell-centred finite volumes for incompressible fluid flow and vertex-centred finite volumes on a median-dual mesh for solid dynamics. The solid equations are integrated implicitly with dual-time stepping, while the fluid is solved on a moving mesh using a pressure-based noniterative predictor-corrector algorithm. Fluid and structure are coupled sequentially: fluid tractions drive the structural solve, the deformed structure updates the fluid boundary and mesh, and the fluid solve then updates interface tractions for the next time step. The method is validated on cantilever deformation/vibration and applied to flexible-plate channel and vortex-induced-motion cases.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** "a partitioned approach based on the finite-volume method" (p.2); "tackled in a sequence manner" (p.13).

**Notes for the authors:** This is a finite-volume FSI predecessor with moving meshes and a single in-house FV framework, but it is explicitly sequential/partitioned rather than monolithic or JFNK/block-preconditioned.

---
