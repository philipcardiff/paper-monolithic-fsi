---

## Förster 2006 — Artificial added mass effect in staggered FSI algorithms

**Full citation:** Förster, C., Wall, W. A., Ramm, E. The artificial added mass effect in sequential staggered fluid-structure interaction algorithms. In: Proceedings of the European Conference on Computational Fluid Dynamics, ECCOMAS CFD 2006, P. Wesseling, E. Oñate and J. Périaux (Eds.), TU Delft, The Netherlands, 2006.

**BibTeX key suggestion:** forster2006

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** fixed-point

**Preconditioner / linearisation:** N/A

**Test cases:**
- Lid-driven cavity with thin flexible bottom wall (taken from Mok); varying structural density to probe instability onset
- Parametric study of different fluid time-integration schemes (BE vs BDF2) on the same cavity problem
- Parametric study of different structural predictors (zeroth, first, second order) on the cavity problem

**Code released?** not stated

**One-paragraph summary (under 120 words):** This conference paper analyses the artificial added mass instability inherent in sequentially staggered (loosely coupled) FSI algorithms applied to incompressible flow. A discrete representation of the added mass operator is derived in terms of fluid and structural mass matrices and the discrete gradient operator. Instability conditions expressed as critical fluid-to-structural mass ratios are derived analytically for various combinations of temporal discretisation schemes (backward Euler, trapezoidal rule, BDF2) and structural predictors. A key result is that schemes with "stationary" characteristics yield a constant instability limit, whereas schemes with "recursive" characteristics (e.g., trapezoidal rule) become unconditionally unstable after a finite number of steps regardless of parameters. Numerical confirmation uses a driven cavity with a flexible bottom wall.

**Relevance classification:** added-mass / FSI stability theory

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** This is a conference paper companion to the journal article by the same group (Förster, Wall, Ramm, submitted to CMAME 2006, reference [5] in the paper). That journal version likely contains the full derivation and should be sought. The key take-away for the monolithic/JFNK paper is that partitioned sequential staggered schemes are fundamentally limited by the fluid-to-solid density ratio — motivating monolithic or iteratively-staggered approaches. The driven cavity with flexible bottom used here is the Mok benchmark.

---
