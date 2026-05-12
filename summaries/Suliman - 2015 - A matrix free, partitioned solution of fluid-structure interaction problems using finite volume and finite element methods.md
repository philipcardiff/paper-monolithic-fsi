---

## Suliman 2015 — Matrix-free partitioned FV-FE FSI

**Full citation:** Suliman, R., Oxtoby, O. F., Malan, A. G., Kok, S. A matrix free, partitioned solution of fluid–structure interaction problems using finite volume and finite element methods. European Journal of Mechanics B/Fluids, 49:272-286, 2015. DOI: 10.1016/j.euromechflu.2014.10.002

**BibTeX key suggestion:** suliman2015

**Discretisation (fluid):** vertex-centred FV

**Discretisation (solid):** vertex-centred FV / FE

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** fixed-point

**Preconditioner / linearisation:** N/A

**Test cases:**
- Dynamic piston-channel system
- Block-tail benchmark in first vibration mode
- Block-tail benchmark in second vibration mode
- Consistent versus lumped traction transfer at the interface
- Parallel speed-up for the block-tail problem

**Code released?** Elemental flow solver; not stated as open source

**One-paragraph summary (under 120 words):** This paper develops a matrix-free, strongly coupled partitioned FSI solver using an ALE incompressible fluid formulation discretised with an edge-based hybrid-unstructured vertex-centred finite volume method. The solid is treated either by an enhanced elemental/nodal-strain finite volume method or by Q8 finite elements, with both subdomains advanced by dual-timestepping. Coupling occurs at solver sub-iteration level by exchanging fluid tractions and solid velocities/displacements, avoiding a separate outer coupling algorithm while retaining independent fluid and solid solvers. The method is parallelised with METIS and MPI and validated on a dynamic piston-channel case and flexible block-tail benchmarks.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** "fully-coupled partitioned finite volume–finite volume and hybrid finite volume–finite element fluid–structure interaction scheme is presented" (p.1); "the fluid and structural domains are to be solved in a strongly-coupled partitioned manner" (p.2)

**Notes for the authors:** Coupling is at solver sub-iteration level and described as fully coupled, but the method remains partitioned rather than monolithic; no JFNK or block preconditioner is used.

---
