# solids4foam learnings register (quasi-monolithic solver paper)

The solver-paper campaign keeps finding subtle choices in solids4foam, each one a fix, an option or a set-up detail, that change results. This register records each finding while it is fresh, for the quasi-monolithic (QM) coupling and for the partitioned runs it is compared with.

**Why it exists.** After the paper is submitted, each entry has to reach solids4foam in a robust form, so that a user who has not read the paper cannot pick the wrong option by accident. That means one of:

- a corrected default;
- a warning or a fatal error on the unsafe combination;
- a fixed tutorial;
- as a last resort, documentation.

The verification paper (paper-fsi-verification) keeps the matching register, `solids4foam_learnings.md` (pfv#105). Entries that affect both couplings are cross-referenced as **pfv N**. Entry 3 here is the full version of pfv 4 (interface viscous traction form), which the verification register assigns to the solver paper.

**How to add an entry.** Give it the next free number, and never renumber entries. Fill in every field, citing evidence by issue, PR, commit, run folder or paper section. Update the *State* field when solids4foam changes. Commits are solids4foam commits unless stated otherwise; "QM branch" is `feature-petsc-snes-quasi-monolithic` (PR #233).

**Status values** (as in the verification register):

- **Open:** nothing in solids4foam yet.
- **Tutorial only:** fixed in the affected tutorials; an uninformed user can still hit it in a new case.
- **Issue filed:** a solids4foam issue exists.
- **Robust:** a default, check or error in the code prevents it.
- **Done:** robust and documented.
- **Practice:** a working practice for runs and timings, not solids4foam code.

## Summary

| # | Topic | Area | Effect if wrong | Status |
|---:|---|---|---|---|
| 1 | Interface pressure condition, QM | interface | first-order added mass, extra damping (ring) | Open (warning only) |
| 2 | `movingWallPressure` in partitioned runs (pfv 3) | interface | enclosed-domain failure; 1/Δt sensitivity; IQN-ILS failure | Issue filed (#721) |
| 3 | Interface viscous traction form (pfv 4) | interface | O(1) traction error on a deforming wall | Robust (QM, #611/#618); Open (partitioned check) |
| 4 | Interface force at the current iterate | interface | amplitude loss per period ×12–15 (ring) | Robust (c008e8dd1) |
| 5 | Conservative vs interpolated traction transfer | interface | force imbalance on non-matching interfaces | Open (default off) |
| 6 | Mesh-motion interface faces from the points | interface | crushed cells at coarse-solid tips | Robust (#699) |
| 7 | Continuity flux from the convecting face flux (pfv 1) | discretisation | up to 0.5% (QM); 13% → 3% CFD3-like lift | Robust (QM, #597) |
| 8 | Non-orthogonal correction of the viscous wall flux | discretisation | O(tan θ) wall-flux error on skewed walls | Issue filed (#716) |
| 9 | Rank-deficient cubic stencils | discretisation | unstable root mode, 6–56% errors | Issue filed (#698) |
| 10 | Wall arcs on curved two-region meshes (pfv 11) | meshing | ~1 µm AMI wall mismatch | Tutorial only (#625) |
| 11 | Fluid/solid row scaling | solver settings | default 1 never used; s_S fixed at construction | Issue filed (#717) |
| 12 | PETSc options of the coupled solve | solver settings | 2–3× cost; LU dominates in 3-D | Tutorial only |
| 13 | Velocity-block preconditioner in large 3-D cases | solver settings | Krylov counts grow with the mesh (3-D tube) | Open (issue drafted) |
| 14 | Rhie–Chow stencil assembly | solver cost | insertion about 1/4 of the run time | Robust (a15366784) |
| 15 | Flux-switching outlets in a Newton solve | boundary conditions | first step fails or cycles (Hessenthaler) | Issue filed (#664, #675) |
| 16 | Ranks without fluid cells | parallel | hang in step 2 | Issue filed (#639, #653) |
| 17 | Coupling convergence test defaults (pfv 6, 7) | coupling | "strict test" claimed but not applied | Issue filed (#552, #710) |
| 18 | Tutorial defaults silently changing study set-ups | tutorials | wrong reuse or test in reruns | Open |
| 19 | Mesh motion on the FSI3 Gmsh meshes | mesh motion | folded cells with standard solvers | Open (until #233) |
| 20 | Mesh-motion predictor | mesh motion | folded cells, stalled Krylov solve | Tutorial only |
| 21 | Pseudo-solid on the previous-step mesh | mesh motion | different interior meshes between results | Done |
| 22 | Initial Poiseuille flow in copied cases (pfv 15) | tutorials | runs started from rest | Tutorial only (8ae03edaf) |
| 23 | Timings on a shared file system | HPC | elapsed 11–39% above CPU, 34% spread | Practice |
| 24 | Checkpoints and restarts at job time limits | HPC | lost steps; stale saves fill the file quota | Practice |
| 25 | Restart without its time state continues as a new run | restart | 2 Newton iterations per step instead of 1 after restart | Robust (#741, QM branch) |
| 26 | Timing protocols restarted from different flow states | HPC | QM Newton counts 2 vs 1 bias cost ratios | Practice |
| 27 | Region-by-region `decomposePar` drops `<time>/uniform` | restart | time index restarts from zero on a re-decomposed restart | Robust (#741, QM branch) |
| 28 | QM solvers ignore fvOptions | sources | body forces (gravity, MMS sources) silently dropped; inconsistent wall pressure | Robust (#751, QM branch) |
| 29 | QM interface pressure without the k·∇p non-orthogonal term | interface | first-order interface pressure and traction on tilting interfaces | Issue filed (#747) |
| 30 | Correction vectors from `patch().delta()` are zero on OpenFOAM.com | boundary conditions | non-orthogonal correction silently off (`newMovingWallVelocity`, `elasticWallVelocity`, others) | Issue filed (#748) |
| 31 | Δt-dependent error plateau in `newtonIcoFluid` | discretisation | temporal orders of p and traction stall below Δt ≈ 0.005 | Issue filed (#749); opt-in fix in PR #752 (entry 33) |
| 32 | `pimpleFluid` pressure order and outlet–wall corner in MMS | discretisation | first-order fluid pressure; L∞ dominated by the outlet corner | Issue filed (#750); `ddtCorr` implicated (entry 33) |
| 33 | Δt-consistent Rhie–Chow as the `newtonIcoFluid` default (pfv 16, 18) | discretisation | discrete problem depends on Δt: MMS plateau; coarse FSI3 drag −2.2% when Δt halves | Open (opt-in PR #752) |

## Interface conditions

### 1. Interface pressure condition, QM

- **Found:** October 2026, ringAddedMass (paper Section 4.4, "Interface pressure").
- **What goes wrong:** with a zero normal pressure gradient on the interface, the interface pressure and with it the added-mass force carry an error proportional to the wall acceleration and the wall-cell size. The ring frequency ratio converges at first order, and the amplitude loss per period exceeds that of the dry ring by 1.3/0.66/0.34% (moderate) and 2.3/1.2/0.65% (strong) on three meshes.
- **Evidence:** 3e93daef6 (second-order interface pressure); #594 (gradient set only for a plain `fixedGradient`); #618 (transpose term included in the gradient); paper Section 4.4 and Figure "ring pressure condition".
- **Right choice:** `fixedGradient` on the fluid interface pressure; the coupling sets the gradient from the normal momentum equation.
- **State:** Open. The coupling accepts any other type and prints only a warning ("only first-order accurate in space", `newtonQuasiMonolithicCouplingInterface.C`, pressure-type check).
- **Robust fix to consider:** a fatal error unless `allowFirstOrderInterfacePressure yes` is set, or set the gradient on any pressure patch type the coupling owns.

### 2. `movingWallPressure` in partitioned runs

Shared with **pfv 3**, which owns the entry; this entry adds the solver-paper evidence.

- **Found:** 17–19 Nov 2026, reruns of every partitioned comparison on build 9e6d1bfb2.
- **What goes wrong:**
  - **Viscous term missing:** the condition prescribes only the acceleration term, −n·a_wall, not the viscous part of the normal momentum equation.
  - **Enclosed domains:** ringAddedMass with Aitken or IQN-ILS stops in step 1 ("Continuity error cannot be removed by adjusting the outflow"): `pEqn.flux()` on the fixed-gradient patch is non-zero, so the wall flux drifts from the wall-velocity flux and nothing absorbs it.
  - **Small Δt:** on the half-cylinder (Re ≈ 1, IQN-ILS) the temporal study stalls; the changes in u_x(A) at the two smallest steps are 8.9×10⁻⁶ and 1.9×10⁻⁵ m (observed orders 2.04, 3.67, −1.07). With `requireAllResidualMeasures` the last order is 0.27; a 1e-8 coupling tolerance is not reached at Δt = 0.0625 s. This is consistent with the coupling error in the wall velocity entering the gradient as ε/Δt.
  - **Robustness:** on the collapsible channel (Δt = 0.00625 s, ρs/ρf = 1) IQN-ILS fails with a solid Newton divergence at t = 0.619 s; with zero gradient the same cell completes, with or without the initial flow (A/B runs).
  - **Coupling to `newMovingWallVelocity`:** the condition hard-casts the velocity patch to `newMovingWallVelocity`.
- **Evidence:** solids4foam#721 and its comment of 18 Nov; paper Sections 4.2, 5.2 and 6.2; runs in `claude-runs/prerun671` (Mac) and MeluXina `/project/home/p201287/philip/blob-mwp`.
- **Right choice in the paper:** for the Dirichlet–Neumann couplings (Aitken, IQN-ILS), `movingWallPressure` on open domains (collapsible channel, pulsatile tube, FSI3), and zero gradient on the enclosed ring, on the half-cylinder and on the Hessenthaler flap (level-1 check with `movingWallPressure`: tip deflection 16.25 against 16.31 mm). Robin–Neumann keeps its Robin condition (`elasticWallPressure`).
- **State:** Issue filed (#721: viscous term, enclosed domains, `refCast`, steady-state switch).
- **Robust fix to consider:** the #721 proposal; a steady-state switch, or zero acceleration when the ddt scheme is `steadyState`; evaluate or relax the acceleration so the coupling error is not amplified by 1/Δt.

### 3. Interface viscous traction form (pfv 4, owned here)

- **Found:** October 2026, womersleyTube and blobInTreacle, during the QM–partitioned comparison (`paper-data/a2_discretisation_differences.md`, D6).
- **What goes wrong:**
  - The QM coupling used to pass `rho*nuEff*snGrad(U)` = μ(∇u)·n. The Cauchy traction also has μ(∇u)ᵀ·n = μ∇(u·n) for constant n, which vanishes on a stationary no-slip wall but not on a deforming one. It is physical, does not vanish with h or Δt, and is about μωR/(Eh) of the pressure: 3.1×10⁻⁴ in the womersleyTube tutorial, which matched a refinement-independent QM wall offset against Robin–Neumann (phase −5.2×10⁻⁴ rad on m1 and −4.8×10⁻⁴ rad on m2 and m4).
  - Adding the transpose term naively introduced a first-order error on the stationary half-cylinder wall (steady u_x −2.34/−1.04/−0.44% from partitioned on x1/x2/x4), from two defects: the `fixedGradient` wall pressure gradient omitted the transpose term, and the wall value of the transpose stress came from the boundary value of `grad(U)`, whose tangential derivatives use adjacent-cell values.
  - Related rule (#583, rejected): the traction passed to the solid must be the fluid's own discrete wall flux; higher-order wall-shear corrections degrade the partitioned convergence.
- **Evidence:** #611 (transpose term in the residual and traction); #618 (always on; consistent wall pressure gradient; wall value n⊗q with q = ν((I − nn)·(G_s·n) − n tr G_s) from a least-squares surface gradient G_s; the `viscousStressTranspose` switch removed and ignored with a warning); paper Sections 3.3 and 4.5.3 (comparison with and without the transpose term).
- **Right choice:** the full Cauchy traction, evaluated as the momentum equation's discrete wall flux, with a wall value of the transpose stress that does not use adjacent-cell tangential derivatives.
- **State:** Robust for the QM coupling (#618). Open for the partitioned `pimpleFluid` traction `n & (-devReff)`: not yet checked whether its wall value of `dev2(T(grad(U)))` has the same defect as the pre-#618 QM evaluation.
- **Robust fix to consider:** one shared traction routine for both couplings, tested on the Womersley tube (deforming wall) and the half-cylinder (stationary wall).

### 4. Interface force at the current iterate

This is the "BDF2 velocity-solid added-mass damping" item.

- **Found:** October 2026, ringAddedMass.
- **What goes wrong:** the velocity solid averaged the stress at the previous and an extrapolated future time, and on the interface the previous-time half was the traction from two steps before (the old-time correction was written where it was never read). The interface force therefore lagged by one step, a damper of coefficient m_a ω² Δt: the ring lost 2.0/10.6/18.3% of its amplitude per period (weak/moderate/strong, 100 steps per period), against 0.17/0.71/1.26% with the stress and traction evaluated once, at the new time. Removing the lag from the centred scheme alone left a scheme without dissipation, in which a high-frequency mode grew in blobInTreacle; hence BDF2.
- **Evidence:** c008e8dd1 (velocity solid: BDF2 displacement, stress and traction at the new time); paper Section 4.4, last paragraph ("Although not shown here…"); comment block in `sectionVerificationExact.tex` (dcbe04505 → c008e8dd1).
- **Right choice:** the interface force enters the velocity solid at the current Newton iterate; the displacement is integrated with BDF2 from the velocity.
- **State:** Robust. The lagged path no longer exists.
- **Robust fix to consider:** none in code; keep a ring regression test on the amplitude loss.

### 5. Conservative vs interpolated traction transfer

- **Found:** October–November 2026, ringAddedMass with non-conformal interfaces (paper Section 4.4).
- **What goes wrong:** with traction interpolation on a curved non-matching interface, the two faceted surfaces differ, so the total force does not balance exactly. The imbalance is mostly geometric: a linear-geometry solid integrates over undeformed face areas, the fluid over the moved faces; it appears on a conformal interface too. The conservative transfer (f_S = −Wᵀ f_F) balances it to round-off. Neither transfer was systematically more accurate in the frequency ratio.
- **Evidence:** `conservativeTractionTransfer` (aae583301), default `false`; the coupling stops with a fatal error if a nonlinear-geometry solid's interface patch does not use the matching area convention (`useUndeformedArea`); paper Sections 3.3 and 4.4.
- **Right choice:** conservative transfer where the interface force balance matters (non-matching interfaces); interpolation where a comparison with a partitioned run that interpolates is wanted (FSI3, Hessenthaler).
- **State:** Open (default off; area convention guarded).
- **Robust fix to consider:** make the conservative transfer the default for non-conformal (AMI) interfaces, and report the force imbalance at start-up.

### 6. Mesh-motion interface faces from the points

- **Found:** November 2026, FSI3 high-order runs and Hessenthaler.
- **What goes wrong:** the face-to-face transfer of the interface displacement to the mesh motion was piecewise constant per solid face and inconsistent with the interface points, which crushed fluid cells at the tips of coarse solids.
- **Evidence:** #697 (issue), #699 (fix: faces set from the points by averaging); verified on FSI3 and Hessenthaler.
- **State:** Robust (#699, QM branch).

## Discretisation

### 7. Continuity flux from the convecting face flux (pfv 1)

- **Found:** October 2026, QM blobInTreacle, cavity and a CFD3-like rigid-plate comparison.
- **What goes wrong:** with `div(U) Gauss linear` the continuity residual is not built from the face flux that convects momentum; with `interpolate(U) skewCorrected linear` the convecting flux is then not solenoidal. The difference vanishes only where the skew correction does (for example on orthogonal, unskewed faces): blobInTreacle moved by up to 0.5% (coarse mesh), the cavity by 0.15% (u_y) and 0.20% (F_y), and the rigid-plate lift amplitude was 13% below `pimpleFluid` before and 3% after.
- **Evidence:** #597 (5a03c7ad8); `paper-data/a1_monolithic_study_inventory.md`, Section 0. For the QM–partitioned cavity comparison the paper uses linear interpolation in both (Section 4.5.2); pfv 1 is the partitioned counterpart (`flux(HbyA)` falling back to `default linear`).
- **State:** Robust for QM (continuity always from `interpolate(U) & Sf`). The interpolation itself (`skewCorrected linear` vs `linear`) is a case choice; the partitioned side is pfv 1.
- **Robust fix to consider:** use the same continuity-flux interpolation in both fluid models by default, so a QM–partitioned comparison does not depend on a scheme entry.

### 8. Non-orthogonal correction of the viscous wall flux

- **Found:** 17 Nov 2026, Philip's review of Section 3.3.
- **What goes wrong:** on fixed-value velocity patches the viscous boundary flux and `patchViscousForce` use (U_f − U_P)/(n·d) without the k = d − (n·d)n correction. The missing term, about tan θ times the tangential derivative, does not vanish under refinement on a deforming wall with persistently skewed wall cells. It is close to zero on the near-orthogonal ring and tube meshes used for the order studies.
- **Evidence:** solids4foam#716; paper Section 3.3. The pressure counterpart is entry 29 (#747).
- **State:** Issue filed (#716).
- **Robust fix to consider:** the #716 proposal (subtract (k·G_s)/(n·d) with the existing wall fit G_s), optional first, tested on a skewed near-wall Womersley mesh.

### 9. Rank-deficient cubic stencils

- **Found:** November 2026, high-order velocity solid on thin structures (collapsible-channel wall, FSI3 flag).
- **What goes wrong:** with `polynomialOrder 3` and two or three cells across the thickness, the cubic fit through the cell centres is undetermined across the thickness (condition numbers 5×10¹⁷–1.4×10¹⁹ on 54×3; 1.5×10³–1.6×10⁴ on 108×6). It is accepted silently and gives an unstable root-corner mode: the order-3 80×2 wall stops at t = 0.28 s, the 54×3 flag completes only with ten-times larger stabilisation and errors of 6–56%.
- **Evidence:** solids4foam#698 (the class is the moving least-squares reconstruction; correction comment posted on the issue); paper Appendix C.
- **State:** Issue filed (#698).
- **Robust fix to consider:** compute the stencil condition number at set-up and stop (or fall back to a lower order) above a threshold, with a message giving the minimum cells across.

### 10. Wall arcs on curved two-region meshes (pfv 11)

See **pfv 11**. The solver paper's 3-D tube uses the corrected meshes for both couplings; a 1 µm mismatch moved c_p by up to 0.7% in preliminary runs (paper Section 6.4). State: Tutorial only (#625, 9b52c2303).

## Solver settings and cost

### 11. Fluid/solid row scaling

- **Found:** 17 Nov 2026, Philip's review of Section 3.4.
- **What goes wrong:** `fluidSystemScaleFactor` defaults to 1, but every `.monolithic` tutorial and every paper run sets 1e8; the value appeared in ccb225bef ("Scale fluid equations for conditioning") and was never derived or studied. The solid factor s_S = gAverage(1/(μΔt)) is a `const` computed at construction, so it is not updated when Δt changes.
- **Evidence:** solids4foam#717; `newtonQuasiMonolithicCouplingInterface.C` (constructor); paper Section 3.4 and Table B2.
- **State:** Issue filed (#717).
- **Robust fix to consider:** default 1e8 (or a dimensional estimate), a study of s_F from 1e6 to 1e10, and recomputing s_S when Δt changes.

### 12. PETSc options of the coupled solve

- **Found:** October–November 2026, beamInCrossFlow, 3-D tube, Hessenthaler.
- **What goes wrong:** the cost depends strongly on options that are not defaults:
  - a linear tolerance (`ksp_rtol`) of 1e-3 instead of 1e-4 for every linear solve, motivated by the first Newton iteration being limited to about 1e-3 by the nonlinearity; Jacobian and preconditioner rebuilt every 8 Newton iterations across steps (safe with `snes_mf_operator`), full Schur factorisation and the basic line search: beamInCrossFlow 149 → 64 s, 3dTube (100 steps) 299 → 103 s, same results (873a8d0e4);
  - the replicated (redundant) LU solid block dominates the cost on the finer 3-D meshes; one BoomerAMG V-cycle replaces it in the 3-D tube (paper Section 6.4.3);
  - BoomerAMG instead of LU for the fluid mesh motion, rebuilt every 20 steps (873a8d0e4);
  - `snes_stol` acts on a mixed-unit vector; check that runs terminate on `rtol` (`a2_discretisation_differences.md`, recommendation 4).
- **Right choice:** the settings of Table B2 and the coupling README; BoomerAMG rather than LU for 3-D solid blocks.
- **State:** Tutorial only (per-tutorial `petscOptions` files).
- **Robust fix to consider:** documented 2-D and 3-D option templates selected by dimension; a warning when the redundant LU solid block is used above a cell count.

### 13. Velocity-block preconditioner in large 3-D cases

- **Found:** November 2026, Hessenthaler Phase I (paper Section 6.3) and the 3-D tube (Section 6.4).
- **What goes wrong:** with the block-Jacobi ILU(0) velocity block, the Krylov iterations per Newton iteration grow with the mesh on the 3-D tube (18 on level 2, 27 on level 3, same state), and each Newton iteration costs 3–5 coupling iterations on FSI3 and about 4 on the Hessenthaler flap. The settings were not optimised for these cases.
- **Correction (20 Nov 2026):** this entry first cited a doubling between Hessenthaler levels 1 and 2 (38 → 81) and QM costs of 2.0–7.6× IQN-ILS. Those level-2 timings were restarted at t = 15 s, while the flap still moved, and re-decomposed without the time state (entry 27). Timed at the same steady state, QM level 2 needs one Newton iteration with 18 Krylov iterations and costs 0.92–1.08× IQN-ILS; level 1, whose flap keeps oscillating, needs two with 38 and costs 1.9×.
- **Evidence:** paper Sections 6.3, 6.4 and 6.5; `paper-data/hessenthaler/timing.csv`; `paper-data/tube3d_scaling_rerun/`. The FSI3 test with the Newton fluid inside IQN-ILS (paper Section 6.1, #100) shows the cost gap against PIMPLE comes from the coupled fluid solve, not the coupling.
- **State:** Open. An issue ("Quasi-monolithic coupling: optimise the linear solver and preconditioner for large 3-D cases") is drafted but not filed.
- **Robust fix to consider:** compare BoomerAMG/GAMG, ASM or ILU(k) for the velocity block and SIMPLE-type, PCD or LSC Schur approximations, under a fixed timing protocol; make the winner the 3-D template (entry 12).

### 14. Rhie–Chow stencil assembly

- **Found:** October 2026, beamInCrossFlow profiling.
- **What goes wrong:** the div(interpolate(grad p)) wide stencil was inserted with full blockSize × blockSize blocks holding one non-zero, so 3-D insertion added 15 explicit zeros per coefficient. Insertion took about a quarter of the run time and padded the stored matrix.
- **Evidence:** a15366784 (#599): beamInCrossFlow 278 → 149 s, 3dTube (100 steps) 503 → 299 s, same results.
- **State:** Robust.

## Boundary conditions, parallel runs and coupling tests

### 15. Flux-switching outlets in a Newton solve

- **Found:** November 2026, Hessenthaler with the QM coupling.
- **What goes wrong:** `inletOutlet` re-evaluates its switch from the current flux in every residual evaluation, so while outlet fluxes are near zero (inflow ramp from rest) faces flip between fixed value and zero gradient between Newton iterations. The residual is non-smooth and Newton cycles: the first step took 12–32 iterations or failed (about 1 run in 3).
- **Evidence:** solids4foam#664 (workarounds: `zeroGradient`, or a lagged `codedMixed` switch on the old-time flux; both gave 2 iterations per step); #675/#676 (`backflowStabilisedOutletVelocity`, β = 0.2, used by every Hessenthaler run in the paper, QM and partitioned). #676 is open; the `hessenthalerFsi` tutorial on the QM branch still uses `inletOutlet`.
- **State:** Issue filed (#664, #675; PR #676 open).
- **Robust fix to consider:** freeze flux-switching conditions during each SNES solve, or a lagged `inletOutlet`; merge #676 and use it in the Hessenthaler tutorial.

### 16. Ranks without fluid cells

- **Found:** November 2026, 3-D tube level 2, 32 ranks, Scotch decomposition.
- **What goes wrong:** a rank with no fluid cells hangs in step 2, consistent with a collective inside the wall-fit rebuild that the fluid-empty rank skips.
- **Evidence:** solids4foam#639 (comment of 17 Nov), #653; 2a1de06d6 (reduce the wall-fit rebuild decision across processors, on the QM branch), which should fix it; a retest has been requested.
- **State:** Issue filed (#639 and #653 open).
- **Robust fix to consider:** after the retest, either close or add a check in `decomposeParMonolithic`.

### 17. Coupling convergence test defaults (pfv 6, 7)

See **pfv 6** (default test accepts unconverged steps, #552) and **pfv 7** (strict test stalls at a true steady state, #710). Solver-paper evidence:

- The half-cylinder IQN-ILS runs were described as using the strict test but did not: the case has no `requireAllResidualMeasures`, the default is off, and 55 steps of the finest time-study run passed on one measure only (paper corrected in #108).
- Partitioned Hessenthaler level 3: the strict test stalls near steady state (22.8 coupling iterations per step over t = 40–45 against about 4 before t ≈ 35).

**State:** Issue filed (#552, #710).

### 18. Tutorial defaults silently changing study set-ups

- **Found:** 17 Nov 2026, partitioned reruns on build 9e6d1bfb2.
- **What goes wrong:** set-up scripts that add an option only when it is missing inherit changed tutorial defaults. The ring tutorial changed to IQN-ILS `couplingReuse 5` (bbf7d6f3a, #587), so reruns intended as "no reuse" ran with reuse 5 (iterations 5.3 → 3.1). A rerun that relied on the tutorial's coupling test instead of the strict test changed the Robin–Neumann iterations from 46.5/37.3/11.7 to 28.8/18.7/10.0.
- **Evidence:** `claude-runs/prerun671` (`runs/old-reuse5/`, `ring_accuracy_runs_nonstrict_table2.csv`); paper Table 2.
- **Right choice:** study scripts set every coupling option explicitly (tolerance, residual measures, reuse, relaxation, predictor).
- **State:** Open (practice in the paper scripts).
- **Robust fix to consider:** print the effective coupling settings in one block at start-up, so a log shows what was used; verification drivers compare it against the intended set-up.

## Mesh motion

### 19. Mesh motion on the FSI3 Gmsh meshes

- **Found:** 17 Nov 2026, preparing the shared partitioned FSI3 runs.
- **What goes wrong:** on the solver paper's three-level Gmsh family, the standard OpenFOAM mesh-motion solvers folded cells between t = 25.7 and 26.0 s in replay tests, so the solid-model (pseudo-solid) mesh motion is needed. Development 206437983 (#671) cannot run that mesh motion with the paper's settings: it lacks the PETSc SNES option, and the QM branch's mesh-motion coupler stops with a fatal error for a motion model without PETSc SNES. With a GAMG solver it runs, at about 21 s instead of 4 s per step.
- **Evidence:** board comment of 17 Nov (paper-monolithic-fsi PR #13); `simulationData/fsi3-gmsh-meshes/README.md`; shared runs on 9e6d1bfb2 (QM branch merged with #671).
- **State:** Open until the QM branch (PR #233) reaches development. #690 (QM mesh motion with OpenFOAM motion solvers) was merged into the QM branch on 20 Nov.
- **Robust fix to consider:** merge #233; a start-up check of mesh quality after the first motion solve.

### 20. Mesh-motion predictor

- **Found:** October 2026, collapsibleChannel, blobInTreacle and cavityFlexibleBottom (QM, nonlinear pseudo-solid).
- **What goes wrong:** without a predictor, the first iterate of each mesh-motion solve carries the whole interface increment in the cells next to the interface; once it exceeds about half their height they fold, the tangent becomes much stiffer than the lagged preconditioner and the Krylov solve stagnates (collapsibleChannel fails at t = 0.3 s).
- **Evidence:** 2f210622b, bf72e7d65, cf2766830 (#626); paper Section 5.2 ("Mesh motion" note). The predictor comes from the pseudo-solid schemes (`ddt(D) backward`, `d2dt2(D) steadyState`), so it is a linear extrapolation; an earlier draft called it a second-order Taylor predictor.
- **State:** Tutorial only.
- **Robust fix to consider:** enable the predictor by default for the mesh-motion solid models, or warn when the mesh-motion solve starts from the old displacement.

### 21. Pseudo-solid on the previous-step mesh

- **Found:** 17 Nov 2026, Philip's review of Section 3.6.
- **What goes wrong:** some results assembled the pseudo-solid on a stored copy of the initial mesh (the pulsatile tube, the ring pressure-condition study and the robustness maps), others on the previous step's mesh with the total displacement from the initial points (the default since a60a5d9b8 / 38954ce2b, 17–18 Oct). The interior meshes differ, so results from the two paths are not identical; the commit date alone does not tell which a run used.
- **Evidence:** a60a5d9b8, 38954ce2b; paper Section 3.6 (which results used the copy).
- **State:** Done (one path in the code; the paper states which results used which).

## Tutorials and set-up

### 22. Initial Poiseuille flow in copied cases (pfv 15)

- **Found:** 17 Nov 2026, collapsible-channel reruns.
- **What goes wrong:** in cases copied outside the solids4foam tree without `SOLIDS4FOAM_ROOT`, `wmake setPoiseuilleFlow` failed and the old `Allrun` carried on, so every map run in the solver paper before 17 Nov (80 partitioned, 47 QM) started from rest. They were rerun with the initial flow (paper PR #106). With the initial flow, every partitioned trough is about 0.20% deeper and closer to oomph-lib; six map cells changed status, partly from this.
- **Evidence:** 8ae03edaf (Allrun stops if `wmake setPoiseuilleFlow` fails to compile; a failure when running the utility is not checked); board comment of 17 Nov; paper PR #106.
- **State:** Tutorial only.
- **Robust fix to consider:** the solver checks the initial field against the expected profile, or the utility is built with the library rather than per case.

## HPC practice

### 23. Timings on a shared file system

- **Found:** November 2026, 3-D tube strong scaling.
- **What goes wrong:** with case files on the shared Lustre file system, the elapsed time exceeded the CPU time by 11–39% and repeats spread by up to 34%. With the case in node-local memory and nothing written in the timed window: 6–12% and below 7% (15% for one case).
- **Evidence:** `paper-data/tube3d_scaling_rerun/README.md` (#104); paper Sections 4.0 (protocol) and 6.4.2.
- **State:** Practice.
- **Robust fix to consider:** a timing script template in the verification drivers that runs from node-local storage.

### 24. Checkpoints and restarts at job time limits

- **Found:** November 2026, Hessenthaler QM level 3 and FSI3 level 3 on MeluXina.
- **What goes wrong:** a job killed at its time limit loses everything since the last write. After a restart, `purgeWrite` purges only the new job's writes, so the restart time folder of each earlier job stays and fills the project file quota (about 10 000–20 000 files per stale save at 128–256 ranks).
- **Right choice:** `--signal=USR1@1800` with `OptimisationSwitches { stopAtWriteNowSignal 10; }` and a write interval the run reaches well before the limit; delete stale restart saves after each restart.
- **State:** Practice (OpenFOAM and Slurm behaviour, not solids4foam code).
- **Robust fix to consider:** a restart-safe job-script template in the tutorials' HPC notes.

## Restarts

### 25. Restart without its time state continues as a new run

- **Found:** 20 Nov 2026, Hessenthaler level-2 QM timing runs, reported by the verification coordinator; diagnosed the same day (solids4foam #740).
- **What goes wrong:** restarting the QM run from its saved t = 45 state did not reproduce the continuous run: each of the first 130 steps after the restart needed two Newton iterations, against one in the continuous run, after a first-step residual of 41.7 against 0.050, decaying to a plateau of 0.11.
- **Cause:** not the QM restart itself. The timing case was re-decomposed region by region, which drops `<time>/uniform/time` (entry 27), so the run started with time index 0. Several solids4foam paths decide "restart or not" from `startTimeIndex() > 0` and took the branch of a new run:
  - Euler weights in the velocity solid's first step (`backwardDeltaT0`);
  - the mesh-motion solid's restart fields not read (`readRestartField`);
  - the mesh-motion stiffness scale factor recomputed on the deformed mesh;
  - the constitutive state not read.
- **Evidence:**
  - Same-decomposition restarts are seamless: the production rF1 restart at t = 20, and TurekHron2006 monolithic at `writePrecision 16`, where the norms match to 1e-9.
  - The 64- and 128-rank re-decomposed restarts give identical norms (31.0407 at t = 15.002), so the effect does not depend on the decomposition.
  - Copying `<time>/uniform` into the processor directories restores the continuous behaviour.
  - Details in #740; MeluXina jobs 5476389/90.
- **State:** Robust on the QM branch. #741 was merged into `feature-petsc-snes-quasi-monolithic` on 20 Nov 2026 (3bc38e401) and #740 closed. `solids4Foam` now stops with an error when the start time holds old-time fields but no `uniform/time`, and `TurekHron2006/restartTest.sh` runs in its regression test. It reaches development with PR #233.
- **Robust fix to consider:** beyond the check, stop deciding "restart or not" from the time index in the models.

### 26. Timing protocols restarted from different flow states

- **Found:** 20 Nov 2026, Hessenthaler timing runs.
- **What goes wrong:** QM Newton counts fall from two to one per step as the flow approaches a steady state (and entry 25 changes them again after a restart), so timing windows started from different flow states, or from a restart against a continuous run, bias the QM/partitioned cost ratio. On the Hessenthaler level 2, QM timed from t = 15 s (and without its time state) against IQN-ILS at the steady state gave a ratio of 6.0; both at the steady state with the time state restored give 0.92 (64 processes).
- **Right choice:** restart both couplings from the same flow state and time window, record the Newton or coupling iterations per step in the timed window, and compare them with the production runs.
- **State:** Practice.

### 27. Region-by-region `decomposePar` drops `<time>/uniform`

- **Found:** 20 Nov 2026, audit of the paper's timing restarts after entry 25.
- **What goes wrong:**
  - `decomposePar` copies or links the top-level `<time>/uniform` (`uniform/time`: time index, `deltaT0`) only when several regions are decomposed in one call (OpenFOAM v2512 `decomposePar.C`, `regionNames.size() > 1`). It links rather than copies unless `-copyUniform` is given, so deleting the reconstructed `<time>` afterwards also loses it.
  - `decomposePar -region fluid` and `-region solid`, run one after the other, therefore leave the processor directories without `uniform/time`. `decomposeParMonolithic` does not copy it either.
  - The restarted run continues as a new run (entry 25).
  - `-allRegions` fails on solids4foam cases, which have no `regionProperties`; `-regions '(fluid solid)' -copyUniform -time <time>` works.
- **Evidence (audit, 20 Nov 2026):**
  - **Affected:** every Hessenthaler timing that changed the process count (QM rF1, all IQN-ILS), now re-timed with `uniform/time` restored.
  - **Affected, effect within the repeat spread:** the 3-D tube strong-scaling rerun with more than one process, both couplings (`paper-data/tube3d_scaling_rerun/README.md`).
    - QM: Newton unchanged; Krylov iterations 5–13% higher for the first 10 steps.
    - Robin–Neumann: +3 coupling iterations at step 1 (excluded) and +1–2 at step 2.
    - Estimated effect on the times: at most about 2%.
  - **Not affected:** the FSI3 timings (production processor directories symlinked), the newton-partitioned test, and the ring and half-cylinder timings (whole runs from t = 0).
- **Right choice:** decompose all regions in one call with `-copyUniform`, or copy `<time>/uniform` into each `processor*/<time>/`, and check that `processor*/<time>/uniform/time` exists before a restart.
- **State:** Robust on the QM branch: #741 (merged 20 Nov 2026, 3bc38e401) makes `solids4Foam` stop with an error in this situation. Reaches development with PR #233.
- **Robust fix to consider:** a solids4foam decomposition helper that always decomposes all regions together and copies `uniform`; `decomposeParMonolithic` copying `uniform`.

## Manufactured-solution FSI case

The entries below come from the manufactured-solution (MMS) FSI case built on 20–21 Nov 2026 (`claude-runs/mms-fsi`, README there).

- **Case.** A 2-D channel with a compliant neo-Hookean wall, an exact ALE solution and an exact interface traction, with no interface source term.
- **Variants.** "Full": the interface tilts by up to 13° against the mesh. "Flat": the interface stays flat, so the ALE mesh stays orthogonal.

### 28. QM solvers ignore fvOptions

- **Found:** 20 Nov 2026, while setting up the MMS case.
- **What goes wrong:**
  - **`newtonIcoFluid`:** `fluidModel` builds and reports `fvOptions`, but `newtonIcoFluid` never applies them. They are missing from the momentum residual.
  - **Wall-normal balance:** the balance that sets the `fixedGradient` wall and interface pressure gradient has no body-force term.
  - **Velocity solid:** its fvOptions line is commented out and would not compile (`ds_` is not a member).
  - **Consequence:** any body force is silently dropped in QM runs, and fixing only the residual would leave the wall and interface pressure inconsistent with it.
- **Evidence:** solids4foam#746 (specific case of #508, #221); MMS README §4.
- **Right choice:** apply `fvOptions(U) & U` in the residual and in the normal balance, and `fvOptions(rho, U) & U` in the velocity solid. This is prototyped and gives second order in the orthogonal-mesh MMS variant.
- **State:** Robust on the QM branch. #751 merged 21 Nov 2026 (db3039b76), #746 closed. The regression tutorial `quasiMonolithicBodyForce` checks the hydrostatic pressure. A non-zero `constant/fluid/g` is still ignored by `newtonIcoFluid` (#508). Reaches development with PR #233.
- **Robust fix to consider:** a regression check that a uniform body force gives the hydrostatic pressure in a QM case. More generally, the #508 rule: a configured option that no equation applies should be reported.

### 29. QM interface pressure without the k·∇p non-orthogonal term

- **Found:** 21 Nov 2026, MMS case, full variant.
- **What goes wrong:**
  - The `fixedGradient` interface pressure sets p_b = p_P + g (n·d) and drops k·∇p_P, where k = (I − nn)·d.
  - The mesh motion moves the cells next to a tilting interface almost along fixed columns, so k = O(h) persists under refinement.
  - The interface pressure and traction are therefore first order, and the solid loses order through the traction.
- **Evidence:**
  - solids4foam#747.
  - At n128, k·∇p_exact = 5.49e-3 against a measured interface p error of 5.28e-3 (correlation 0.96). The reconstruction with exact p_P and exact g gives exactly 5.49e-3.
  - Spatial orders at Δt = 0.000625, n64 to n128:

    | quantity | full variant | flat variant |
    |---|---|---|
    | interface traction | 1.11 | 1.67 |
    | solid D | 1.37 | 2.17 |

  - A boundary-value-only fix (`fixedGradientCorrected` with a consistently evaluated gradient) excites a near-wall mode and makes U worse by about 50%.
- **Right choice in the paper:** the ring and tube meshes are near-orthogonal at the interface, so the term is close to zero there. Check this for any case whose interface tilts relative to the mesh (collapsible channel, FSI3, Hessenthaler).
- **State:** Issue filed (#747); a consistent fix (wall value, Rhie–Chow wall flux and wall-cell gradient) is being prototyped.
- **Robust fix to consider:** the consistent correction, or at least a warning when the interface non-orthogonality exceeds a threshold.

### 30. Correction vectors from `patch().delta()` are zero on OpenFOAM.com

- **Found:** 21 Nov 2026, Fable review of the MMS case; confirmed in the code.
- **What goes wrong:**
  - Several conditions compute k = (I − nn)·`patch().delta()`.
  - On OpenFOAM.com, `fvPatch::delta()` is purely normal for non-coupled patches, so k ≡ 0 and their non-orthogonal correction does nothing.
  - Affected: `newMovingWallVelocity`, `elasticWallVelocity`, `normalInletVelocity`, `paraboloidInletVelocity`, `solidSymmetry`, `normalDisplacement`, `tractionPressureDisplacement`, `fixedTemperature`.
  - `patchCorrectionVectors()` (Cf − Cn) is correct.
- **Evidence:** solids4foam#748; v2512 `fvPatch.C`.
- **Right choice in the paper:** none needed for the near-orthogonal interfaces. For the partitioned runs on tilting interfaces, the interface viscous flux and traction are uncorrected whatever the condition claims.
- **State:** Issue filed (#748).
- **Robust fix to consider:** use `patchCorrectionVectors()` everywhere, and update the regression references.

### 31. Δt-dependent error plateau in `newtonIcoFluid`

- **Found:** 21 Nov 2026, MMS temporal study (n32 mesh, Δt 0.04 → 0.00125).
- **What goes wrong:**
  - The differences between successive-Δt solutions converge at second order for the solid down to Δt ≈ 0.005.
  - Below that they stall or grow for the interface traction (−0.28 and −0.54 for the two variants) and the fluid pressure.
  - The plateau is about 3–5e-3, against a spatial error of about 1e-2 at n32.
- **Evidence:**
  - solids4foam#749.
  - Tight tolerances (snes_rtol 1e-13, ksp_rtol 1e-10) change nothing.
  - A Rhie–Chow scale factor of 4 reduces the plateau by about 50% but does not remove it. A Rhie–Chow coefficient that scales with Δt is suspected.
- **Right choice in the paper:**
  - Run spatial studies at a fixed small Δt and temporal studies on a fixed mesh. Refining h and Δt together mixes partly cancelling errors.
  - Check whether the paper's temporal orders for the pressure and traction come from Δt below the plateau.
- **State:** Issue filed (#749). Cause found (the Rhie–Chow coefficient ∝ Δt) and fixed as an option in PR #752; see entry 33.
- **Robust fix to consider:** a pressure stabilisation independent of Δt, or a Rhie–Chow coefficient without the 1/Δt dependence, verified on the MMS case. Entry 33 records the chosen fix.

### 32. `pimpleFluid` pressure order and outlet–wall corner in MMS

- **Found:** 21 Nov 2026, MMS case, Aitken and Robin–Neumann couplings (n16 to n64).
- **What goes wrong:**
  - The fluid pressure is first order in the whole domain: about 1.0, also with the outlet region excluded.
  - The mean pressure offset does not halve with h.
  - The velocity L∞ is dominated by the cell column at the outlet–bottom-wall corner, with orders 0.4–0.8.
  - The solid D is still second order.
  - QM on the same meshes has a pressure order of 1.7–2.1 and no corner outlier.
- **Evidence:** solids4foam#750; MMS README §5.4.
- **Right choice in the paper:** when the pressure-type accuracy of the two couplings is compared, separate coupling effects from this `pimpleFluid` effect.
- **State:** Issue filed (#750). `pimpleFluid`'s `ddtCorr` term accounts for much of it (entry 33): with `ddtCorr no`, the n64 pressure error falls by 2.4× and its order rises to 1.5–1.7. This is not yet separated into spatial and temporal parts. Other candidates remain: the boundary condition set-up (#748), and the Dirichlet-p/Neumann-U outlet next to a `fixedFluxPressure` wall.
- **Robust fix to consider:** depends on the cause.


### 33. Δt-consistent Rhie–Chow as the `newtonIcoFluid` default (pfv 16, 18)

- **Found:** 21 Nov 2026. Follow-up to entry 31 on the MMS case, checked on the ring, FSI3 and blobInTreacle.
- **What goes wrong:**
  - **Coefficient ∝ Δt.** The default Rhie–Chow coefficient of `newtonIcoFluid` is `−interpolate(1/A)`, where A includes the transient diagonal c/Δt. For small Δt it is ∝ Δt, so the discrete problem that time integration converges to depends on Δt. This causes the plateau of entry 31.
  - **FSI3.** On the coarse tutorial mesh, halving Δt from 1e-3 to 5e-4 moves the drag from 7.674 to 7.502 (−2.2%) and the uy amplitude from 20.89 to 20.34 mm.
  - **Steady coefficient breaks the ring.** Dropping the ddt term from the coefficient removes the plateau but breaks the ring (amplitude loss 21% per period, wet/dry ratio −0.42%, Newton 3.9 per step) and TurekHron (forces 12%). The reason is that 1/a_spatial is unbounded for a nearly inviscid, slow flow.
- **Evidence:**
  - solids4foam#749 (diagnosis and comments) and PR #752 (implementation, all tables); `claude-runs/mms-fsi` PROGRESS.md and `case/runs/rc/`.
  - **MMS temporal study, n32, Δt 0.04 → 0.00125.** Final-pair orders, default → time history:

    | quantity | tilting interface | flat interface |
    |---|---|---|
    | fluid p | 0.05 → 1.64 | −0.10 → 1.83 |
    | interface traction | −0.28 → 1.92 | −0.54 → 1.98 |
    | solid D | 1.60 → 2.00 | 0.36 → 1.99 |

  - **Ring, all levels, history on.** All 9 checks pass; strong level: ratio −0.009% (default −0.004%), loss 0.070% (0.049%) per period, Newton 2.00.
  - **blobInTreacle.** Changes ≤ 3.4e-5.
  - **FSI3, history on.** Drag 8.520 and 8.521, uy amplitude 25.55 and 25.54 mm at Δt 1e-3 and 5e-4: independent of Δt to about 4 digits.
  - **Restart.** Serial matches to 10 digits; parallel to 6e-8.
- **Right choice:** the Choi (1999) / Cubero and Fueyo (2007) time-history correction.
  - **Flux.** φ = interpolate(U)·Sf − γ|Sf|B + γ|Sf|(c0 wⁿ − c00 wⁿ⁻¹)/Δt, with w the accepted face-normal correction of each step.
  - **Coefficient.** γ = 1/(interpolate(a_P) + c/Δt): interpolate the spatial diagonal first, then invert. Then a converged steady state, w = −B/a_f, is exactly independent of Δt.
  - **No limiter.** OpenFOAM's `ddtCouplingCoeff`-style limiter on the history brings the plateau back: tilting-interface traction order 1.92 → 0.80, p 1.64 → 0.56, U 0.92 → 0.05; flat traction 1.98 → 1.25.
- **Relation to `ddtCorr` in `pimpleFluid` (pfv 16, 18).**
  - **What is shared.** `pimpleFluid` adds `interpolate(rAU)*fvc::ddtCorr(U, phi, Uf)`, on by default. It is the same history quantity, with the same backward weights and the same Euler first step.
  - **Coefficient.** `interpolate(rAU)` interpolates a reciprocal, so a `pimpleFluid` steady state is only approximately Δt-independent. This is the residual Δt dependence of pfv 16.
  - **Limiter.** The default limiter is `1 − min(|δφ|/|φ|, 1)`.
  - **ALE form.** On a moving mesh it is the Uf form, the vector history projected on the current Sf.
  - **Restart.** OpenFOAM writes `phi_0` only.
  - **In the partitioned MMS runs** (Aitken, combined refinement n16–n64), `ddtCorr` accounts for much of pfv 18 / entry 32:

    | setting | p L2 at n64 (orders) |
    |---|---|
    | default | 1.82e-2 (0.88, 0.94) |
    | `backward 1`, no limiter | 2.33e-2 (1.13, 1.40) |
    | `ddtCorr no` | 7.50e-3 (1.73, 1.49) |

    Over the same runs, the velocity L∞ falls from 8.07e-2 to 2.39e-2 with `ddtCorr no`.
  - **What this means for the partitioned side.** The limiter is not the cause there. `ddtCorr no` is not a recommendation until fixed-Δt and fixed-mesh studies separate the parts.
- **BDF-q caveat.**
  - **What #752 supports.** The correction must use exactly the weights the ddt scheme applies to U. #752 supports `backward`, `Euler` and `BDF 1`, and stops with an error for `BDF 2` to `6` (298ec4852). Mapping `BDF 2` to `backward` would differ on restart (Astra review).
  - **What BDF-q would need:**
    - q history levels, written for restart;
    - the scheme's effective weights and start-up ramp, which are private in `bdfDdtScheme`;
    - on moving meshes, #674.
  - **OpenFOAM's `ddtCorr`.** `bdfDdtScheme` (#629) implements `ddtCorr` for vector U up to q = 6, with the same limiter. #674 leaves it unchanged on moving meshes. The interaction is flagged on #674.
- **Right choice in the paper:**
  - The QM results use the default coefficient. The ring and the half-cylinder are insensitive to the switch (above).
  - The paper's FSI3 QM runs (fine meshes, Δt 1–2e-4) were already insensitive to Δt: qm_2 drag 461.113 against 461.119. They have not been rerun with the history.
  - Temporal orders of p and traction measured with the default coefficient should be checked against the plateau (entry 31).
- **State:** Open. PR #752 (`RhieChowTimeHistory yes`, opt-in, off by default) is open and not merged. Philip's view (21 Nov 2026) is that it should become the default, probably not disableable. Two checks come first:
  - a Mac-sized mesh-refinement comparison: FSI3 at two levels and two Δt, and the collapsible channel;
  - a CI arm with the option on: the TurekHron `restartTest.sh`, blobInTreacle, and possibly a short MMS temporal check.
- **Robust fix:**
  - Make the time-history correction the `newtonIcoFluid` default and remove the keyword. Alternatively, keep only a regression switch, named for its purpose (for example `legacyRhieChowCoefficient`), that prints a warning. Update the regression references once.
  - Keep the FatalError for ddt schemes without matching weights, until a BDF-q version exists.
  - For `pimpleFluid`, a separate decision once its `ddtCorr` effect is isolated: the Δt-consistent coefficient and no limiter there too, or a documented default.
