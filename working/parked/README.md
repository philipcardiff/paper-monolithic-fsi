# Parked material

Material removed from the paper but kept so it can be put back.

- `sectionSupplementaryCases.tex`: the former appendix "Additional cases" (label `app:additional_cases`). It covered the solids4foam tutorials that have a quasi-monolithic variant but are not used in Sections 4–9: `mokLidDrivenCavity`, `beamInCrossFlow`, `membraneRoof`, `perpendicularFlap` and Hron–Turek FSI1.
  - **Removed:** 1 Nov 2026, on Philip's decision; Astra's referee review recommended deleting it.
  - **To put it back:** add `\input{working/parked/sectionSupplementaryCases.tex}` inside the `appendices` environment of `article.tex`. Restore the closing sentence of the case-overview paragraph in `sectionVerificationExact.tex` (it pointed to the appendix).
  - **Time scheme:** any results added for these cases must use BDF2. `mokLidDrivenCavity`, `membraneRoof` and `perpendicularFlap` default to Euler for the fluid `ddt(U)`.
