# FSI Paper Triage

_Generated 2026-05-12. Total summaries: 48 (48 files found; prompt specified 51 — 3 appear to be absent from the summaries/ directory)._

## 1. Papers by Relevance Classification

### closest prior work in spirit

- **Greenshields1999b** — Greenshields 1999, _The finite volume method for coupled fluid flow and stress analysis_
  The paper presents a cell-centred finite volume method for coupled transient fluid flow and linear elastic stress analysis, implemented in FOAM.
- **michler2004** — Michler 2004, _A monolithic approach to fluid–structure interaction_
  The paper compares partitioned and monolithic solution procedures for a one-dimensional compressible-fluid piston FSI model.
- **walhorn2005** — Walhorn 2005, _Fluid–structure coupling within a monolithic model involving free surf_
  This paper presents a fully monolithic space–time finite element method for FSI problems involving free surfaces and two-fluid flows.
- **Giannopapa2007** — Giannopapa 2007, _Indicative results and progress on the development of the unified sing_
  This paper presents preliminary FSI results for a unified single-solution method in which fluid and solid are represented on one finite-volume grid and distinguished by...
- **Giannopapa2008** — Giannopapa 2008, _Linear stability analysis and validation of a new solution method of t_
  The paper reformulates linear elastodynamics in velocity-pressure variables so Hookean solids can be solved with the same finite-volume pressure-velocity machinery used for fluids.
- **Degroote2009** — Degroote 2009, _Performance of a new partitioned procedure versus a monolithic procedu_
  The paper presents IQN-ILS, a partitioned interface quasi-Newton method that treats the flow and structural solvers as black boxes and approximates the inverse interface Jacobian...
- **idelsohn2009** — Idelsohn 2009, _Fluid-structure interaction problems with strong added-mass effect_
  The paper studies added-mass convergence problems in FSI by starting from a monolithic finite element system and segregating pressure through static condensation of velocity.
- **ryzhakov2010** — Ryzhakov 2010, _A monolithic Lagrangian approach for fluid–structure interaction probl_
  The paper develops a monolithic Lagrangian PFEM/finite-element FSI method for flexible structures interacting with free-surface flows.
- **vonscheven2010** — von Scheven 2010, _Strong coupling schemes for interaction of thin-walled structures and _
  The paper compares strong partitioned coupling schemes for FSI between incompressible ALE flow and thin-walled structures.
- **malan2012** — Malan 2012, _An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-_
  The paper presents a parallel 3D strongly coupled partitioned FSI solver using vertex-centred edge-based finite volumes for both incompressible fluid and nonlinear elastic solid domains.
- **malan2013** — Malan 2013, _An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-_
  This paper develops a parallel, matrix-free, strongly coupled partitioned FSI solver using vertex-centred edge-based finite volumes for both incompressible ALE fluid flow and geometrically nonlinear elastic solids.
- **Liu2014** — Liu 2014, _A stable second-order scheme for fluid–structure interaction with stro_
  The paper presents a second-order combined-field with explicit-interface-advancing (CFEI) scheme for ALE fluid-structure interaction.
- **liu2015** — Liu 2015, _A second-order stable explicit interface advancing scheme for FSI with_
  This paper presents a second-order ALE finite-element FSI scheme for rigid and elastic structures using a combined-field formulation.
- **lozovskiy2015** — Lozovskiy 2015, _An unconditionally stable semi-implicit FSI finite element method_
  The paper develops a monolithic ALE finite element method for incompressible Newtonian fluid coupled to hyperelastic solids.
- **eken2016** — Eken 2016, _A parallel monolithic algorithm for the numerical simulation of large-_
  Eken and Sahin present a fully monolithic ALE-based FSI algorithm combining a side-centred unstructured finite volume discretisation for incompressible Navier–Stokes (velocity at face midpoints, pressure...
- **franci2016** — Franci 2016, _Unified Lagrangian formulation for solid and fluid mechanics and FSI p_
  Franci et al.
- **schott2018b** — Schott 2018, _A monolithic approach to fluid-structure interaction based on a hybrid_
  The paper proposes a monolithic FSI method using a hybrid fluid domain: a moving ALE boundary-layer patch fitted to the structure is embedded in a...
- **cerquaglia2019** — Cerquaglia 2019, _A fully partitioned Lagrangian framework for FSI problems characterize_
  The paper couples an in-house PFEM incompressible free-surface fluid solver with the nonlinear FE solid solver Metafor through CUPyDO.
- **lozovskiy2019** — Lozovskiy 2019, _Analysis and assessment of a monolithic FSI finite element method_
  The paper analyses a monolithic finite element method for incompressible Navier–Stokes flow coupled to a Saint Venant–Kirchhoff hyperelastic solid.
- **Schott2019** — Schott 2019, _A monolithic approach to fluid-structure interaction based on a hybrid_
  The paper proposes a monolithic FSI method in which the fluid is split into a fixed Eulerian background domain and a moving ALE fluid patch...
- **Cardiff2026** — Cardiff 2026, _A Jacobian-Free Newton-Krylov Method for Cell-Centred Finite Volume So_
  The paper introduces a Jacobian-free Newton-Krylov solver for Lagrangian cell-centred finite volume solid mechanics in solids4foam/OpenFOAM using PETSc.

### FE precedent for block-preconditioned Newton-Krylov FSI

- **Heil2004** — Heil 2004, _An efficient solver for the fully coupled solution of large-displaceme_
  The paper develops a fully coupled finite-element solver for large-displacement incompressible FSI in a moving ALE domain.
- **hubner2004** — Hubner 2004, _A monolithic approach to fluid–structure interaction using space–time _
  This paper presents a fully monolithic FSI method in which incompressible Navier–Stokes equations and geometrically nonlinear elastodynamics are discretised with a unified stabilised space-time finite...
- **Heil2008** — Heil 2008, _Solvers for large-displacement fluid-structure interaction problems - _
  This paper compares segregated Picard and monolithic Newton solvers for large-displacement FSI in the finite-element library oomph-lib.
- **gee2010** — Gee 2010, _Truly monolithic algebraic multigrid for fluid-structure interaction_
  Gee et al.
- **richter2015** — Richter 2015, _A monolithic geometric multigrid solver for fluid-structure interactio_
  Richter presents a fully monolithic ALE finite-element formulation for incompressible fluid interaction with nonlinear hyperelastic solids.
- **schott2018** — Schott 2018, _Monolithic cut finite element based approaches for fluid-structure int_
  The paper develops monolithic finite element FSI formulations based on CutFEM, Nitsche coupling, and ghost-penalty stabilization.

### FV-but-partitioned

- **kassiotis2010** — Kassiotis 2010, _Nonlinear fluid-structure interaction problem. Part II: space discreti_
  This paper describes a CTL component-coupling implementation for nonlinear FSI that reuses FEAP for geometrically nonlinear Lagrangian finite-element solids and OpenFOAM for ALE finite-volume fluid...
- **oxtoby2012** — Oxtoby 2012, _A matrix-free, implicit, incompressible fractional-step algorithm for _
  This paper develops a fast, fully-coupled, partitioned FSI solver within the *Elemental* multiphysics code, using a vertex-centred edge-based FV discretisation for both fluid and solid...
- **Tsui2013** — Tsui 2013, _A finite-volume-based approach for dynamic fluid-structure interaction_
  Tsui et al.
- **suliman2015** — Suliman 2015, _A matrix free, partitioned solution of fluid-structure interaction pro_
  This paper develops a matrix-free, strongly coupled partitioned FSI solver using an ALE incompressible fluid formulation discretised with an edge-based hybrid-unstructured vertex-centred finite volume method.
- **gillebaart2016** — Gillebaart 2016, _Time consistent fluid structure interaction on collocated grids for in_
  The paper develops time-consistent finite-volume FSI on collocated grids for incompressible flow using an ALE PISO formulation.
- **Selim2017** — Selim 2017, _Finite Volume Based Fluid-Structure Interaction Solver_
  The paper develops a loosely coupled FSI framework using an in-house HYB3D cell-centred finite-volume Euler/Navier-Stokes solver, a new finite-volume linear-elastic structural solver, and RBF mesh deformation.
- **Tukovic2019** — Tukovic 2018, _Added mass partitioned fluid-structure interaction solver based on a R_
  This paper presents a partitioned FSI solver in which both the incompressible ALE fluid (PISO) and the Saint Venant-Kirchhoff hyperelastic solid are discretised with second-order...
- **Tukovic2018** — Tukovic 2018, _OpenFOAM FINITE VOLUME SOLVER FOR FLUID-SOLID INTERACTION_
  This paper presents a parallel OpenFOAM FSI solver using second-order cell-centred finite volume discretisations for both incompressible ALE flow and total-Lagrangian St.
- **Cardiff2025** — Cardiff 2025, _solids4foam A toolbox for performing solid mechanics and fluid-solid i_
  This JOSS software paper describes solids4foam v2.1, an OpenFOAM toolbox for solid mechanics, fluid-solid interaction, and thermo-fluid-solid interaction.

### FV-but-unified-SIMPLE

- **Papadakis2008** — Papadakis 2008, _A novel pressure–velocity formulation and solution method for fluid–st_
  Papadakis reformulates linear Hookean solid dynamics in velocity-pressure variables so fluid and solid subdomains can use collocated finite-volume discretisation and SIMPLE pressure-velocity coupling.
- **yeo2017** — Yeo 2017, _A Unified Momentum Equation Approach for Computing Flow-Induced Stress_
  The paper derives a velocity-based unified momentum equation by hybridising incompressible Newtonian fluid momentum and linear elastic solid momentum for stationary fluid-structure boundaries.

### Eulerian-one-continuum FV FSI

- **Greenshields2005** — Greenshields 2005, _A unified formulation for continuum mechanics applied to fluid–structu_
  The paper derives a single velocity-pressure continuum formulation for Newtonian fluids and small-strain Hookean solids, using accumulated deviatoric stress to express the solid momentum equation...

### FV solid mechanics foundational

- **cardiff2021** — Cardiff 2021, _Thirty Years of the Finite Volume Method for Solid Mechanics_
  This review surveys three decades of finite volume methods for computational solid mechanics.

### added-mass / FSI stability theory

- **forster2006** — Förster 2006, _The artificial added mass effect in sequential staggered fluid-structu_
  This conference paper analyses the artificial added mass instability inherent in sequentially staggered (loosely coupled) FSI algorithms applied to incompressible flow.
- **yvin2018** — Yvin 2018, _Added mass evaluation with a finite-volume solver for applications in _
  This paper develops and validates a method to evaluate the added mass matrix directly within a cell-centred finite-volume RANS solver (ISIS-CFD) by solving an auxiliary...

### textbook

- **JaimanJoshi2022** — Jaiman 2021, _Computational Mechanics of Fluid-Structure Interaction - Computational_
  This graduate-level textbook presents a comprehensive variational finite element framework for FSI, covering continuum mechanics foundations, ALE formulation, stabilised FE methods, and both partitioned and...

### background

- **antoci2007** — Antoci 2007, _Numerical simulation of fluid–structure interaction by SPH_
  The paper presents a fully Lagrangian SPH formulation for FSI in which both fluid and solid phases are represented by particles.
- **idelsohn2008** — Idelsohn 2008, _Unified Lagrangian formulation for elastic solids and incompressible f_
  This paper presents a unified Lagrangian finite element framework in which both incompressible (or quasi-incompressible) Newtonian fluids and hypo-elastic solids are described by a single...
- **roshchenko2015** — Roshchenko 2015, _A time splitting fictitious domain algorithm for fluid-structure inter_
  This paper develops a mixed Eulerian–Lagrangian finite element fictitious domain method for incompressible fluid interacting with a hyperelastic incompressible solid.
- **meduri2018** — Meduri 2017, _A partitioned fully explicit Lagrangian finite element method for high_
  The paper presents a fully explicit, fully Lagrangian partitioned FSI method for highly nonlinear transient problems with free surfaces and large structural deformation.
- **zarifian2018** — Zarifian 2018, _Sloshing effects on supersonic flutter characteristics of circular cyl_
  The paper develops a finite element fluid-structure interaction model for supersonic flutter of a circular cylindrical shell partially filled with liquid.

## 2. Cross-Reference Against Current Section 1

| BibTeX key (summary) | Resolved bib key | First author | Year | Title (short) | Relevance | Status |
|---|---|---|---|---|---|---|
| `cardiff2026` | `Cardiff2026` | Cardiff | 2026 | A Jacobian-Free Newton-Krylov Method for Cell-Cent | closest prior work in spirit | ✓ |
| `cerquaglia2019` | `—` | Cerquaglia | 2019 | A fully partitioned Lagrangian framework for FSI p | closest prior work in spirit | ✗ missing from bib |
| `degroote2009` | `Degroote2009` | Degroote | 2009 | Performance of a new partitioned procedure versus  | closest prior work in spirit | ✓ |
| `eken2016` | `—` | Eken | 2016 | A parallel monolithic algorithm for the numerical  | closest prior work in spirit | ✗ missing from bib |
| `franci2016` | `—` | Franci | 2016 | Unified Lagrangian formulation for solid and fluid | closest prior work in spirit | ✗ missing from bib |
| `giannopapa2007` | `Giannopapa2007` | Giannopapa | 2007 | Indicative results and progress on the development | closest prior work in spirit | ⚠ in bib, not cited |
| `giannopapa2008` | `Giannopapa2008` | Giannopapa | 2008 | Linear stability analysis and validation of a new  | closest prior work in spirit | ✓ |
| `greenshields1999` | `Greenshields1999b` | Greenshields | 1999 | The finite volume method for coupled fluid flow an | closest prior work in spirit | ✓ |
| `idelsohn2009` | `—` | Idelsohn | 2009 | Fluid-structure interaction problems with strong a | closest prior work in spirit | ✗ missing from bib |
| `liu2014` | `Liu2014` | Liu | 2014 | A stable second-order scheme for fluid–structure i | closest prior work in spirit | ✓ |
| `liu2015` | `—` | Liu | 2015 | A second-order stable explicit interface advancing | closest prior work in spirit | ✗ missing from bib |
| `lozovskiy2015` | `—` | Lozovskiy | 2015 | An unconditionally stable semi-implicit FSI finite | closest prior work in spirit | ✗ missing from bib |
| `lozovskiy2019` | `—` | Lozovskiy | 2019 | Analysis and assessment of a monolithic FSI finite | closest prior work in spirit | ✗ missing from bib |
| `malan2012` | `—` | Malan | 2012 | An accelerated, fully-coupled, parallel 3D hybrid  | closest prior work in spirit | ✗ missing from bib |
| `malan2013` | `—` | Malan | 2013 | An accelerated, fully-coupled, parallel 3D hybrid  | closest prior work in spirit | ✗ missing from bib |
| `michler2004` | `—` | Michler | 2004 | A monolithic approach to fluid–structure interacti | closest prior work in spirit | ✗ missing from bib |
| `ryzhakov2010` | `—` | Ryzhakov | 2010 | A monolithic Lagrangian approach for fluid–structu | closest prior work in spirit | ✗ missing from bib |
| `schott2018b` | `—` | Schott | 2018 | A monolithic approach to fluid-structure interacti | closest prior work in spirit | ✗ missing from bib |
| `schott2019` | `Schott2019` | Schott | 2019 | A monolithic approach to fluid-structure interacti | closest prior work in spirit | ✓ |
| `walhorn2005` | `—` | Walhorn | 2005 | Fluid–structure coupling within a monolithic model | closest prior work in spirit | ✗ missing from bib |
| `vonscheven2010` | `—` | von Scheven | 2010 | Strong coupling schemes for interaction of thin-wa | closest prior work in spirit | ✗ missing from bib |
| `gee2010` | `—` | Gee | 2010 | Truly monolithic algebraic multigrid for fluid-str | FE precedent for block-preconditioned Ne | ✗ missing from bib |
| `heil2004` | `Heil2004` | Heil | 2004 | An efficient solver for the fully coupled solution | FE precedent for block-preconditioned Ne | ✓ |
| `heil2008` | `Heil2008` | Heil | 2008 | Solvers for large-displacement fluid-structure int | FE precedent for block-preconditioned Ne | ✓ |
| `hubner2004` | `—` | Hubner | 2004 | A monolithic approach to fluid–structure interacti | FE precedent for block-preconditioned Ne | ✗ missing from bib |
| `richter2015` | `—` | Richter | 2015 | A monolithic geometric multigrid solver for fluid- | FE precedent for block-preconditioned Ne | ✗ missing from bib |
| `schott2018` | `—` | Schott | 2018 | Monolithic cut finite element based approaches for | FE precedent for block-preconditioned Ne | ✗ missing from bib |
| `cardiff2025` | `Cardiff2025` | Cardiff | 2025 | solids4foam A toolbox for performing solid mechani | FV-but-partitioned | ✓ |
| `gillebaart2016` | `—` | Gillebaart | 2016 | Time consistent fluid structure interaction on col | FV-but-partitioned | ✗ missing from bib |
| `kassiotis2010` | `—` | Kassiotis | 2010 | Nonlinear fluid-structure interaction problem. Par | FV-but-partitioned | ✗ missing from bib |
| `oxtoby2012` | `—` | Oxtoby | 2012 | A matrix-free, implicit, incompressible fractional | FV-but-partitioned | ✗ missing from bib |
| `selim2017` | `Selim2017` | Selim | 2017 | Finite Volume Based Fluid-Structure Interaction So | FV-but-partitioned | ⚠ in bib, not cited |
| `suliman2015` | `—` | Suliman | 2015 | A matrix free, partitioned solution of fluid-struc | FV-but-partitioned | ✗ missing from bib |
| `tsui2013` | `Tsui2013` | Tsui | 2013 | A finite-volume-based approach for dynamic fluid-s | FV-but-partitioned | ⚠ in bib, not cited |
| `tukovic2019` | `Tukovic2019` | Tukovic | 2018 | Added mass partitioned fluid-structure interaction | FV-but-partitioned | ✓ |
| `tukovic2018` | `Tukovic2018` | Tukovic | 2018 | OpenFOAM FINITE VOLUME SOLVER FOR FLUID-SOLID INTE | FV-but-partitioned | ✓ |
| `papadakis2008` | `Papadakis2008` | Papadakis | 2008 | A novel pressure–velocity formulation and solution | FV-but-unified-SIMPLE | ⚠ in bib, not cited |
| `yeo2017` | `—` | Yeo | 2017 | A Unified Momentum Equation Approach for Computing | FV-but-unified-SIMPLE | ✗ missing from bib |
| `greenshields2005` | `Greenshields2005` | Greenshields | 2005 | A unified formulation for continuum mechanics appl | Eulerian-one-continuum FV FSI | ✓ |
| `cardiff2021` | `—` | Cardiff | 2021 | Thirty Years of the Finite Volume Method for Solid | FV solid mechanics foundational | ✗ missing from bib |
| `forster2006` | `—` | Förster | 2006 | The artificial added mass effect in sequential sta | added-mass / FSI stability theory | ✗ missing from bib |
| `yvin2018` | `—` | Yvin | 2018 | Added mass evaluation with a finite-volume solver  | added-mass / FSI stability theory | ✗ missing from bib |
| `jaiman2022` | `JaimanJoshi2022` | Jaiman | 2021 | Computational Mechanics of Fluid-Structure Interac | textbook | ✓ |
| `antoci2007` | `—` | Antoci | 2007 | Numerical simulation of fluid–structure interactio | background | ✗ missing from bib |
| `idelsohn2008` | `—` | Idelsohn | 2008 | Unified Lagrangian formulation for elastic solids  | background | ✗ missing from bib |
| `meduri2018` | `—` | Meduri | 2017 | A partitioned fully explicit Lagrangian finite ele | background | ✗ missing from bib |
| `roshchenko2015` | `—` | Roshchenko | 2015 | A time splitting fictitious domain algorithm for f | background | ✗ missing from bib |
| `zarifian2018` | `—` | Zarifian | 2018 | Sloshing effects on supersonic flutter characteris | background | ✗ missing from bib |

## 3. Flagged Anomalies

### 3a. Directly-Competing and Closest-in-Spirit Papers

#### Cardiff 2026 — A Jacobian-Free Newton-Krylov Method for Cell-Centred Finite Volume Solid Mechan

**Resolved bib key:** `Cardiff2026`  
**Status:** ✓  
**Relevance:** closest prior work in spirit

**Full citation:** Cardiff, P., Armfield, D., Tuković, Ž., Batistić, I. A Jacobian-Free Newton-Krylov Method for Cell-Centred Finite Volume Solid Mechanics. International Journal for Numerical Methods in Engineering, 127(3):e70268, 2026. DOI: 10.1002/nme.70268

**Direct quote(s):**
"the first (to the authors' knowledge) to propose a Jacobian-free Newton-Krylov approach for finite volume solid mechanics" (p.4); "we propose to use the compact-stencil approximate Jacobian from the segregated algorithm as the preconditioning matrix" (p.12); "The implementation is made publicly available within the solids4foam toolbox for OpenFOAM" (p.31).

**Notes for the authors:**
Do not cite this as monolithic FSI prior work: the paper is solid-mechanics-focused, and the Turek-Hron FSI3 case uses a segregated PIMPLE fluid solver with partitioned interface quasi-Newton coupling. The abstract reports elastoplastic divergence, consistent with Section 4.2.

---

#### Cerquaglia 2019 — A fully partitioned Lagrangian framework for FSI problems characterized by free 

**Resolved bib key:** `cerquaglia2019`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Cerquaglia, M. L., Thomas, D., Boman, R., Terrapon, V., Ponthot, J.-P. A fully partitioned Lagrangian framework for FSI problems characterized by free surfaces, large solid deformations and displacements, and strong added-mass effects. Computer Methods in Applied Mechanics and Engineering, 348:409-442, 2019. DOI: 10.1016/j.cma.2019.01.021

**Direct quote(s):**
"fully partitioned Lagrangian framework" (p.1); "partitioned FSI coupling" (p.1); "matrix-free and directly provides an approximation of the inverse Jacobian" (p.8).

**Notes for the authors:**
Closest in spirit because it uses matrix-free IQN-ILS and black-box solver coupling for severe added-mass FSI, but it is fully partitioned PFEM/FEM rather than quasi-monolithic cell-centred FV/JFNK/PETSc. No abstract-method inconsistency found.

---

#### Degroote 2009 — Performance of a new partitioned procedure versus a monolithic procedure in flui

**Resolved bib key:** `Degroote2009`  
**Status:** ✓  
**Relevance:** closest prior work in spirit

**Full citation:** Degroote, J., Bathe, K.-J., Vierendeels, J. Performance of a new partitioned procedure versus a monolithic procedure in fluid-structure interaction. Computers and Structures, 87:793-801, 2009. DOI: 10.1016/j.compstruc.2008.11.013

**Direct quote(s):**
"compared with a monolithic Newton algorithm" (p.1); "the partitioned IQN-ILS method and the MN method are compared" (p.4)

**Notes for the authors:**
Not directly competing with cell-centred FV/JFNK work: this study uses finite elements in ADINA, direct sparse solves, and full Newton-Raphson iterations rather than OpenFOAM/solids4foam, PETSc Krylov solvers, or a cell-centred FV discretisation.

---

#### Eken 2016 — A parallel monolithic algorithm for the numerical simulation of large-scale flui

**Resolved bib key:** `eken2016`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Eken, A. and Sahin, M. A parallel monolithic algorithm for the numerical simulation of large-scale fluid structure interaction problems. Int. J. Numer. Meth. Fluids, 80(11):687–714, 2016. DOI: 10.1002/fld.4169

**Direct quote(s):**
"The goal of the present paper is to incorporate the ALE-based unstructured finite volume algorithm [11] with the classical Galerkin finite element discretization for the solid domain in order to develop a novel monolithic algorithm for the large-scale simulation of FSI problems in a fully coupled form" (p. 688). "In the present paper, the original system of equations is multiplied with an upper triangular right preconditioner that results in a scaled discrete Laplacian instead of a zero block in the original system. Then, a one-level restricted additive Schwarz preconditioner with a block-incomplete factorization within each partitioned sub-domains is utilized for the modified fully coupled system." (p. 689).

**Notes for the authors:**
The fluid discretisation is side-centred (staggered) rather than cell-centred collocated: velocities live at face midpoints, not cell centroids. This distinguishes it from the cell-centred FV approach in the paper under review. The solid uses standard FE, not FV. The Newton-Krylov preconditioner strategy (right-preconditioned triangular block approach replacing the zero divergence block with a Laplacian) is directly analogous in spirit to the block-preconditioning strategy used in the paper under review, making this a key reference for comparison, albeit on a different mesh arrangement. Parallelism is achieved via domain decomposition with PETSc/METIS; scaling results are reported up to 128 cores with ~2.5M DOF.

---

#### Franci 2016 — Unified Lagrangian formulation for solid and fluid mechanics and FSI problems

**Resolved bib key:** `franci2016`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Franci, A., Onate, E., Carbonell, J. M. Unified Lagrangian formulation for solid and fluid mechanics and FSI problems. Computer Methods in Applied Mechanics and Engineering, 298:520-547, 2016. DOI: 10.1016/j.cma.2015.09.023

**Direct quote(s):**
"We present a Lagrangian monolithic strategy for solving fluid-structure interaction (FSI) problems." (p.1); "fluids and solids are solved within the same linear system of algebraic equations" (p.3).

**Notes for the authors:**
Closest in spirit because it is monolithic and unified, but it is FE/PFEM with a two-step Gauss-Seidel pressure-velocity procedure, not cell-centred FV, JFNK, PETSc, or block-preconditioned.

---

#### Giannopapa 2007 — Indicative results and progress on the development of the unified single solutio

**Resolved bib key:** `Giannopapa2007`  
**Status:** ⚠ in bib, not cited  
**Relevance:** closest prior work in spirit

**Full citation:** Giannopapa, C. G., Papadakis, G. Indicative results and progress on the development of the unified single solution method for fluid-structure interaction problems. N/A, 2007. DOI: N/A

**Direct quote(s):**
"The new approach is based on continuum mechanics formulation for fluids and structures where both continua can be solved using the momentum and continuity equation" (p.1); "The finite volume method was used for the discretisation of the equations" (p.3); "the interface between fluid and solid is part of the inner computational domain and no explicit exchange of information is needed" (p.4).

**Notes for the authors:**
Abstract and conclusions describe a fully implicit unified FSI method, but the numerical method is a PISO velocity-pressure algorithm, not Newton-Krylov/JFNK or block-preconditioned. The paper presents preliminary tube-wave results and states that validation against analytical and established computational methods is future work.

---

#### Giannopapa 2008 — Linear stability analysis and validation of a new solution method of the elastod

**Resolved bib key:** `Giannopapa2008`  
**Status:** ✓  
**Relevance:** closest prior work in spirit

**Full citation:** Giannopapa, C. G., Papadakis, G. Linear stability analysis and validation of a unified solution method for fluid-structure-interaction on a structural dynamic problem. Journal of Pressure Vessel Technology, N/A, 2008. DOI: N/A

**Direct quote(s):**
"treats both fluid and solid as a single continuum" (p.1); "A single set of equations is used to describe the fluid and solid" (p.2); "the finite volume method is used here for solids as well" (p.3).

**Notes for the authors:**
Although framed as a unified FSI method, the validation in this paper is a solid-only transient beam-bending problem; full FSI is described as the next step rather than demonstrated.

---

#### Greenshields 1999 — The finite volume method for coupled fluid flow and stress analysis

**Resolved bib key:** `Greenshields1999b`  
**Status:** ✓  
**Relevance:** closest prior work in spirit

**Full citation:** Greenshields, C. J., Weller, H. G., and Ivankovic, A. The finite volume method for coupled fluid flow and stress analysis. Computer Modeling and Simulation in Engineering, 4(3):213-218, 1999. DOI: N/A

**Direct quote(s):**
"The use of a single code enables simple transfer of information" (p.3); "dependent variables and material properties are stored at each cell centroid" (p.4).

**Notes for the authors:**
The abstract describes an implicit solution procedure for the whole system, but Section 4 shows a partitioned strong-coupling algorithm with separate fluid and structure solves plus outer iterations. It is highly relevant as early OpenFOAM/FOAM cell-centred FV FSI, but it is not quasi-monolithic, Newton-Krylov, PETSc-based, or block-preconditioned.

---

#### Idelsohn 2009 — Fluid-structure interaction problems with strong added-mass effect

**Resolved bib key:** `idelsohn2009`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Idelsohn, S. R., Del Pin, F., Rossi, R., and Oñate, E. Fluid-structure interaction problems with strong added-mass effect. International Journal for Numerical Methods in Engineering, 80:1261-1294, 2009. DOI: 10.1002/nme.2659

**Direct quote(s):**
"The monolithic fluid–structure problem is partitioned using a static condensation of the velocity terms." (p.1); "Starting from the monolithical approach the ‘exact’ way to segregate the pressure" (p.3); "The problems were tested with both methods: monolithic with pressure segregation and with a strongly coupled partitioned scheme" (p.23).

**Notes for the authors:**
Close algorithmic precedent for using an approximate pressure/interface operator derived from monolithic static condensation to address added-mass effects, but it is FE/PFEM-ALE and projection/fixed-point based rather than cell-centred FV, JFNK, PETSc, or block-preconditioned Newton-Krylov. No abstract/method inconsistency found.

---

#### Liu 2014 — A stable second-order scheme for fluid–structure interaction with strong added-m

**Resolved bib key:** `Liu2014`  
**Status:** ✓  
**Relevance:** closest prior work in spirit

**Full citation:** Liu, J., Jaiman, R. K., Gurugubelli, P. S. A stable second-order scheme for fluid-structure interaction with strong added-mass effects. Journal of Computational Physics, 270:687-710, 2014. DOI: 10.1016/j.jcp.2014.04.020

**Direct quote(s):**
"fully coupled FSI problems which is stable for any mass density ratio" (p.2).

**Notes for the authors:**
The paper is close in spirit because it targets stable fully coupled FSI with strong added-mass effects, but it is FE-based CFEI with explicit interface advancement, semi-implicit linearisation, and direct linear solves, not cell-centred FV/JFNK/PETSc/block-preconditioned. The abstract calls the method stable for any mass density ratio; Section 3 clarifies that no Newton-Raphson iteration is used.

---

#### Liu 2015 — A second-order stable explicit interface advancing scheme for FSI with both rigi

**Resolved bib key:** `liu2015`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Liu, J. A second-order stable explicit interface advancing scheme for FSI with both rigid and elastic structures and its application to fish swimming simulations. Computers & Fluids, N/A(N/A):N/A, 2015. DOI: 10.1016/j.compfluid.2015.06.002

**Direct quote(s):**
"we take the monolithic approach" (p.6); "removed the mesh position from the list of unknown variables" (p.6).

**Notes for the authors:**
Close in spirit because it is a monolithic ALE FSI method with explicit interface/mesh advancement outside the coupled solve, but it is FE-based, uses semi-implicit linearisation and direct MATLAB solves, and explicitly states that iterative preconditioners are planned future work rather than used here.

---

#### Lozovskiy 2015 — An unconditionally stable semi-implicit FSI finite element method

**Resolved bib key:** `lozovskiy2015`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Lozovskiy, A., Olshanskii, M. A., Salamatova, V., Vassilevski, Y. V. An unconditionally stable semi-implicit FSI finite element method. Comput. Methods Appl. Mech. Engrg., 297:437-454, 2015. DOI: 10.1016/j.cma.2015.09.014

**Direct quote(s):**
"monolithic strongly coupled finite element method" (p.3); "only a linear algebraic system should be solved" (p.7)

**Notes for the authors:**
Closest in monolithic/ALE/strong-coupling spirit, but not cell-centred FV and not Newton-Krylov; the paper explicitly leaves preconditioned iterative solvers for future work.

---

#### Lozovskiy 2019 — Analysis and assessment of a monolithic FSI finite element method

**Resolved bib key:** `lozovskiy2019`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Lozovskiy, A., Olshanskii, M. A., Vassilevski, Y. V. Analysis and assessment of a monolithic FSI finite element method. Computers and Fluids, 179:277–288, 2019. DOI: 10.1016/j.compfluid.2018.11.004

**Direct quote(s):**
"we analyze and investigate numerically a monolithic finite element method for the incompressible Navier–Stokes equations coupled to the Saint Venant–Kirchhoff hyperelastic model" (p.2); "The approach strongly enforces the coupling conditions on the fluid–structure interface" (p.2); "In the monolithic approach we consider conforming FE spaces" (p.6).

**Notes for the authors:**
The method is monolithic FE and uses lagged geometric/advection terms with a direct MUMPS solve in the reported experiments; it does not describe JFNK, PETSc, cell-centred FV, or a block preconditioner.

---

#### Malan 2012 — An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure 

**Resolved bib key:** `malan2012`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Malan, A. G., Oxtoby, O. F. An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure interaction scheme. Preprint submitted to Computer Methods in Applied Mechanics and Engineering, 2012. DOI: N/A

**Direct quote(s):**
"a fast, parallel 3D, fully-coupled partitioned hybrid-unstructured finite volume fluid-structure-interaction (FSI) scheme" (p.1); "a strongly coupled, partitioned, matrix-free iterative solution process" (p.7); "As far as fluid-structure interaction is concerned, the method above represents a block-Jacobi method" (p.14).

**Notes for the authors:**
The abstract and title emphasise "fully-coupled", but Section 4.5 states the FSI coupling is block-Jacobi and the introduction explicitly frames the method as partitioned. It is close in finite-volume, matrix-free, strongly coupled spirit, but not quasi-monolithic and not JFNK.

---

#### Malan 2013 — An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure 

**Resolved bib key:** `malan2013`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Malan, A. G., Oxtoby, O. F. An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure interaction scheme. Computer Methods in Applied Mechanics and Engineering, 253:426-438, 2013. DOI: 10.1016/j.cma.2012.09.004

**Direct quote(s):**
"we propose a fast, parallel 3D, fully-coupled partitioned hybrid-unstructured finite volume fluid-structure-interaction (FSI) scheme" (p.1); "We therefore advocate a strongly coupled, partitioned, matrix-free iterative solution process" (p.4); "the method above represents a block-Jacobi method" (p.6).

**Notes for the authors:**
The "fully-coupled" terminology means strongly coupled partitioned dual-time iterations, not a monolithic Newton or JFNK solve; Section 4.5 explicitly identifies the FSI-level method as block-Jacobi and notes possible added-mass robustness limits.

---

#### Michler 2004 — A monolithic approach to fluid–structure interaction

**Resolved bib key:** `michler2004`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Michler, C., Hulshoff, S. J., van Brummelen, E. H., de Borst, R. A monolithic approach to fluid-structure interaction. Computers & Fluids, 33:839-848, 2004. DOI: 10.1016/j.compfluid.2003.06.006

**Direct quote(s):**
"This paper compares partitioned and monolithic solution procedures for the numerical simulation of fluid-structure interactions." (p.1); "In a monolithic method, the interaction of the fluid and the structure at the mutual interface is treated synchronously." (p.4); "The discretized equations are then typically solved by multiple fluid-structure iterations" (p.4).

**Notes for the authors:**
Monolithic FSI precedent focused on stability, accuracy, and cost, but the model is one-dimensional with a spring-mass piston, the fluid discretisation is FE/DG rather than cell-centred FV, and no Newton-Krylov, JFNK, PETSc, or block preconditioner is described.

---

#### Ryzhakov 2010 — A monolithic Lagrangian approach for fluid–structure interaction problems

**Resolved bib key:** `ryzhakov2010`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Ryzhakov, P. B., Rossi, R., Idelsohn, S. R., Oñate, E. A monolithic Lagrangian approach for fluid–structure interaction problems. Computational Mechanics, 46:883–899, 2010. DOI: 10.1007/s00466-010-0522-0

**Direct quote(s):**
"Current work presents a monolithic method for the solution of fluid–structure interaction problems involving flexible structures and free-surface flows." (p.1); "The method described features a global pressure condensation which in turn enables the definition of a purely displacement-based linear system of equations." (p.1); "The choice of using Krylov-type methods implies that a matrix-free approach can be used" (p.9).

**Notes for the authors:**
Closest in monolithic/matrix-free spirit, but the discretisation is PFEM/finite element with diagonally preconditioned CG, not cell-centred FV, JFNK, PETSc, or block-preconditioned FSI.

---

#### Schott 2018 — A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-

**Resolved bib key:** `schott2018b`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Schott, B., Ager, C., Wall, W. A. A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-ALE fluid domain decomposition involving cut elements. arXiv preprint arXiv:1808.00343, 2018.

**Direct quote(s):**
"full-implicit monolithic way" (p.29); "not limited to Finite Element based schemes" (p.8).

**Notes for the authors:**
No abstract/method inconsistency found. This is monolithic FE/CutFEM with Newton-Raphson and Nitsche coupling, not cell-centred FV, OpenFOAM/PETSc, JFNK, or a block-preconditioned method. The PDF is an arXiv 2018 preprint and no DOI appears in the PDF or metadata.

---

#### Schott 2019 — A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-

**Resolved bib key:** `Schott2019`  
**Status:** ✓  
**Relevance:** closest prior work in spirit

**Full citation:** Schott, B., Ager, C., Wall, W. A. A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-ALE fluid domain decomposition involving cut elements. International Journal for Numerical Methods in Engineering, 00:2-33, 2019. DOI: 10.1002/nme.6047

**Direct quote(s):**
"A novel method for complex fluid-structure interaction (FSI) involving large structural deformation and motion is proposed." (p.1); "A clear advantage over existing overlapping domain decomposition methods consists in the sharp splitting of the fluid domain which comes along with improved convergence behavior of the resulting monolithic FSI system." (p.1); "This discretization technique is not limited to finite element based schemes, but can be realized in finite volume frameworks as well, even though FEM is chosen in the present work." (p.3).

**Notes for the authors:**
Closest in monolithic/hybrid FSI spirit, but it is FE/CutFEM with Nitsche and Newton-Raphson rather than cell-centred FV, JFNK, PETSc, or block-preconditioned quasi-monolithic FSI.

---

#### Walhorn 2005 — Fluid–structure coupling within a monolithic model involving free surface flows

**Resolved bib key:** `walhorn2005`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** Walhorn, E., Kölke, A., Hübner, B., Dinkler, D. Fluid–structure coupling within a monolithic model involving free surface flows. Computers and Structures, 83(2100–2111), 2005. DOI: 10.1016/j.compstruc.2005.03.010

**Direct quote(s):**
"The article presents a monolithic approach to solve fluid–structure interaction problems with free surface flows and strong coupling in a single system of equations." (p. 2101); "The monolithic formulation of fluid, structure, and coupling conditions in a single equation system, shown in Fig. 6 without pressure, allows the analysis of the coupled system. This applies because the equation system describes the behavior of the fully coupled system in the current space–time slab. The highly non-linear system is solved by a Picard iteration scheme." (p. 2103)

**Notes for the authors:**
The nonlinear solver is Picard (3–4 iterations claimed sufficient), not Newton or JFNK, so there is no Jacobian or preconditioner discussion. The block structure in Fig. 6 (K_F, B, B^T, K_S sub-blocks with interface traction unknowns t) is directly comparable to the block system targeted by the approximate block preconditioner in the present paper. The paper also covers two-fluid/free-surface physics via level set with extended FE basis functions — a feature not present in the target paper but worth acknowledging if free-surface extensions are discussed.

---

#### von Scheven 2010 — Strong coupling schemes for interaction of thin-walled structures and incompress

**Resolved bib key:** `vonscheven2010`  
**Status:** ✗ missing from bib  
**Relevance:** closest prior work in spirit

**Full citation:** von Scheven, M., Ramm, E. Strong coupling schemes for interaction of thin-walled structures and incompressible flows. International Journal for Numerical Methods in Engineering, 87:214-231, 2011. DOI: 10.1002/nme.3033

**Direct quote(s):**
"Different partitioned strong coupling approaches are presented and compared" (p.1); "a Newton-Krylov approach" (p.1); "Jacobian is not required explicitly" (p.10).

**Notes for the authors:**
Closest in spirit for Newton-Krylov FSI coupling, but it is partitioned interface coupling with FE/FE discretisation, not quasi-monolithic cell-centred FV; no block preconditioner is described.

---

### 3b. All Papers with Non-Empty "Notes for the Authors"

#### Cardiff 2026 — A Jacobian-Free Newton-Krylov Method for Cell-Centred Finite Volume Solid Mechan

**Relevance:** closest prior work in spirit  
**Status:** ✓

Do not cite this as monolithic FSI prior work: the paper is solid-mechanics-focused, and the Turek-Hron FSI3 case uses a segregated PIMPLE fluid solver with partitioned interface quasi-Newton coupling. The abstract reports elastoplastic divergence, consistent with Section 4.2.

---

#### Cerquaglia 2019 — A fully partitioned Lagrangian framework for FSI problems characterized by free 

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Closest in spirit because it uses matrix-free IQN-ILS and black-box solver coupling for severe added-mass FSI, but it is fully partitioned PFEM/FEM rather than quasi-monolithic cell-centred FV/JFNK/PETSc. No abstract-method inconsistency found.

---

#### Degroote 2009 — Performance of a new partitioned procedure versus a monolithic procedure in flui

**Relevance:** closest prior work in spirit  
**Status:** ✓

Not directly competing with cell-centred FV/JFNK work: this study uses finite elements in ADINA, direct sparse solves, and full Newton-Raphson iterations rather than OpenFOAM/solids4foam, PETSc Krylov solvers, or a cell-centred FV discretisation.

---

#### Eken 2016 — A parallel monolithic algorithm for the numerical simulation of large-scale flui

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

The fluid discretisation is side-centred (staggered) rather than cell-centred collocated: velocities live at face midpoints, not cell centroids. This distinguishes it from the cell-centred FV approach in the paper under review. The solid uses standard FE, not FV. The Newton-Krylov preconditioner strategy (right-preconditioned triangular block approach replacing the zero divergence block with a Laplacian) is directly analogous in spirit to the block-preconditioning strategy used in the paper under review, making this a key reference for comparison, albeit on a different mesh arrangement. Parallelism is achieved via domain decomposition with PETSc/METIS; scaling results are reported up to 128 cores with ~2.5M DOF.

---

#### Franci 2016 — Unified Lagrangian formulation for solid and fluid mechanics and FSI problems

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Closest in spirit because it is monolithic and unified, but it is FE/PFEM with a two-step Gauss-Seidel pressure-velocity procedure, not cell-centred FV, JFNK, PETSc, or block-preconditioned.

---

#### Giannopapa 2007 — Indicative results and progress on the development of the unified single solutio

**Relevance:** closest prior work in spirit  
**Status:** ⚠ in bib, not cited

Abstract and conclusions describe a fully implicit unified FSI method, but the numerical method is a PISO velocity-pressure algorithm, not Newton-Krylov/JFNK or block-preconditioned. The paper presents preliminary tube-wave results and states that validation against analytical and established computational methods is future work.

---

#### Giannopapa 2008 — Linear stability analysis and validation of a new solution method of the elastod

**Relevance:** closest prior work in spirit  
**Status:** ✓

Although framed as a unified FSI method, the validation in this paper is a solid-only transient beam-bending problem; full FSI is described as the next step rather than demonstrated.

---

#### Greenshields 1999 — The finite volume method for coupled fluid flow and stress analysis

**Relevance:** closest prior work in spirit  
**Status:** ✓

The abstract describes an implicit solution procedure for the whole system, but Section 4 shows a partitioned strong-coupling algorithm with separate fluid and structure solves plus outer iterations. It is highly relevant as early OpenFOAM/FOAM cell-centred FV FSI, but it is not quasi-monolithic, Newton-Krylov, PETSc-based, or block-preconditioned.

---

#### Idelsohn 2009 — Fluid-structure interaction problems with strong added-mass effect

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Close algorithmic precedent for using an approximate pressure/interface operator derived from monolithic static condensation to address added-mass effects, but it is FE/PFEM-ALE and projection/fixed-point based rather than cell-centred FV, JFNK, PETSc, or block-preconditioned Newton-Krylov. No abstract/method inconsistency found.

---

#### Liu 2014 — A stable second-order scheme for fluid–structure interaction with strong added-m

**Relevance:** closest prior work in spirit  
**Status:** ✓

The paper is close in spirit because it targets stable fully coupled FSI with strong added-mass effects, but it is FE-based CFEI with explicit interface advancement, semi-implicit linearisation, and direct linear solves, not cell-centred FV/JFNK/PETSc/block-preconditioned. The abstract calls the method stable for any mass density ratio; Section 3 clarifies that no Newton-Raphson iteration is used.

---

#### Liu 2015 — A second-order stable explicit interface advancing scheme for FSI with both rigi

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Close in spirit because it is a monolithic ALE FSI method with explicit interface/mesh advancement outside the coupled solve, but it is FE-based, uses semi-implicit linearisation and direct MATLAB solves, and explicitly states that iterative preconditioners are planned future work rather than used here.

---

#### Lozovskiy 2015 — An unconditionally stable semi-implicit FSI finite element method

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Closest in monolithic/ALE/strong-coupling spirit, but not cell-centred FV and not Newton-Krylov; the paper explicitly leaves preconditioned iterative solvers for future work.

---

#### Lozovskiy 2019 — Analysis and assessment of a monolithic FSI finite element method

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

The method is monolithic FE and uses lagged geometric/advection terms with a direct MUMPS solve in the reported experiments; it does not describe JFNK, PETSc, cell-centred FV, or a block preconditioner.

---

#### Malan 2012 — An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure 

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

The abstract and title emphasise "fully-coupled", but Section 4.5 states the FSI coupling is block-Jacobi and the introduction explicitly frames the method as partitioned. It is close in finite-volume, matrix-free, strongly coupled spirit, but not quasi-monolithic and not JFNK.

---

#### Malan 2013 — An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure 

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

The "fully-coupled" terminology means strongly coupled partitioned dual-time iterations, not a monolithic Newton or JFNK solve; Section 4.5 explicitly identifies the FSI-level method as block-Jacobi and notes possible added-mass robustness limits.

---

#### Michler 2004 — A monolithic approach to fluid–structure interaction

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Monolithic FSI precedent focused on stability, accuracy, and cost, but the model is one-dimensional with a spring-mass piston, the fluid discretisation is FE/DG rather than cell-centred FV, and no Newton-Krylov, JFNK, PETSc, or block preconditioner is described.

---

#### Ryzhakov 2010 — A monolithic Lagrangian approach for fluid–structure interaction problems

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Closest in monolithic/matrix-free spirit, but the discretisation is PFEM/finite element with diagonally preconditioned CG, not cell-centred FV, JFNK, PETSc, or block-preconditioned FSI.

---

#### Schott 2018 — A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

No abstract/method inconsistency found. This is monolithic FE/CutFEM with Newton-Raphson and Nitsche coupling, not cell-centred FV, OpenFOAM/PETSc, JFNK, or a block-preconditioned method. The PDF is an arXiv 2018 preprint and no DOI appears in the PDF or metadata.

---

#### Schott 2019 — A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-

**Relevance:** closest prior work in spirit  
**Status:** ✓

Closest in monolithic/hybrid FSI spirit, but it is FE/CutFEM with Nitsche and Newton-Raphson rather than cell-centred FV, JFNK, PETSc, or block-preconditioned quasi-monolithic FSI.

---

#### Walhorn 2005 — Fluid–structure coupling within a monolithic model involving free surface flows

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

The nonlinear solver is Picard (3–4 iterations claimed sufficient), not Newton or JFNK, so there is no Jacobian or preconditioner discussion. The block structure in Fig. 6 (K_F, B, B^T, K_S sub-blocks with interface traction unknowns t) is directly comparable to the block system targeted by the approximate block preconditioner in the present paper. The paper also covers two-fluid/free-surface physics via level set with extended FE basis functions — a feature not present in the target paper but worth acknowledging if free-surface extensions are discussed.

---

#### von Scheven 2010 — Strong coupling schemes for interaction of thin-walled structures and incompress

**Relevance:** closest prior work in spirit  
**Status:** ✗ missing from bib

Closest in spirit for Newton-Krylov FSI coupling, but it is partitioned interface coupling with FE/FE discretisation, not quasi-monolithic cell-centred FV; no block preconditioner is described.

---

#### Gee 2010 — Truly monolithic algebraic multigrid for fluid-structure interaction

**Relevance:** FE precedent for block-preconditioned Newton-Krylov FSI  
**Status:** ✗ missing from bib

Strong prior art for monolithic block-preconditioned Newton-Krylov FSI, but it is FE/ALE with assembled Jacobian blocks and AMG, not cell-centred FV, OpenFOAM/solids4foam, PETSc, or Jacobian-free residual differencing.

---

#### Heil 2004 — An efficient solver for the fully coupled solution of large-displacement fluid-s

**Relevance:** FE precedent for block-preconditioned Newton-Krylov FSI  
**Status:** ✓

Strong FE precedent for monolithic Newton-GMRES FSI with block-triangular approximate Jacobian preconditioning and pressure Schur-complement/multigrid approximations. Not cell-centred FV, not Jacobian-free, and not OpenFOAM/PETSc.

---

#### Heil 2008 — Solvers for large-displacement fluid-structure interaction problems - segregated

**Relevance:** FE precedent for block-preconditioned Newton-Krylov FSI  
**Status:** ✓

Monolithic FE Newton-Krylov/block-preconditioned FSI precedent in oomph-lib; not cell-centred FV, not OpenFOAM/PETSc, and not Jacobian-free. The paper compares against segregated Picard solvers and includes exact Jacobian interaction blocks in the monolithic Newton linearisation.

---

#### Hubner 2004 — A monolithic approach to fluid–structure interaction using space–time finite ele

**Relevance:** FE precedent for block-preconditioned Newton-Krylov FSI  
**Status:** ✗ missing from bib

The nonlinear solver is Picard (not Newton or JFNK), but the paper is the canonical early monolithic FE-FSI reference with a block-assembled system solved by a Krylov method (BiCGStab) with an LU-based preconditioner — directly analogous in spirit to the block-preconditioned JFNK approach of the paper being written, but using FE rather than cell-centred FV. The scalability limitation is explicitly acknowledged: the direct LU preconditioner is impractical for large 3D problems, which motivates the need for approximate block preconditioners such as those used in the authors' own work.

---

#### Richter 2015 — A monolithic geometric multigrid solver for fluid-structure interactions in ALE 

**Relevance:** FE precedent for block-preconditioned Newton-Krylov FSI  
**Status:** ✗ missing from bib

Strongly relevant monolithic FE Newton-GMRES/multigrid precedent, but not cell-centred FV, OpenFOAM/PETSc, or Jacobian-free; the Jacobian is analytically evaluated and sometimes reused in an approximate Newton scheme.

---

#### Schott 2018 — Monolithic cut finite element based approaches for fluid-structure interaction

**Relevance:** FE precedent for block-preconditioned Newton-Krylov FSI  
**Status:** ✗ missing from bib

Strongly relevant as monolithic FE/CutFEM FSI with Newton-like nonlinear solves and block-preconditioned GMRES, but not cell-centred FV, not OpenFOAM/solids4foam/PETSc, and not Jacobian-free; the paper appears to assemble linearized matrices and treats some geometry/interface-normal terms in a fixed-point fashion.

---

#### Cardiff 2025 — solids4foam A toolbox for performing solid mechanics and fluid-solid interaction

**Relevance:** FV-but-partitioned  
**Status:** ✓

JOSS software paper rather than a detailed numerical-method paper; no direct JFNK, PETSc, or quasi-monolithic method is described in the inspected text.

---

#### Gillebaart 2016 — Time consistent fluid structure interaction on collocated grids for incompressib

**Relevance:** FV-but-partitioned  
**Status:** ✗ missing from bib

Highly relevant collocated FV/ALE FSI predecessor, but Section 2.6.1 explicitly uses partitioned black-box fluid/solid coupling with Aitken or IQN-ILS interface iterations, not monolithic or quasi-monolithic JFNK with a block preconditioner.

---

#### Kassiotis 2010 — Nonlinear fluid-structure interaction problem. Part II: space discretization, im

**Relevance:** FV-but-partitioned  
**Status:** ✗ missing from bib

Published online in 2010 but the journal issue is Computational Mechanics 47, 2011. The abstract says the framework can accommodate other schemes, but the implemented FSI examples use partitioned DFMT-BGS coupling, not monolithic Newton/JFNK.

---

#### Oxtoby 2012 — A matrix-free, implicit, incompressible fractional-step algorithm for fluid–stru

**Relevance:** FV-but-partitioned  
**Status:** ✗ missing from bib

The solver is partitioned but achieves strong (sub-iteration level) coupling via the dual-timestepping loop — fluid and solid are solved concurrently within each pseudo-timestep, with interface conditions exchanged every iteration. This is worth distinguishing from loosely-coupled staggered partitioned schemes. The LU-SGS preconditioned GMRES applied to the pressure equation is conceptually analogous to (but distinct from) the block-preconditioned Krylov approach used for the monolithic system in the target paper. The Elemental code appears to be an in-house research code and is not publicly available.

---

#### Selim 2017 — Finite Volume Based Fluid-Structure Interaction Solver

**Relevance:** FV-but-partitioned  
**Status:** ⚠ in bib, not cited

---

---

#### Suliman 2015 — A matrix free, partitioned solution of fluid-structure interaction problems usin

**Relevance:** FV-but-partitioned  
**Status:** ✗ missing from bib

Coupling is at solver sub-iteration level and described as fully coupled, but the method remains partitioned rather than monolithic; no JFNK or block preconditioner is used.

---

#### Tsui 2013 — A finite-volume-based approach for dynamic fluid-structure interaction

**Relevance:** FV-but-partitioned  
**Status:** ⚠ in bib, not cited

This is a finite-volume FSI predecessor with moving meshes and a single in-house FV framework, but it is explicitly sequential/partitioned rather than monolithic or JFNK/block-preconditioned.

---

#### Tukovic 2018 — Added mass partitioned fluid-structure interaction solver based on a Robin bound

**Relevance:** FV-but-partitioned  
**Status:** ✓

This is the direct predecessor/companion paper to the other Tukovic 2018 work in this review (tukovic2018). Both use cell-centred FV for fluid and solid; this paper's Robin pressure BC and Robin-Neumann partitioned scheme are the closest published FV-partitioned approach to the target paper's cell-centred FV framework. The paper does not display a journal name, volume, issue, page numbers, or DOI anywhere in the PDF — publication metadata should be verified externally (likely published in a Springer journal such as the OpenFOAM proceedings or a computational mechanics journal). Future work stated explicitly: second-order temporal accuracy and full kinematically coupled beta-scheme implementation in cell-centred FV.

---

#### Tukovic 2018 — OpenFOAM FINITE VOLUME SOLVER FOR FLUID-SOLID INTERACTION

**Relevance:** FV-but-partitioned  
**Status:** ✓

The paper is highly relevant as an OpenFOAM, cell-centred FV FSI predecessor, but it is explicitly partitioned and uses PISO plus segregated solid solves rather than monolithic Newton/JFNK or a block preconditioner.

---

#### Papadakis 2008 — A novel pressure–velocity formulation and solution method for fluid–structure in

**Relevance:** FV-but-unified-SIMPLE  
**Status:** ⚠ in bib, not cited

The abstract and conclusions call the approach fully coupled, but the nonlinear solution strategy is SIMPLE pressure correction rather than Newton-Krylov/JFNK or a block-preconditioned monolithic solve. The paper assumes small displacements and a fixed Eulerian mesh; it explicitly states that large deformations would require ALE mesh motion.

---

#### Yeo 2017 — A Unified Momentum Equation Approach for Computing Flow-Induced Stresses in Stru

**Relevance:** FV-but-unified-SIMPLE  
**Status:** ✗ missing from bib

Although the abstract calls the method monolithic, the method is a unified stationary-boundary/SIMPLE formulation rather than a moving-mesh FSI formulation with Newton-Krylov or block preconditioning.

---

#### Greenshields 2005 — A unified formulation for continuum mechanics applied to fluid–structure interac

**Relevance:** Eulerian-one-continuum FV FSI  
**Status:** ✓

Abstract and method are consistent. The paper is highly relevant as an OpenFOAM FV unified-continuum predecessor, but the solver is segregated/PISO-like and Eulerian, not JFNK/PETSc/block-preconditioned or ALE quasi-monolithic.

---

#### Cardiff 2021 — Thirty Years of the Finite Volume Method for Solid Mechanics

**Relevance:** FV solid mechanics foundational  
**Status:** ✗ missing from bib

Review article rather than original solver paper; volume, issue, and page range were not visible in the extracted PDF text or pdfinfo metadata.

---

#### Förster 2006 — The artificial added mass effect in sequential staggered fluid-structure interac

**Relevance:** added-mass / FSI stability theory  
**Status:** ✗ missing from bib

This is a conference paper companion to the journal article by the same group (Förster, Wall, Ramm, submitted to CMAME 2006, reference [5] in the paper). That journal version likely contains the full derivation and should be sought. The key take-away for the monolithic/JFNK paper is that partitioned sequential staggered schemes are fundamentally limited by the fluid-to-solid density ratio — motivating monolithic or iteratively-staggered approaches. The driven cavity with flexible bottom used here is the Mok benchmark.

---

#### Yvin 2018 — Added mass evaluation with a finite-volume solver for applications in fluid–stru

**Relevance:** added-mass / FSI stability theory  
**Status:** ✗ missing from bib

The paper is relevant as background on the added-mass instability that motivates implicit/monolithic coupling. The BGS-IFC algorithm (one linearised Picard fluid iteration per coupling step) is distinct from the JFNK approach but is a noteworthy partitioned alternative that also avoids full fluid resolves at each coupling iteration. The FV added-mass pressure equation (Eq. 20) is solved with the same cell-centred discretisation as the main flow, which may be of interest when discussing how partitioned methods handle added-mass stabilisation compared to the monolithic block-preconditioned approach.

---

#### Jaiman 2021 — Computational Mechanics of Fluid-Structure Interaction - Computational Methods f

**Relevance:** textbook  
**Status:** ✓

The quasi-monolithic strategy in Ch. 6 is closely related in spirit to the approach being developed (explicit interface/ALE treatment to avoid nonlinear iterations, single block-system solve per time step), but is entirely FE-based whereas the present work uses cell-centred FV. The book explicitly contrasts its approach with "finite-volume discretization for the fluid equations in combination with a finite-element discretization for the structural equations" (p. 124, §6.2.2), noting that it applies FE throughout — a useful negative citation. No JFNK or block preconditioners are described.

---

#### Antoci 2007 — Numerical simulation of fluid–structure interaction by SPH

**Relevance:** background  
**Status:** ✗ missing from bib

SPH particle-based FSI with simultaneous explicit updates, not a finite-volume, ALE moving-mesh, Newton-Krylov, PETSc, or block-preconditioned method.

---

#### Idelsohn 2008 — Unified Lagrangian formulation for elastic solids and incompressible fluids: App

**Relevance:** background  
**Status:** ✗ missing from bib

The method is fully Lagrangian (PFEM) rather than Eulerian, and is entirely FE/particle-based with no FV, no Newton-Krylov, and no block preconditioner. It is methodologically distant from the target paper. Could be cited briefly as a contrasting unified-continuum approach that avoids explicit fluid–solid interface coupling entirely.

---

#### Meduri 2017 — A partitioned fully explicit Lagrangian finite element method for highly nonline

**Relevance:** background  
**Status:** ✗ missing from bib

The paper is relevant as a highly nonlinear FSI method, but it is partitioned, fully explicit, Lagrangian PFEM/FEM, and commercial-software-based rather than monolithic, cell-centred FV, Newton-Krylov/JFNK, PETSc, or block-preconditioned. The filename uses 2017, while the PDF citation line gives International Journal for Numerical Methods in Engineering, 2018;113:43-64, with DOI 10.1002/nme.5602.

---

#### Roshchenko 2015 — A time splitting fictitious domain algorithm for fluid-structure interaction pro

**Relevance:** background  
**Status:** ✗ missing from bib

The key distinguishing feature relative to the target paper is that this method avoids all nonlinear (Newton/JFNK) solves by using a semi-implicit operator-splitting strategy that produces constant SPD matrices — explicitly trading spatial accuracy near the interface and time-step restrictions for solver simplicity. The paper explicitly notes this tradeoff (p. 111): "The relative ease of solving the present matrix problems come at a cost of possible time step restrictions due to the specific time-splitting algorithms mentioned above and sub-optimal spatial convergence rates in the vicinity of the fluid–structure interface inherent to the immersed methods." Uses FE not FV; immersed/fictitious domain not ALE; no block preconditioning.

---

#### Zarifian 2018 — Sloshing effects on supersonic flutter characteristics of circular cylindrical s

**Relevance:** background  
**Status:** ✗ missing from bib

Citation metadata in the PDF is an accepted-article version: first page says Int. J. Numer. Meth. Engng 2017; 00:1-26, while the file name and PDF creation date indicate 2018. Method is a linear FE coupled eigenvalue formulation, not a Newton-Krylov, JFNK, PETSc, cell-centred FV, or block-preconditioned FSI method.

---

### 3c. Possible Classification Mismatches (keyword heuristic)

Papers classified as *background* or *not relevant* but whose summary text contains Newton-Krylov, JFNK, block preconditioner, monolithic, or approximate Jacobian.

- **antoci2007** (Antoci 2007) — relevance: *background*
  Triggered keywords: newton-krylov, monolithic
  One-sentence summary: The paper presents a fully Lagrangian SPH formulation for FSI in which both fluid and solid phases are represented by particles.

- **idelsohn2008** (Idelsohn 2008) — relevance: *background*
  Triggered keywords: newton-krylov, jfnk, block preconditioner
  One-sentence summary: This paper presents a unified Lagrangian finite element framework in which both incompressible (or quasi-incompressible) Newtonian fluids and hypo-elastic solids are described by a single...

- **meduri2018** (Meduri 2017) — relevance: *background*
  Triggered keywords: newton-krylov, jfnk, monolithic
  One-sentence summary: The paper presents a fully explicit, fully Lagrangian partitioned FSI method for highly nonlinear transient problems with free surfaces and large structural deformation.

- **roshchenko2015** (Roshchenko 2015) — relevance: *background*
  Triggered keywords: jfnk
  One-sentence summary: This paper develops a mixed Eulerian–Lagrangian finite element fictitious domain method for incompressible fluid interacting with a hyperelastic incompressible solid.

- **zarifian2018** (Zarifian 2018) — relevance: *background*
  Triggered keywords: newton-krylov, jfnk, monolithic
  One-sentence summary: The paper develops a finite element fluid-structure interaction model for supersonic flutter of a circular cylindrical shell partially filled with liquid.
