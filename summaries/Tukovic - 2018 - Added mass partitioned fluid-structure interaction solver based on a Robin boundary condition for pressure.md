---

## Tukovic 2019 — Added-mass partitioned FSI solver with Robin pressure BC

**Full citation:** Tuković, Ž., Bukač, M., Cardiff, P., Jasak, H., Ivanković, A. Added Mass Partitioned Fluid–Structure Interaction Solver Based on a Robin Boundary Condition for Pressure. In: Nóbrega, J., Jasak, H. (eds) OpenFOAM®. Springer, Cham, 2019. DOI: 10.1007/978-3-319-60846-4_1

**BibTeX key suggestion:** tukovic2019

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** Picard

**Preconditioner / linearisation:** N/A

**Test cases:** 
- Wave propagation in a flexible elastic tube (hemodynamics benchmark, low solid-to-fluid density ratio)
- Temporal accuracy study (four time-step sizes, first-order accuracy confirmed)
- Loose vs. strong coupling stability comparison on the elastic tube
- Enclosed fluid domain: balloon-type inflation problem with geometrically nonlinear solid deformation

**Code released?** not stated

**One-paragraph summary (under 120 words):** This paper presents a partitioned FSI solver in which both the incompressible ALE fluid (PISO) and the Saint Venant-Kirchhoff hyperelastic solid are discretised with second-order cell-centred FV on polyhedral meshes, with first-order implicit Euler time integration. The key contribution is a Robin boundary condition for pressure at the fluid-structure interface, derived by combining the standard Neumann pressure BC with an approximation of the solid inertia. This Robin BC is embedded in a Robin-Neumann partitioned scheme that inherits the added-mass stability of the kinematically coupled beta-scheme without full operator splitting. The scheme handles both strongly and loosely coupled variants without under-relaxation and addresses enclosed-domain FSI problems with pure Dirichlet velocity boundaries.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** This is the direct predecessor/companion paper to the other Tukovic 2018 work in this review (tukovic2018). Both use cell-centred FV for fluid and solid; this paper's Robin pressure BC and Robin-Neumann partitioned scheme are the closest published FV-partitioned approach to the target paper's cell-centred FV framework. The paper does not display a journal name, volume, issue, page numbers, or DOI anywhere in the PDF — publication metadata should be verified externally (likely published in a Springer journal such as the OpenFOAM proceedings or a computational mechanics journal). Future work stated explicitly: second-order temporal accuracy and full kinematically coupled beta-scheme implementation in cell-centred FV.

---
