# Method sections against the solids4foam code

Audit of `sectionMathModel.tex` (Section 2) and `sectionNumericalModel.tex`
(Section 3, with Algorithms 1-2 and `figures/tikz/*.tex`) against solids4foam
`origin/feature-petsc-snes-quasi-monolithic` at `fdcc397e2` (includes #581,
#610, #611, `viscousStressTranspose` default `no`). Code was read with
`git show fdcc397e2:<path>`; line numbers refer to that commit.

Abbreviations for code paths (all under `src/solids4FoamModels/` unless
stated):

- NIF: `fluidModels/newtonIcoFluid/newtonIcoFluid.C`; NIH: `.H`;
  NIR: `fluidModels/newtonIcoFluid/README.md`
- QMC: `fluidSolidInterfaces/newtonQuasiMonolithicCouplingInterface/newtonQuasiMonolithicCouplingInterface.C`;
  QMR: its `README.md`
- VS: `solidModels/nonLinGeomTotalLagVelocitySolid/nonLinGeomTotalLagVelocitySolid.C`;
  LVS: `solidModels/linGeomVelocitySolid/linGeomVelocitySolid.C`
- SNES: `numerics/foamPetscSnesHelper/foamPetscSnesSolver.C`;
  MA: `numerics/foamPetscSnesHelper/foamPetscMeshAssembly.C`
- DSL: `numerics/stabilisationModels/diffStencilLaplacianStab/diffStencilLaplacianStab.C`
  (`...Templates.H` for the face flux); SM: `numerics/stabilisationModels/stabilisationModel/stabilisationModel.C`
- MMS: `fluidModels/fluidModel/meshMotionSolidModel/meshMotionSolidModelFvMotionSolver.C`
- SMC: `solidModels/solidModel/solidModel.C`; EVP:
  `src/blockCoupledSolids4FoamTools/enhancedVolPointInterpolation/enhancedVolPointInterpolate.C`
- TUT: `tutorials/fluidSolidInteraction/<case>/` with the `.monolithic`
  variants of `system/fvSolution`, `system/fluid/fvSchemes`,
  `constant/fluid/fluidProperties`, `constant/fsiProperties`,
  `constant/solid/solidProperties`, `constant/fluid/dynamicMeshDict`.
  "All 12" = 3dTube, TurekHron2006, beamInCrossFlow, blobInTreacle,
  cavityFlexibleBottom, collapsibleChannel, foilInWind, membraneRoof,
  mokLidDrivenCavity, perpendicularFlap, ringAddedMass, womersleyTube.
- OF: OpenFOAM.com library behaviour (not in solids4foam).

Paper locations use the section and equation labels; "l." gives the line in
the file before this audit's edits.

## Claim table

| # | Paper location | Claim | Code location | Status | Note |
|---|---|---|---|---|---|
| 1 | Sec. 2 intro l.28-29 | Solid total Lagrangian; solid velocity is the primary unknown | VS 850-1022 (unknown `U`) | matches | |
| 2 | Sec. 2 `eqn:solid_displacement_velocity` | dD/dt = v_S | VS 331-367 | matches | discretised by BDF2 (row 40) |
| 3 | Sec. 2 `eqn:deformation_gradient` | F = I + (grad_0 D)^T, J = det F | VS 895-901 | matches | |
| 4 | Sec. 2 `eqn:stvk` | Saint Venant-Kirchhoff for finite strain | TUT solid `mechanicalProperties` (StVenantKirchhoffElastic) | matches | |
| 5 | Sec. 2 `eqn:hooke` | Hooke's law with linear-geometry solid | TUT ringAddedMass, womersleyTube, perpendicularFlap, blobInTreacle (linearElastic) | matches | |
| 6 | Sec. 2 l.163 | "Two-dimensional cases assume plane strain" | TUT `planeStress no`; womersleyTube `system/solid/blockMeshDict` l.19 (wedge) | differs | womersleyTube is axisymmetric (wedge); fixed |
| 7 | Sec. 2 todo l.164 | All monolithic tutorials at 257b2e564 use StVK/TL or Hooke/linear | TUT solidProperties at fdcc397e2 | matches | hash updated to fdcc397e2 |
| 8 | Sec. 2 `eqn:fluid_continuity_ale` | Incompressible continuity after GCL | NIF 1295-1298 | matches | |
| 9 | Sec. 2 `eqn:fluid_stress`, `eqn:fluid_momentum_ale` | Newtonian stress 2 nu sym(grad v) - p I | NIF 1247-1274 | ambiguous | residual uses laplacian(nu,U) only; transpose term omitted by default (NIH 128-131, NIF 282-288). Continuum statement correct; discrete omission now stated in Sec. 3.3 |
| 10 | Sec. 2 l.245-246 | Kinematic pressure, sigma_F = rho sigma*_F | NIF 569-579 (`rho*p`) | matches | |
| 11 | Sec. 2 `eqn:kinematic_interface` | v_F = v_S = v^Gamma on interface | QMC 1592-1758, 1455-1479 | matches | discretely v^Gamma comes from the predicted mesh motion (Sec. 3.3 "Mass flux") |
| 12 | Sec. 2 l.320 | TL solid imposes traction via t_0 / Nanson | VS 227-299 | matches | force = t \|Gamma^n\| (deformed area) unless `useUndeformedArea` |
| 13 | Sec. 3 intro l.21 | Mesh moved once per step, before the coupled solve, to a predicted interface position | QMC 2395-2432 | matches | |
| 14 | Sec. 3 intro l.22 + footnote | Convection fully implicit; linearised (extrapolated flux) option exists, not used | NIF 1184-1218; TUT all 12 `forceImplicitFlux yes` | matches | |
| 15 | Sec. 3 intro l.25 | Newton vector (v_F, p_F, v_S); mesh motion before and D update after solve outside the vector | QMC 2724-2769, 2616-2636 | matches | |
| 16 | Sec. 3.1 l.63 | Face values by linear interpolation | TUT fvSchemes `interpolate(U) skewCorrected linear` | differs (minor) | the convecting/continuity flux uses skew-corrected linear; fixed at `eqn:fluid_momentum_residual` text |
| 17 | Sec. 3.1 `eqn:least_squares_gradient` | First-neighbour least-squares cell gradients | TUT `gradSchemes default leastSquares; grad(D) leastSquaresS4f`; VS 730-742 | matches | |
| 18 | Sec. 3.1 l.73 | Diffusion: compact two-cell part + explicit non-orthogonal correction | TUT `laplacianSchemes Gauss linear corrected` | matches | |
| 19 | Sec. 3.1 `eqn:relative_flux` | Relative ALE flux Gamma.(v_f - v^Gamma_f) | NIF 1188-1234 (`fvc::makeRelative`) | matches | |
| 20 | Sec. 3.1 `eqn:moving_mesh_bdf2_time_term` | Moving-mesh BDF2 with Omega^n, Omega^{n-1}, Omega^{n-2} | NIF 1251 (`fvc::ddt(U)`, OF `backward`), TUT `ddt(U) backward` | matches | only where ddt(U) is backward: Euler in cavityFlexibleBottom, collapsibleChannel, 3dTube, perpendicularFlap, membraneRoof, mokLidDrivenCavity, blobInTreacle (existing todo l.139) |
| 21 | Sec. 3.1 l.116 | Variable-step BDF2 coefficients when Delta t adapts | VS 331-350 (`coefft`, `coefft00`); OF backward | matches | the AB2 predictor keeps constant coefficients (row 72) |
| 22 | Sec. 3.1 `eqn:bdf2` | Solid inertia by BDF2 on reference volume | VS 989-999; TUT solid `ddtSchemes default backward` | matches | |
| 23 | Sec. 3.2 l.151 | Solve on the already moved, fixed mesh Omega_F^n | QMC 2432, 2553 | matches | |
| 24 | Sec. 3.2 l.188-190 | Order: impose solid velocity, update interface p-gradient, map traction, solid residual, fluid residual | QMC 2852-3058 | matches | fluid formResidual resets the gradient again (NIF 1176) |
| 25 | Sec. 3.2 `eqn:fluid_momentum_residual` | laplacian - grad p - ddt - div(phi_rel, v) | NIF 1247-1254, 1276 | matches | `momentumStabilisation` scaleFactor 0 by default (NIF 295-297) |
| 26 | Sec. 3.2 l.263 | Convective flux from current Newton iterate | NIF 1188-1191 with `forceImplicitFlux yes` | matches | |
| 27 | Sec. 3.2 l.264 + todo | Convected velocity: limited second-order upwind or linear | TUT `div(phi,U)` | matches | perpendicularFlap tutorial uses `Gauss upwind` (todo l.265 already asks per case) |
| 28 | Sec. 3.2 l.267 | Pressure gradient by least squares | NIF 1238 (`fvc::grad(p)`, TUT leastSquares) | matches | |
| 29 | Sec. 3.2 `eqn:fluid_pressure_residual` | R_p = -sum Gamma.v_f + D_p, same flux as convection | NIF 1295-1298, 1323-1325 | matches | #597 |
| 30 | Sec. 3.2 `eqn:rhie_chow` | D_p = sum (alpha/a)_f [(p_N-p_P)/(n.d) - d/(n.d).(grad p)_f] \|Gamma\| | DSL Templates 42-43 (`scaleFactor*(snGrad(p) - n & interpolate(gradp))`), SM 131-161 (`fvc::div(gamma*magSf*face)`), NIF 1319-1323 | matches | snGrad `corrected` gives the stated combination |
| 31 | Sec. 3.2 l.298 | a_{P_f} linearly interpolated | NIF 1319 (`fvc::interpolate(1/A)`) | matches | interpolated reciprocal, as in l.320 |
| 32 | Sec. 3.2 l.299 | alpha_p = 1 unless stated | NIF 299-301; TUT all 12 `RhieChow scaleFactor 1.0` | matches | |
| 33 | Sec. 3.2 `eqn:rAU_definition` | alpha/a_P = alpha [3 Omega/(2 dt) + sum nu\|Gamma\|/(n.d) + sum max(phi,0)]^-1 | NIF 1312-1319 (`rAUf = -interpolate(1/UEqn.A())`, `A() = diag/V`) | differs | code coefficient is Omega_P/diag (units s); paper formula lacked Omega_P (wrong dimension); fixed. Sums also contain boundary-face diagonal contributions; stated |
| 34 | Sec. 3.2 l.319 | First-order upwind for the convection coefficient in a_P | NIF 1312-1317 (`jacobian-div(phi,U)`), TUT all 12 `Gauss upwind` | matches | scheme is user-set; all tutorials upwind |
| 35 | Sec. 3.2 `eqn:solid_bdf2_displacement` | D^n = (4D^{n-1} - D^{n-2} + 2 dt v^n)/3 | VS 331-367 | matches | constant-step form of the variable-step formula |
| 36 | Sec. 3.2 l.344-346 | Stress, interface traction and inertia at t^n; no force lag | VS 880-911, 254-257 | matches | |
| 37 | Sec. 3.2 `eqn:solid_velocity_residual` | sum T_f + rho b - rho BDF2(v) - c_d rho v + D_s | VS 986-999 | matches | `dampingCoeff` used in cavityFlexibleBottom (0.1) |
| 38 | Sec. 3.2 `eqn:rhie_chow_s` | D_s = sum alpha_d K_f [..] \|Gamma_{0,f}\| | VS 974-980 (nonlinear), 935-941 (linear) | differs (minor) | nonlinear variant multiplies by the deformed area magSfNew; fixed with a sentence |
| 39 | Sec. 3.2 l.387 | K = 2mu+lambda (linear); scalar tangent at start of analysis (finite strain) | VS 123-178, 547-548 | matches | `impK_` built once in the constructor |
| 40 | Sec. 3.2 l.389 todo | alpha_d 0.5 / 0.1 per tutorial | TUT solidProperties (ringAddedMass, TurekHron2006 0.5; cavityFlexibleBottom 0.1) | matches | spot-checked 3 cases |
| 41 | Sec. 3.2 l.391 | Stabilisation formed from the new-time D (function of trial v_S) | VS 976 (`DImplicit_`) | matches | `velocityBasedMomentumStabilisation` default off (VS 552-559) |
| 42 | Sec. 3.2 `eqn:face_force` | T_f = (J_f F_f^{-T} . Gamma_0) . sigma_f, F_f, J_f interpolated | VS 949-957 (`fvc::interpolate(J_*Finv_.T()) & Sf`) | differs (minor) | the product J F^{-T} is interpolated, not F and J separately; reworded |
| 43 | Sec. 3.2 l.403 | Cell stress from D^n by the selected law, linearly interpolated to faces | VS 94-120, 957 | matches | |
| 44 | Sec. 3.2 l.404 | Linear variant: T_f = Gamma_0 . sigma_f, small strain | VS 919-944, LVS 36-42 | matches | |
| 45 | Sec. 3.2 l.407 | Interface faces: force from fluid traction, stabilisation zero on traction boundaries | VS 227-270 | matches | |
| 46 | Sec. 3.2 l.409 | After convergence D set from v, stress and point displacements updated | VS 805-831; QMC 2630-2636 | matches | |
| 47 | Sec. 3.3 `eqn:mapped_solid_velocity` | Fluid interface velocity = transferred solid velocity (fixedValue) | QMC 1455-1479, 1592-1671 | matches | |
| 48 | Sec. 3.3 l.432 | Solid face velocity extrapolated with the cell gradient | QMC 1633-1648 | matches | |
| 49 | Sec. 3.3 `eqn:interface_pressure_gradient` | dp/dn = n.(laplacian(nu v)_P - (dv/dt)_f) | NIF 1096-1138 | matches | plain `fixedGradient` only (#594) |
| 50 | Sec. 3.3 l.447 | Interface acceleration with the fluid ddt scheme | NIF 1114-1117 | matches | |
| 51 | Sec. 3.3 l.449 | Interface pressure extrapolated with this gradient | NIF 1137 (`fixedGradient` evaluate) | matches | |
| 52 | Sec. 3.3 l.450 | fixedGradient: second order; zeroGradient: first order | NIH 306-317; QMC 2107-2126 | matches | claim from code comments/README, verified elsewhere |
| 53 | Sec. 3.3 `eqn:interface_fluid_traction` | rho(-p n + nu (grad v)^perp) | QMC 2893-2903; NIF 531-566 | matches | with `viscousStressTranspose no` (default) |
| 54 | Sec. 3.3 l.467 | Normal gradient "with the same compact and non-orthogonal-correction form" | NIF 546-548 (`snGrad()` of a fixedValue patch; OF boundary snGrad = deltaCoeffs*(U_b - U_P)) | differs | no non-orthogonal correction on boundary faces; fixed |
| 55 | Sec. 3.3 l.469 | Normal-gradient form is the viscous traction at an incompressible no-slip wall; full stress adds a first-order error | NIR 247-255, 396-408; NIF 538-566 | differs | stale: the omitted transpose part is physical on a deforming wall (Sec. 5); now stated, option and default named |
| 56 | Sec. 3.3 "Mass flux" | Relative flux zero on interface; continuity uses absolute interface flux | NIF 1223-1234, 1295-1298 | matches | zeroed on all `wall` patches when the mesh moves |
| 57 | Sec. 3.3 l.473 | Flux/swept-volume difference monitored as a diagnostic | QMC 1519-1552 (`interfaceFluxDiagnostics`, default off) | matches | |
| 58 | Sec. 3.3 `eqn:solid_to_fluid_transfer` | Face-area weights; directMap w = 1; AMI weights | QMC 277-350, 401-423 | matches | |
| 59 | Sec. 3.3 l.486 | Default: traction interpolated with w_sf | QMC 2944-2960, 426-448 | matches | |
| 60 | Sec. 3.3 l.487 | Same weights in residual and coupling blocks | QMC 1043-1057, 1214-1215 | matches | with conservative transfer, w_sf\|Gamma_s\| equals the overlap area w_fs\|Gamma_f\|, so still consistent |
| 61 | Sec. 3.3 `eqn:conservative_transfer` | Transpose transfer of forces, divided by undeformed solid area | QMC 2922-2943, 451-477 | matches | default `conservativeTractionTransfer no` (QMC 2035-2042) |
| 62 | Sec. 3.3 l.501 | Nonlinear solid must apply traction on undeformed area | QMC 2128-2151 | matches | |
| 63 | Sec. 3.3 l.504 | Mesh-motion displacement: face weights for faces, point transfer for points | QMC 1625-1757 | matches | an initial solid/fluid interface offset is subtracted (QMC 1761-1815); not described, not needed |
| 64 | Sec. 3.4 l.568 | `-snes_mf_operator`; J~ only builds the preconditioner | TUT fvSolution all 12; SNES 545-551; QMC 3214-3252 | matches | |
| 65 | Sec. 3.4 l.570 | J~ as operator converges only linearly | QMR "Replacing snes_mf_operator..." | matches | README statement |
| 66 | Sec. 3.4 l.572 | Restarted LGMRES, relative linear residual reduction | TUT `ksp_type lgmres`, `ksp_gmres_restart 200`, `ksp_rtol 1e-4` (1e-3 for 3dTube, beamInCrossFlow) | ambiguous | no `ksp_pc_side`: left preconditioning, so the test is on the preconditioned norm; stated |
| 67 | Sec. 3.4 l.574 | Stop on relative residual or relative Newton correction | SNES 117-140 (`SNESConvergedDefault`); TUT `snes_rtol`, `snes_stol` | matches | stol is relative to the iterate norm; wording made precise |
| 68 | Sec. 3.4 l.575 | Full step by default; bt or l2 line search optional | TUT `snes_linesearch_type basic` (bt foilInWind, l2 membraneRoof) | matches | |
| 69 | Sec. 3.4 "System scaling" | Fluid rows x s_F, solid rows x s_S, same for J~ rows | QMC 3046-3058, 3208-3212 | matches | |
| 70 | Sec. 3.4 l.582 | s_S default = average of 1/(mu dt); s_F = 1e8 here | QMC 2011-2033; TUT all 12 `fluidSystemScaleFactor 1e+08` | matches | added: s_S fixed with the initial dt; s_F default 1 |
| 71 | Sec. 3.4 "lagging" | Rebuilt every iteration by default; optional lag across steps | SNES 762-813; TUT 3dTube, beamInCrossFlow lag 8 persists | matches | |
| 72 | Sec. 3.4 "Adaptive time stepping" | x1.5 max increase, /2 max decrease; <2 or >7 iterations by default; bounds | QMC 2198-2287 (`minTargetNIter` 3, `maxTargetNIter` 6, `numIter < min-1`, `> max+1`) | matches | increase factor min(1.5, 1.1 maxTarget/N), decrease max(0.5, 0.9 maxTarget/N) |
| 73 | Sec. 3.4 l.592 | Failure: restore fields, mesh, time; retry with max(dt/4, dt_min), up to max retries | QMC 2555-2614, 1818-1867, 2228-2234; `maxTimeStepRetries` 10 | matches | also stops if dt cannot be reduced |
| 74 | Sec. 3.4 l.593 | Without adaptive dt a failure stops the run | QMC 2571-2580 | matches | |
| 75 | Sec. 3.5 `eqn:block_preconditioner` | 2x2 fluid/solid block J~ | QMC 2641-2721, 3093-3212 | matches | MatNest |
| 76 | Sec. 3.5 `eqn:Jmm_diag`, `eqn:Jmm_offdiag` | Compact diffusion, BDF2, first-order upwind | NIF 1427-1433, 1470-1475 | matches | tensor part of convection linearisation off (`addNewtonDivPhiU` default no, NIF 1446-1468); boundary-face diagonal terms included (stated) |
| 77 | Sec. 3.5 `eqn:Jmp` | -Omega_P g_{P,Q} | NIF 1541-1549; MA 592-700 | matches | uses `leastSquaresS4f` vectors |
| 78 | Sec. 3.5 `eqn:Jpm_diag`, `eqn:Jpm_offdiag` | Continuity derivative with weights w_f | NIF 1527-1536; MA 1433-1460 | matches | plain linear weights (no skew correction) |
| 79 | Sec. 3.5 `eqn:Jpp_diag`, `eqn:Jpp_offdiag` + l.743 | Compact Laplacian with alpha/a, plus wide interpolated-gradient part | NIF 1477-1524; DSL 149-191 | ambiguous | matrix uses `rAUf` times `scaleFactorJacobian` (default 1) instead of alpha_p; equal for alpha_p = 1; todo added |
| 80 | Sec. 3.5 `eqn:fluid_solid_velocity_momentum_coupling` | w_fs nu \|Gamma\|/(n.d) I | QMC 1001-1003, 1085-1124 | matches | |
| 81 | Sec. 3.5 `eqn:fluid_solid_velocity_pressure_coupling` | -w_fs Gamma^T | QMC 1005-1006, 1126-1170 | matches | |
| 82 | Sec. 3.5 `eqn:Jss_diag`, `eqn:Jss_offdiag` | (2dt/3) K_f compact Laplacian, BDF2, damping | VS 1063-1092, 319-328 | matches | factor is dt/coefft for variable dt |
| 83 | Sec. 3.5 `eqn:pressure_coupling_approximation` | w_sf rho \|Gamma_S,s\| n_F | QMC 1267-1280, 1364-1410 | matches | undeformed solid area |
| 84 | Sec. 3.5 `eqn:viscous_coupling_approximation` | w_sf rho nu \|Gamma_S\|/(n.d) (I + n n) | QMC 1288-1322, 1412-1447 | matches | |
| 85 | Sec. 3.5 `eqn:schur_complement_approx` | selfp Schur approximation | TUT `schur_precondition selfp` | matches | |
| 86 | Sec. 3.5.1 l.950-952 | Built after row scaling; multiplicative outer split | QMC 3208-3252; TUT `pc_fieldsplit_type multiplicative` | matches | |
| 87 | Sec. 3.5.1 l.954-956 | Schur upper (or full); bjacobi+ILU(0); one BoomerAMG V-cycle | TUT (`upper`; `full` in 3dTube, beamInCrossFlow; `max_iter 1`) | matches | |
| 88 | Sec. 3.5.1 l.957 | Inner blocks applied once (preonly) | TUT `*_ksp_type preonly` | matches | |
| 89 | Sec. 3.5.1 l.959, Fig. `fig:block_preconditioner`(b) | Solid block: LU on one process, or AMG | TUT all 12 `redundant` + `lu`; QMC 3297-3358 | not in code (AMG) | AMG is an options-only, untested choice; existing todo l.960 |
| 90 | Sec. 3.6 l.976-990 | AB2 predictor D^{n,*} = D^{n-1} + dt/2(3v^{n-1} - v^{n-2}) | QMC 2395-2402 | matches | constant coefficients also with variable dt; stated |
| 91 | Sec. 3.6 l.991-993 | Interpolated to points; replaced after the solve; no accumulation | QMC 2404-2412, 2630-2636 | matches | |
| 92 | Sec. 3.6 `eqn:mesh_displacement_interface` | Interface mesh displacement from transferred predicted D | QMC 1592-1758 | matches | |
| 93 | Sec. 3.6 l.1009-1010 | Pseudo-solid via `solids4foamSolidModel`; linear elastic or TL neo-Hookean | MMS 125-140; TUT dynamicMeshDict, fluid solidProperties | matches | TurekHron2006 uses `diffusionHyperElastic` (todo l.1042) |
| 94 | Sec. 3.6 l.973 | Assembled on the previous-step fluid mesh | MMS 205-217 (solved before `curPoints` moves the mesh) | matches | |
| 95 | Sec. 3.6 l.1010-1011 | (text) | | n/a | broken sentence ("reads / The unknown"); fixed |
| 96 | Sec. 3.6 `eqn:mesh_motion_diffusivity_raw`-`eqn:delta_clip` | 1/l^2, mean, clip [0.1, 100] x mean, normalise | MMS 63-122 | matches | |
| 97 | Sec. 3.6 l.1072 | Face values averaged to cells | MMS 114 (`fvc::average`) | matches | |
| 98 | Sec. 3.6 l.1079 | Mesh motion solved once per step, outside Newton | QMC 2432; MMS 205-217 | matches | |
| 99 | Sec. 3.6 l.1082 | Point values: extrapolate from each cell and average | SMC 2478-2504; EVP 400-418 | differs (minor) | inverse-distance weighted average; stated |
| 100 | Sec. 3.6 l.1083 | Points = initial points + point displacement | MMS 188-198 | matches | |
| 101 | Sec. 3.6 `eqn:gcl_swept_volume` | phi = 3/2 V^n - 1/2 V^{n-1} | OF `fvc::makeRelative` -> `backwardDdtScheme::meshPhi` = coefft phi^n - coefft00 phi^{n-1}, `mesh.phi` = V/dt | differs | missing 1/dt (dimension); fixed, Euler form added |
| 102 | Sec. 3.7 l.1106-1112 | Index sets for fluid/solid and for velocity/pressure define the splits | QMC 97-200, 2772-2795, 3254-3294 | differs (minor) | only fluid/solid IS are passed to PETSc; inner split is set by `fieldsplit_fluid_pc_fieldsplit_block_size`; fixed |
| 103 | Sec. 3.7 l.1114-1120 | SNES callbacks; MatNest blocks converted to AIJ | SNES 520-560; QMC 3214-3252 | matches | converted in serial and parallel |
| 104 | Sec. 3.7 l.1122-1123 | Interface data gathered to all processes; single interface | QMC 285-290, 2905-2960 | matches | |
| 105 | Sec. 3.7 l.1126-1127 | `decomposeParMonolithic`: joint graph, interface edges, region weights | `applications/utilities/decomposeParMonolithic/decomposeParMonolithic.C` 400-565 | matches | |
| 106 | Alg. 1 steps 1-11 | Store; predict; transfer; move mesh; seed; solve; retry; extract and update interface; set D; adapt dt | QMC 2377-2636; time-step selection by `setDeltaT` 2198-2287 | matches | |
| 107 | Alg. 2 steps 1-8 | Extract; impose interface velocity; pressure gradient; fluid force; transfer; solid residual; fluid residual; scale | QMC 2852-3058 | matches | |
| 108 | Fig. `fig:time_step_flowchart` | Same as Alg. 1/2, retry arrow to store | QMC 2377-2614 | matches | |
| 109 | Fig. `fig:block_preconditioner`(a) | Block legend | as rows 75-84 | matches | |

Count: 109 rows (some rows bundle a group of closely related statements).
Status totals: matches 94, differs 10 (of which 5 minor), ambiguous 3, not in
code 1, n/a 1.

## Corrections made in the .tex

Substantive (formula or statement wrong):

1. `eqn:rAU_definition`: the Rhie-Chow coefficient is the cell volume divided by
   the momentum diagonal (code `rAUf = -interpolate(1/UEqn.A())`, NIF 1312-1319);
   the factor Omega_{F,P} was missing, which also made the formula
   dimensionally wrong. Added, with a sentence on its dimension and on the
   boundary-face contributions to the sums (also used in Sec. 3.5).
2. `eqn:gcl_swept_volume`: the mesh flux lacked the division by Delta t;
   now (3V^n - V^{n-1})/(2 Delta t), with the Euler form.
3. Interface traction (Sec. 3.3, l.467-469): removed the claims that the
   boundary normal gradient carries a non-orthogonal correction and that the
   normal-gradient form is the viscous traction at any no-slip wall. Now: compact
   boundary gradient; it omits the transpose part, which is physical on a
   deforming wall (consistent with Sec. 5 and NIR); the option
   `viscousStressTranspose` exists, off by default, not used.
4. Sec. 2: "Two-dimensional cases assume plane strain" now distinguishes
   planar (plane strain) and axisymmetric wedge cases (womersleyTube).

Precision / stale description:

5. Interpolated face velocity: skew-corrected linear (TUT `interpolate(U)`).
6. Nonlinear-solid stabilisation is multiplied by the deformed face area.
7. Face force: J F^{-T} is interpolated as a product.
8. "(which is a second-order upwind scheme in the current work)" replaced by
   "linear or limited second-order upwind" (tutorials use both).
9. Krylov test: left preconditioning, preconditioned residual norm.
10. SNES step test: correction norm relative to the iterate norm.
11. Scaling defaults: s_S evaluated once with the initial Delta t; s_F
    default 1.
12. AB2 predictor keeps constant coefficients under adaptive Delta t.
13. Mesh-point interpolation is inverse-distance weighted.
14. Index sets: only the fluid/solid sets define a split; the inner split uses
    the block size.
15. Broken sentence in Sec. 3.6 ("the pseudo-solid problem reads / The
    unknown ...") merged.
16. Sec. 2 todo: solids4foam hash 257b2e564 -> fdcc397e2 (laws re-checked).

## Open judgement calls (left as todo or unchanged)

- `\todo` added at `eqn:Jpp_diag`: the assembled J_pp uses
  `scaleFactorJacobian` (default 1) instead of alpha_p; identical for
  alpha_p = 1 (all cases). Mention only if a case uses alpha_p != 1.
- Solid-block AMG in Sec. 3.5.1 and Fig. 2(b): not used in any tutorial
  (existing todo l.960). Remove "or AMG" unless the planned test is reported.
- Fluid `ddt(U)` is Euler in 7 of 12 monolithic tutorials (including
  cavityFlexibleBottom, collapsibleChannel and 3dTube), while Sec. 3 describes
  BDF2 and the solid is always BDF2 (existing todo l.139).
- How BDF2 starts on the first step is not stated: the velocity solid's
  displacement update uses Euler coefficients on the first step (VS 302-316);
  whether the fluid `backward` scheme does depends on the OpenFOAM fork.
  Decide whether to state it.
- The paper does not mention the first-time-step interface offset handling
  (QMC 1761-1815), the pressure reference cell, or `snes_max_linear_solve_fail`,
  `ksp_max_it`, `ksp_gmres_restart` values (existing todo l.576 covers
  tolerances). Probably not needed in the paper.
- Code comment QMC 1297-1301 says the residual traction is `n & (-devReff)`;
  that is only true with `viscousStressTranspose yes`. Code-comment issue, not
  a paper issue.
