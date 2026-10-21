# A2: discretisation differences, quasi-monolithic versus partitioned

Evidence note for M Section 5 ("Consistency with partitioned coupling").
Read from the source, not the READMEs, except where a README is quoted for a
measured number.

## Refs and abbreviations

- **R** = `origin/feature-petsc-snes-quasi-monolithic` at `257b2e564`
  (solver branch, contains #594 `eebf12bf6` and #597 `597cc6317`).
- **V** = `origin/verification/cavityflexiblebottom-partitioned-fine` at
  `f356c3242` (cavity four-level rerun; tutorial case files identical to R,
  only `verification/` differs).
- File abbreviations (all on R unless stated):
  - NIF = `src/solids4FoamModels/fluidModels/newtonIcoFluid/newtonIcoFluid.C`
  - QMI = `src/solids4FoamModels/fluidSolidInterfaces/newtonQuasiMonolithicCouplingInterface/newtonQuasiMonolithicCouplingInterface.C`
  - PF = `src/solids4FoamModels/fluidModels/pimpleFluid/pimpleFluid.esi.C`
    (OpenFOAM.com fork, the one used by the recorded runs)
  - FSI = `src/solids4FoamModels/fluidSolidInterfaces/fluidSolidInterface/fluidSolidInterface.C`
  - VS = `src/solids4FoamModels/solidModels/nonLinGeomTotalLagVelocitySolid/nonLinGeomTotalLagVelocitySolid.C`
    (`linearGeometryVelocity` is the same class with the linear-geometry flag)
  - TDS = `src/solids4FoamModels/solidModels/nonLinGeomTotalLagTotalDispSolid/nonLinGeomTotalLagTotalDispSolid.C`
  - LDS = `src/solids4FoamModels/solidModels/linGeomTotalDispSolid/linGeomTotalDispSolid.C`
  - NMWV, EWV, EWP = `src/solids4FoamModels/fluidModels/fvPatchFields/{newMovingWallVelocity,elasticWallVelocity,elasticWallPressure}/*.C`
  - MMS = `src/solids4FoamModels/fluidModels/fluidModel/meshMotionSolidModel/meshMotionSolidModelFvMotionSolver.C`
  - DSL = `src/solids4FoamModels/numerics/stabilisationModels/diffStencilLaplacianStab/diffStencilLaplacianStabTemplates.H`
  - CAV = `tutorials/fluidSolidInteraction/cavityFlexibleBottom/` (on V),
    WOM = `tutorials/fluidSolidInteraction/womersleyTube/` (on R).

"Mono" = `newtonIcoFluid` + velocity solid + `NewtonQuasiMonolithic`;
"part" = `pimpleFluid` + displacement solid + Aitken/IQN-ILS/Robin-Neumann.

## Summary

1. **womersleyTube offset (b): the leading candidate is the interface viscous
   traction.** Mono passes `rho*nuEff*snGrad(U)` (NIF:505-526); part passes
   `n & (-devReff)` (PF:425-444). On a deforming wall the two differ by
   `mu*grad(u.n)` (the transpose part of the viscous stress), which is a
   physical term, not a discretisation error: it is O(1) in h and Δt. Its
   size relative to the pressure is about `mu*omega*R/(E*h)` = 3.1e-4 for the
   tutorial (5 Pa s, 0.126 rad/s, R = 1 m, E h = 2000 N/m), the size of the
   observed 3.3-3.5e-4. The fingerprint fits: the fluid quantities agree to
   7e-5 or better, while the wall radial amplitude (-3.3e-4), wall phase
   (-4.8e-4 rad) and axial amplitude (+4e-4) are all offset by constant
   amounts. A travelling-wave exact solution with the Laplacian-form traction
   (script `a2_womersley_traction_variant.py`) gives the same signs and
   one quarter to one half of the magnitudes (B1). It is therefore a
   major contributor but not proven to be the only one.
2. **cavityFlexibleBottom offset (a): the leading candidate is the face
   interpolation in the continuity flux.** The offset is the #597 shift
   itself: before #597 mono and part agreed to 0.008-0.02% in `uy` on
   L2-L4. #597 moved mono by +0.15, +0.10, +0.06% (shrinking by a factor of
   only 1.5 per halving), and the post-#597 difference is 0.14, 0.08, 0.05%.
   #597 changed only the interpolation in the continuity residual, from
   `div(U) Gauss linear` to `interpolate(U) skewCorrected linear`.
   `pimpleFluid` builds its continuity flux from `fvc::flux(HbyA)`, which
   uses the default `linear`. On the strongly deformed cavity mesh
   (|uy| = 0.24 m), skew correction is not negligible, and the mesh-motion
   solvers differ (pseudo-solid against Laplacian), so the two runs also see
   different skewness. The difference is consistent (it vanishes with h).
3. The solid time integrators are algebraically equivalent for the linear
   solid (BDF2 on the velocity with BDF2 kinematics, against the backward
   `d2dt2`, which applies BDF2 twice), and the solid spatial operators and
   stabilisation are identical (`impKf*diffStencilLaplacian` applied to the
   displacement on both sides). The solid can explain neither offset.
4. The other differences (predicted mesh position, interface flux defect,
   convection linearisation, Rhie-Chow details, wall pressure condition,
   convergence tests) are either O(Δt^2), O(h^2), O(h) with small
   coefficients, or zero at steady state. They are catalogued below because
   a reader needs them, and because some are first order in h (interface
   pressure, normal viscous stress at the wall).
5. **README inaccuracy to fix:** the womersley README says the mono wall
   amplitude is 3.3-3.5e-4 below Robin-Neumann "on every mesh and step
   size". From the production CSVs, the m1 (coarsest) `wallMid_amp`
   difference is -8.0e-5 (`wallQuarter_amp` -1.9e-4). The 3.2-3.5e-4 holds
   on m2 (all four Δt) and m4.

## Difference catalogue

Orders: "O(1)" means the difference does not vanish under refinement (a
modelling difference); "consistent" means it does. Columns (a) and (b) say
whether the difference can produce the cavity offset (steady, slowly
shrinking) and the womersley offset (constant in h and Δt).

| # | Item | Mono | Part | Order of difference | (a) | (b) |
|---|---|---|---|---|---|---|
| D1 | Momentum convection | `fvc::div(phi,U)` with `phi = interpolate(U)&Sf - meshPhi`, flux of the current iterate (`forceImplicitFlux yes`), Newton | `fvm::div(phi,U)` with the conservative flux of the previous corrector (Picard) | O(Δt) lag within a step for part, converged at steady state | no (steady) | no (convection 1.5e-3) |
| D2 | Convection scheme (cavity) | `Gauss linearUpwind cellLimited leastSquares 1` | `Gauss linearUpwind grad(U)` (unlimited leastSquares) | consistent, limiter order between 1 and 2 | possible, ranked 3 | no (both `Gauss linear`) |
| D3 | Pressure-velocity coupling | Rhie-Chow as a stabilisation term `div(rAUf*(snGrad p - n.interpolate(grad p))|Sf|)`, `rAUf = -1/A(lap - ddt - upwind div)`, no `ddtCorr` | PISO: `phi = flux(HbyA) [+ rAUf*ddtCorr] - rAUf*snGrad(p)|Sf|`, `rAU = 1/A(UEqn)` | consistent, O(h^2) (O(h^3) where `rAU ~ h/|U|`); same `A` in both | unlikely | no |
| D4 | Continuity flux | `div(interpolate(U)&Sf)` with `interpolate(U) skewCorrected linear` (since #597) | `div(phi)` with `phi` built from `flux(HbyA)`, default `linear` | consistent; O(h^2) on smooth meshes, lower near the plate corners | **yes, ranked 1** | no (wedge mesh nearly unskewed) |
| D5 | Wall/interface pressure | `fixedGradient`, gradient `n.(nuEff lap U - ddt U)` (#594) | cavity and IQN-ILS: `zeroGradient`; Robin-Neumann: `elasticWallPressure` (Robin, `-rho a_n`, no viscous term) | O(h) in the wall pressure | possible, ranked 4 | no (h-dependent) |
| D6 | Interface viscous traction | `rho*nuEff*snGrad(U)` | `rho*n&(-devReff)` | **O(1)** on a deforming wall (missing `mu grad(u.n)`); O(h) at a stationary wall | small at steady state | **yes, ranked 1** |
| D7 | Viscous term in the momentum equation | `laplacian(nuEff,U)` only | `laplacian(nuEff,U) + div(nuEff dev2(T(grad U)))` (`divDevReff`) | consistent in the interior (O(h^2)); O(h) wall-flux terms | small | no |
| D8 | Non-orthogonal correction | full `corrected` laplacian in the residual (Newton-converged) | `corrected` with lagged explicit part; `nNonOrthogonalCorrectors 1` (cavity), 0 (womersley) | zero at convergence (cavity steady); O(Δt) lag in transients | no | no |
| D9 | Moving-mesh flux and wall kinematics | interface velocity = solid velocity extrapolated to the face; continuity uses the absolute flux `U_b.Sf`; mesh flux from the predicted mesh motion; defect `U_b.Sf - meshPhi` (logged) | wall velocity = BDF2 of the fluid face centres with the normal part set to `meshPhi/|Sf|` (no leakage by construction) | consistent, O(Δt^2) (observed time order 2) | no (zero at steady state) | no (Δt-dependent) |
| D10 | Time at which the fluid mesh moves | once per step, to the AB2-predicted solid displacement; not moved again after the solve | every coupling iteration, to the current solid displacement | O(Δt^3) local position, O(Δt^2) velocity | no (exact at steady state) | no (Δt-dependent) |
| D11 | Mesh motion solver | pseudo-solid (`solids4foamSolidModel`: neo-Hookean in the cavity, linear elastic in womersley), total displacement | `velocityLaplacian`, `quadratic inverseDistance (interface)`, incremental | consistent (different interior meshes, O(h^2) via truncation) | yes, via D4 (ranked 2) | no |
| D12 | Solid time integration | BDF2 on velocity, `D` from `U` by BDF2, stress and traction at the new time | womersley: backward `d2dt2` (BDF2 twice); cavity: Euler `d2dt2` | algebraically equivalent (linear, womersley); irrelevant at steady state (cavity) | no | no |
| D13 | Solid spatial operator and stabilisation | `n&interpolate(sigma) + impKf*diffStencilLaplacian(DImplicit)` | same with `D` | identical | no | no |
| D14 | Solid damping (cavity) | `-dampingCoeff*rho*U` | `dampingCoeff*rho*ddt(D)` | zero at steady state | no | n/a |
| D15 | Time scheme for the fluid | from `ddt(U)` (Euler cavity, backward womersley) | same | identical | no | no |
| D16 | Convergence criteria | SNES `rtol = stol = 1e-6`, KSP `rtol 1e-4`, mixed-unit step test | cavity Aitken `outerCorrTolerance 1e-5` (L4: strict test, 6e-6); womersley RN `1e-6`, `robinFluxTolerance 5e-3`; IQN-ILS `1e-6` | iterative | at most 10-20% of the L4 offset | possible, ranked 2 |
| D17 | Start-up | coupled from t = 0, inlet ramp 20 s (cavity); `restart yes` with exact `U`, `U_0` (womersley) | coupling from 10 s (cavity); exact `D`, `D_0`, `D_0_0`, `D_0_0_0` (womersley) | steady state unaffected; slowly decaying transient (womersley) | no | possible, ranked 3 |

### Details with file:line

**D1 Convection, flux and linearisation.**
Mono: `phi = fvc::interpolate(U) & mesh.Sf()` when `forceImplicitFlux` is set
or the flux is not extrapolated (NIF:1145-1151); both tutorials set
`forceImplicitFlux yes` (CAV and WOM `constant/fluid/fluidProperties.monolithic`),
so the extrapolated flux (NIF:1152-1178; QMI:2421-2448) is not used in the
residual, although QMI calls `formResidual(..., true)` (QMI:3006-3009). The
flux is made relative and set to zero on `wall` patches (NIF:1183-1194). The
residual is `laplacian(nuEff,U) - grad p - ddt U - div(phi,U)`
(NIF:1207-1214), all of it evaluated at the current Newton iterate, so the
convection is solved exactly (fully nonlinear) at each step. The Jacobian uses
a first-order upwind `jacobian-div(phi,U)` (NIF:1372-1378); with
`snes_mf_operator` it only preconditions.
Part: `fvm::div(phi, U)` (PF:526-534) with `phi` from the end of the previous
pressure corrector (PF:709, PF:752), so the convecting flux lags by one
corrector (Picard). Cavity: `nOuterCorrectors 1` (CAV
`system/fluid/fvSolution`), so in transients the lag is O(Δt); at steady state
it vanishes. Womersley: `nOuterCorrectors 2`, and the fluid is re-solved in
every coupling iteration.
Convecting flux: mono's `phi` is the plain interpolated velocity, which is not
discretely solenoidal (its divergence balances the Rhie-Chow term, D3/D4);
part's `phi` is the Rhie-Chow-corrected conservative flux.
Order: consistent (O(h^2) difference in the convecting flux; O(Δt) lag in
part's transients). Neither offset.

**D2 Convection scheme (cavity only).** CAV `system/fluid/fvSchemes:32`
`Gauss linearUpwind grad(U)` (gradSchemes default `leastSquares`, no limiter)
against `system/fluid/fvSchemes.monolithic:45`
`Gauss linearUpwind cellLimited leastSquares 1`. This is a case set-up
difference, not a property of the coupling. Limited schemes converge at
between first and second order near extrema and singular corners (the cavity
lips). The limiter was there before #597, when the two agreed to 0.01-0.02%,
so its effect at L2-L4 is at most of that size unless it cancelled another
term. Womersley: `Gauss linear` on both sides (WOM `fvSchemes:32`,
`fvSchemes.monolithic:45`).

**D3 Rhie-Chow and its ddt correction.**
Mono: `pressureResidual += pressureStabilisation().cellScalar(rAUf)`
(NIF:1267-1268), where the stabilisation face value is
`scaleFactor*(snGrad(p) - n & interpolate(grad p))` (DSL:42-43), weighted by
`rAUf = -interpolate(1/A)` of `laplacian - ddt - upwind div` (NIF:1257-1265).
Default `RhieChow` with `scaleFactor 1` (NIF:269-275); both tutorials use the
legacy `stabilisation { type RhieChow; scaleFactor 1.0; }`. There is no
`ddtCorr`-type term: the stabilisation depends on Δt only through the
`V/Δt` part of `A`.
Part: `rAU = 1/UEqn.A()`, `phiHbyA = fvc::flux(HbyA)` (PF:553-555), plus
`interpolate(rAU)*ddtCorr(U, phi, Uf)` when `ddtCorr` is on (PF:572-576), then
`phi = phiHbyA - pEqn.flux()` (PF:692-711). On a moving mesh `ddtCorr` uses
`Uf`, whose normal component is reset to `phi` by `correctUf` (PF:749), so the
correction is of the size of the mesh-motion change of `Sf` and vanishes at
steady state.
`A` is essentially the same on both sides: the implicit part of
`linearUpwind` is upwind, which is mono's `jacobian-div` scheme. The two
Rhie-Chow fluxes differ by `interpolate(rAU grad p) - rAUf interpolate(grad p)`,
O(h^2) relative to the Rhie-Chow term, which is itself O(h^2)-O(h^3).
Cannot explain (a) at the 0.1% level, and is h-dependent for (b). The
partitioned cavity runs at Δt = 0.25 and 0.125 changed `uy` by 0.014% and
0.003% (V README), so any Δt dependence of the steady part solution through
`rAU` is small; mono was run at Δt = 0.5 on every level and its steady Δt
sensitivity has not been measured.

**D4 Continuity flux (#597).** Mono since #597:
`pressureResidual = -div(interpolate(U) & Sf)` (NIF:1240-1243), so the
continuity flux is the convecting flux, both with the `interpolate(U)`
scheme, which is `skewCorrected linear` in every monolithic tutorial variant
(CAV `fvSchemes.monolithic:59`, WOM `fvSchemes.monolithic:59`). Before #597 it
was `-fvc::div(U)` with `div(U) Gauss linear` (diff `98211d90e..597cc6317`,
NIF hunk at line 1230), i.e. continuity with plain linear interpolation and
convection with skew-corrected interpolation.
Part: the continuity flux is `phi = flux(HbyA) - rAU snGrad(p)|Sf|`; the
interpolation of `HbyA` is looked up as `flux(HbyA)` (OpenFOAM `fvc::flux`),
which falls to `default linear` in CAV `system/fluid/fvSchemes:44`.
`interpolate(U) skewCorrected linear` in the partitioned CAV `fvSchemes:45` is
used only for `Uf` (constructor, `correctUf`), not for the continuity flux.
So after #597, mono interpolates the continuity flux with skew correction and
part does not. Before #597 neither did. This matches the record (V README,
"Rerun with the newtonIcoFluid continuity fix"):

| Level | ΔX (m) | mono pre-#597 − part (m) | #597 shift (m) | mono post-#597 − part (m) |
|---:|---:|---:|---:|---:|
| 2 | 0.05 | −1.8e-5 (−0.008%) | +3.49e-4 | +3.31e-4 (0.145%) |
| 3 | 0.025 | −4.8e-5 (−0.020%) | +2.28e-4 | +1.80e-4 (0.076%) |
| 4 | 0.0125 | −2.9e-5 (−0.012%) | +1.49e-4 | +1.20e-4 (0.051%) |

(computed from the `uy` columns of the V README table; positive = smaller
magnitude). The #597 shift falls by a factor of 1.53 per halving, and the
post-#597 offset by 1.84 and 1.50. Skewness on a smoothly deformed hex mesh
makes skew correction an O(h^2) change, but near the plate ends (deforming
interface meeting fixed walls) the mesh motion is not smooth, which can slow
the convergence of the difference. The difference is consistent: the p = 2
extrapolations agree to 0.04% (V README). A related observation: in
`blobInTreacle` (R, `verification/README.md` "Quasi-monolithic coupling"),
post-#597 mono is below part by 0.38, 0.29, 0.17% on x1, x2, x4 (computed from
the table: 0.116851/0.117301, 0.119346/0.119696, 0.120020/0.120224), also
shrinking by less than a factor of 2 per refinement. The pre-#597 values there
were not as close (−0.14% on x2 and x4), so this case supports the pattern but
does not isolate the cause.

**D5 Wall/interface pressure condition (#594).**
Mono: `updatePressureGradientBoundary` sets the gradient of a plain
`fixedGradient` pressure on a fixed-value-velocity wall to
`n & (nuEff lap(U)_P - ddt(U)_b)` (NIF:1056-1098; since #594, derived types
such as `fixedGradientCorrected` are left alone, NIF:1061-1071). It is called
at every residual evaluation for all wall patches (NIF:1134-1136, 1101-1110),
and for the interface before the traction is formed (QMI:2836-2848,
1451-1461). CAV `0/fluid/p.monolithic:45` and WOM `0/fluid/p.monolithic` use
`fixedGradient` on the interface.
Part: cavity `zeroGradient` (CAV `0/fluid/p:41-43`), womersley IQN-ILS
`zeroGradient` (WOM `0/fluid/p.dirichletNeumann`), womersley Robin-Neumann
`elasticWallPressure` (EWP:587-707; at convergence the normal gradient is
`-rho_f a_n` from the solid acceleration, no viscous term; PF:53-195 sets the
consistent interface flux).
Order: `zeroGradient` gives an O(h) error in the wall pressure,
`d*dp/dn` with `d` the wall-to-centre distance (ringAddedMass verification
README, "Defects found by this study": first-order ratio error, factors 1.66
and 1.86 per halving). At a stationary wall in steady flow `dp/dn = mu
d2u_n/dn2 = -d(tau_w)/ds`, so the effect scales with the along-wall gradient
of the wall shear. Robin without the viscous term: O(h) in the viscous part
only. Both are h-dependent, so they cannot produce (b). For (a) the term was
present before #597 when the two agreed, so it is not the cause of the
post-#597 offset (unless it cancelled D4 before; see run A3).

**D6 Interface traction.**
Mono: `patchViscousForce = rho*nuEff*snGrad(U)` (NIF:505-526), added to
`-rho*p_b*n` when `passViscousStress yes` (QMI:2852-2872; both tutorials set
it). The comment at NIF:512-519 argues that the full `n & devReff` adds
transpose and trace parts whose tangential components are cell values, a
first-order error that the residual does not contain. The `blobInTreacle`
ablation supports this for a stationary wall at steady state (mono with
`devReff`: observed order 1.4; with `snGrad`: 1.9; R blob README).
Part: `rho*(n & -devReff)` (PF:425-444), passed for every partitioned coupling
(FSI:1113-1131; no switch).
The two differ by `mu*(grad U)^T.n` (OpenFOAM's `n & T(grad U)` =
`grad(u.n)` for constant `n`) plus the trace term. At the exact-solution
level `div u = 0` removes the trace, and
`mu grad(u.n) = mu (d_n u_n) n + mu (d_s u_n) t`. On a no-slip wall
`d_s u_n` is the tangential derivative of the wall normal velocity and
`d_n u_n = -div_s(u_t) - kappa u_n` (surface divergence and curvature terms of
the wall velocity). Both are zero on a stationary wall, so `snGrad` is then
the correct (and conservative) traction. They are **not** zero on a deforming
wall. In the womersley tube, `d_r u_r = -u_r/R + i k u_x` and
`d_x u_r = -i k u_r` at the wall. Hence on a deforming wall the Laplacian-form
traction drops a physical part of the Cauchy traction: an O(1) difference,
of relative size about `mu*omega*R/(E*h)` for a compliant tube (B1). In the
fluid interior the Laplacian form is exact, because `div(mu grad(u)^T) =
mu grad(div u) = 0`. Only the per-patch wall flux differs. Over the whole
closed boundary the transpose fluxes sum to zero, so the term is balanced on
the inlet and outlet.
O(h) parts at a stationary wall (relevant to (a)): with the boundary gradient
`(I - nn).grad(U)_P + n snGrad(U)` (OpenFOAM's corrected boundary gradient), a
Taylor expansion gives normal-traction errors of about `-(1/2) d dp/dn` (mono:
correct wall pressure from D5, `mu snGrad(U).n = -(d/2) mu d2u_n/dn2`) and
`-(1/3) d dp/dn` (part: zeroGradient pressure plus `devReff`, the
cell-centre pressure error partly cancelling the viscous one). Both are first
order with a small coefficient (`dp/dn = -d(tau_w)/ds` at a steady stationary
wall). This is my estimate and has not been checked numerically.

**D7 Viscous term in the momentum equation.** Mono: `laplacian(nuEff, U)` in
the residual (NIF:1209) and the Jacobian (NIF:1372-1376). Part:
`turbulence_->divDevReff(U)` (PF:530), i.e.
`-laplacian(nuEff,U) - div(nuEff*dev2(T(grad(U))))`, the second term explicit
`Gauss linear` (CAV/WOM `fvSchemes`: `div((nuEff*dev2(T(grad(U))))) Gauss
linear`). In the interior the extra term is O(h^2). Its boundary-face values
use the same first-order boundary gradient as `devReff` (D6), so part's
traction is its own discrete wall flux, as mono's `snGrad` traction is its
own. Each side is internally conservative, but the two wall fluxes differ as
in D6.

**D8 Viscous non-orthogonal correction.** Mono: `laplacian` with
`Gauss linear corrected` evaluated fully in the residual (NIF:1209), Jacobian
orthogonal part only (NIF:1372-1376); exact at Newton convergence. Part:
`corrected` with the explicit correction from the current iterate; pressure
`nNonOrthogonalCorrectors 1` (cavity) and 0 (womersley). At steady state
(cavity) both are converged. Boundary `snGrad` on a fixed-value patch has no
non-orthogonal correction on either side (same OpenFOAM patch field). Not a
candidate.

**D9 Moving-mesh flux, wall kinematics and BDF2 geometric conservation.**
Mono: the fluid interface velocity is the solid cell velocity extrapolated to
the face with the cell gradient (QMI:1602-1617, then 1424-1448). Continuity
uses the absolute face flux, so at the interface it is `U_b.Sf` (NIF:1240-1243);
the convecting flux subtracts `meshPhi` (NIF:1183-1185), and its wall values
are zeroed (NIF:1187-1193). The difference `U_b.Sf - meshPhi_b` is a mass
defect at the interface, reported with `interfaceFluxDiagnostics yes`
(QMI:1488-1521).
Part: `newMovingWallVelocity` / `elasticWallVelocity` set the wall velocity
to the BDF2 derivative of the fluid face centres and then replace its normal
component by `meshPhi/|Sf|` (NMWV:202-263, EWV:262-371). The wall flux equals
the mesh flux, so there is no leakage, by construction.
BDF2 GCL: both fluids use the same OpenFOAM `meshPhi`/`backward` machinery,
so any discrete-GCL defect of the backward scheme on moving meshes is common
to both. QMI:2468-2476 states that `mesh.phi()` is second order and GCL
consistent for a second-order time scheme. I could not check this against
the OpenFOAM v2512 source (not available here); it is consistent with the
measured time order of 1.94-2.07 of mono womersley (WOM verification README).
Order: O(Δt^2) (follows from D10). Zero at steady state; Δt-dependent, so it
cannot produce (b).

**D10 When the fluid mesh moves.** Mono: once per time step, before the
solve, to `D* = D^{n-1} + (3Δt/2) U^{n-1} - (Δt/2) U^{n-2}` (QMI:2359-2376,
mapped at 2388, moved at 2396). The mesh is not moved again: after the solve
`mapInterfaceSolidToMeshMotion` is called with the predicted `D` still in
place, and only then does `updateDisplacement` set `D^n` by BDF2 from `U^n`
(QMI:2589-2599, VS:805-831). The fluid domain is therefore always at the AB2
prediction. `D*` and the BDF2 `D^n` are both third-order-local
approximations, so the position lag is O(Δt^3) per step and does not
accumulate (MMS:193, `points0 + pointD`). The resulting mesh-velocity
mismatch is O(Δt^2).
Part: the mesh is moved in each coupling iteration to the current (relaxed)
solid interface displacement (`fluidSolidInterface::moveFluidMesh`,
FSI:1544), so at convergence it sits at the solid's `D^n`. Zero at steady
state; Δt-dependent.

**D11 Mesh motion.** Mono: `motionSolver solids4foamSolidModel` (CAV/WOM
`constant/fluid/dynamicMeshDict.monolithic`). It is a solid model in the
fluid region: `nonLinearGeometryTotalLagrangianTotalDisplacement`,
`neoHookeanElastic` (mu = 1, K = 3) in the cavity, `linearGeometryTotalDisplacement`
`linearElastic` in womersley (`constant/fluid/solidProperties.monolithic`,
`mechanicalProperties.monolithic`). It is solved by PETSc SNES to
`snes_rtol 1e-6`, with total displacement `points0 + pointD` (MMS:193,
205-216), and uniform stiffness when no `diffusivity` is given (MMS:62).
The task's `diffusionHyperElastic` law exists on R but is not used by these
two cases.
Part: `velocityLaplacian`, `diffusivity quadratic inverseDistance (interface)`
(CAV/WOM `constant/fluid/dynamicMeshDict`), incremental.
Effect: different interior meshes at the same interface position, so
different truncation errors: a consistent O(h^2) difference, larger where the
mesh is distorted. In the cavity it changes the skewness that D4 acts on.

**D12 Solid time integration.**
Mono (VS): residual `div(sigma(D^n)) + rho(g - ddt(U) - c U)` with
`D^n = (Δt U^n + c0 D^{n-1} - c00 D^{n-2})/c` (BDF2 kinematics,
VS:331-367); stress at the new time (VS:880-911); `ddt(U)` backward (WOM, CAV
solid `fvSchemes.monolithic`).
Part: womersley `linearGeometryTotalDisplacement` with backward `d2dt2`
(WOM `system/solid/fvSchemes`; the README notes that it "applies the backward
ddt twice", hence `D_0_0_0`). Cavity `nonLinearGeometryTotalLagrangianTotalDisplacement`
`implicitSegregated` with Euler `d2dt2` (CAV `system/solid/fvSchemes`).
The backward `d2dt2` is the BDF2 combination of the backward `ddt` of
`D`, `D.oldTime()` and `D.oldTime().oldTime()`
(`src/solids4FoamModels/numerics/backwardD2dt2Scheme/backwardD2dt2Scheme.C:187-243`),
i.e. `a^n = BDF2(V)^n` with `V^k = BDF2(D)^k`. Mono enforces
`U^k = BDF2(D)^k` at every step, so `a^n = BDF2(U)^n` is the same on both
sides. So for the linear womersley
solid the two schemes are algebraically identical once started consistently.
They differ only in start-up (D17) and in damping (D14). Not a candidate for
either offset.

**D13 Solid spatial operator and stabilisation.** Mono:
`traction = n & interpolate(sigma) + impKf*diffStencilLaplacian(DImplicit)`
(VS:922-939, nonlinear geometry with deformed normals VS:949-978);
`velocityBasedMomentumStabilisation` defaults to off (VS:552-559), so the
stabilisation acts on the displacement. Part: the same `impKf*` stabilisation
on `D` (TDS:493-494; LDS:351-352). The scale factors are the same: cavity 0.1
on both, womersley 0.5 on both (`constant/solid/solidProperties*`). The
operators are identical. In the nonlinear cavity case both form the
traction in the deformed configuration (VS:949-978 with `J F^-T Sf`; TDS
`currentSf`, TDS:57); I did not compare the two expressions term by term.
Not a candidate for (a) at steady state beyond O(h^2), and not used in (b)
(linear geometry).

**D14 Solid damping (cavity).** Mono: `-dampingCoeff*rho*U` (VS:994);
part: `dampingCoeff*rho*fvm::ddt(D)` (TDS:537-540), both 0.1 s^-1. Zero at
steady state.

**D16 Convergence criteria.** Mono: one SNES per step, `snes_rtol 1e-6`,
`snes_stol 1e-6`, `ksp_rtol 1e-4` (CAV/WOM `system/fvSolution.monolithic`),
with the fluid residual scaled by `fluidSystemScaleFactor 1e8` and the solid
by the default `1/(mu Δt)` (QMI README). `snes_stol` is a step-length test on
the full mixed-unit vector (pressure, fluid velocity, solid velocity). In
womersley the solid velocity is about 1e-4 of the pressure, so a `stol`
termination could leave the solid velocity loosely converged. Mono takes 2.00
Newton iterations per step in every womersley run (CSV `mean_iterations`),
consistent with termination by `rtol` after two KSP solves of 1e-4 each.
Part: cavity Aitken `outerCorrTolerance 1e-5`; the recorded L1-L3 used the
legacy `min(r1, r2)` test, the strict reruns agree to 0.02% (V README).
Womersley Robin-Neumann `outerCorrTolerance 1e-6`, `robinPressureTolerance
1e-5`, `robinFluxTolerance 5e-3`; IQN-ILS `outerCorrTolerance 1e-6`
(WOM `constant/fsiProperties.robin`, `.iqnils`). Robin-Neumann and IQN-ILS
themselves differ by 2.2e-4 in the wall amplitude at m2 n100 (WOM
verification README), so 2e-4 is the scale of partitioned-variant spread.

**D17 Start-up.** Womersley mono: `restart yes`, exact `U` and `U_0`
(WOM `0/solid/U.monolithic`, `U_0.monolithic`); part: exact `D` to `D_0_0_0`.
The README notes a slowly decaying first-period transient, and periods five to
six change by up to 6.4e-5 (mono) and 7e-5 (part) (CSV `periodicity`).

## (a) cavityFlexibleBottom: ranking and discriminating runs

Observed (V README): mono − part in `uy` = +3.31e-4, +1.80e-4, +1.20e-4 m on
L2-L4 (0.14, 0.08, 0.05%); in `Fy` 0.20, 0.11, 0.07%. Steady state, so only
spatial and steady-iteration differences count.

| Rank | Candidate | Why | Cheapest discriminating run | Expected if it is the cause |
|---:|---|---|---|---|
| 1 | D4: skew-corrected continuity flux (mono, since #597) against linear (part) | the offset equals the #597 shift (table in D4); pre-#597 agreement 0.008-0.02% | A1: mono L2 and L3, serial, Δt 0.5, with `interpolate(U) linear;` in `system/fluid/fvSchemes.monolithic` | mono − part back to 0.02% or below on L2 and L3 |
| 2 | D11: mesh-motion solvers give different skewness | D4 acts on skewness, which differs between pseudo-solid and Laplacian motion | A0 (no run): `checkMesh -region fluid -latestTime` on the existing L2/L3 final states of both, compare max skewness and its location | mono mesh more skewed near the plate ends |
| 3 | D2: limited against unlimited `linearUpwind` gradient | limiter errors converge between first and second order | A2: mono L2 with `div(phi,U) Gauss linearUpwind grad(U);` | change of order 1e-4 m at L2 |
| 4 | D5/D6: interface pressure and viscous normal stress, O(h) | first order, but present before #597 when they agreed | A3: mono L2 with `zeroGradient` interface pressure (runs, with a warning) | first-order change; tests the cancellation hypothesis |
| 5 | D16/D3: steadiness, coupling tolerance and steady Δt dependence | mono L4 steady to ≤ 5e-6 m at 300 s, part L4 1.3e-5 m (V README): ≤ 10-20% of the L4 offset | A4: mono L2 at Δt = 0.25 | change ≤ 1e-5 m |

Excluded: D9, D10, D12, D14 (zero at steady state), D13 (identical), D15.
If A1 confirms D4, the consistency statement for M is that the two couplings
differ by the choice of face interpolation in the continuity flux, which is a
case set-up choice. M should then run the cavity comparison with the same
interpolation on both sides, or say which it uses.

## (b) womersleyTube: ranking and discriminating runs

Observed: mono − Robin-Neumann, from `verification/temporal/production/
womersleyTube_results{,_monolithic}.csv` on R (my subtraction):

| Run | wallMid amp | wallQuarter amp | wallThreeQuarter amp | wallMid phase (rad) | axialMid amp | flow amp | speed | attenuation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| m1 n200 | −8.0e-5 | −1.9e-4 | +6.3e-5 | −5.2e-4 | +4.7e-4 | −1.5e-5 | −2.5e-5 | −7.2e-4 |
| m2 n50 | −3.4e-4 | −3.5e-4 | −1.7e-4 | −4.8e-4 | +4.1e-4 | −4.5e-5 | −7.2e-5 | −4.1e-4 |
| m2 n100 | −3.3e-4 | −3.4e-4 | −1.6e-4 | −4.8e-4 | +4.1e-4 | −4.1e-5 | −7.0e-5 | −4.0e-4 |
| m2 n200 | −3.3e-4 | −3.4e-4 | −1.6e-4 | −4.8e-4 | +4.1e-4 | −3.8e-5 | −6.9e-5 | −4.1e-4 |
| m2 n400 | −3.2e-4 | −3.3e-4 | −1.5e-4 | −4.8e-4 | +4.1e-4 | −3.5e-5 | −6.8e-5 | −4.0e-4 |
| m4 n200 | −3.5e-4 | −3.5e-4 | −1.9e-4 | −4.8e-4 | +3.9e-4 | −3.3e-5 | −7.4e-5 | −3.5e-4 |

The fluid (flow rate, pressure, wave speed) agrees to 7e-5 or better. The
wall (radial amplitude and phase, axial amplitude) carries a constant offset
on m2 and m4 for all Δt. This points to the load on the wall or to the
solid, not to the fluid discretisation, and to a term that does not vanish
with h or Δt.

### B1. Estimate of the traction effect

`a2_womersley_traction_variant.py` solves the exact linear problem of the
verification (`womersley_exact.py` on R, numpy only) with the interface
traction changed from `-p n + 2 mu D(u).n` to `-p n + mu (grad u).n`. Output
(Laplacian form minus full, relative), travelling wave with the same axis
pressure at x = 0:

| x | radial amp | radial phase (rad) | axial amp |
|---|---:|---:|---:|
| L/4 | −9.7e-5 | −1.6e-4 | +6.5e-4 |
| L/2 | −1.6e-4 | −1.3e-4 | +5.9e-4 |
| 3L/4 | −2.2e-4 | −1.0e-4 | +5.3e-4 |

Re(k) −5.2e-5, Im(k) +7.6e-4 (relative); flow rate −2e-6.
The normal part alone gives −1.9e-4 (radial amp at L/2) and the shear part
alone +3.6e-5.
Compared with the observed offsets, it has the right sign in all three wall
quantities and the right order of magnitude, and it leaves the fluid flow
almost unchanged, as observed. It gives about half of the radial amplitude
offset at L/2 and a quarter of the phase offset, and its distribution along
the tube (growing towards 3L/4) differs from the observed one (smaller at
3L/4). The simulations impose the full-traction exact solution at both tube
ends, which the travelling-wave estimate does not represent. So the traction
form is a confirmed contributor of the right size, but whether it accounts
for the whole offset needs run B2.

| Rank | Candidate | Why | Cheapest discriminating run | Expected if it is the cause |
|---:|---|---|---|---|
| 1 | D6: Laplacian-form traction drops `mu grad(u.n)` | O(1) in h and Δt; size `mu omega R/(E h)` = 3.1e-4; fingerprint; B1 estimate | B2: mono m2 n50 (77 s serial) with `patchViscousForce` = `rho*(n & -devReff)` (the `pimpleFluid` form), or better `rho*nuEff*(snGrad(U) + grad(U)_b & n)` with the tangential part from the wall velocity; or part (Robin-Neumann) m2 n50 with `pimpleFluid::patchViscousForce` = `rho*nuEff*snGrad(U)` | wall offsets fall to ≲ 1e-4 (mono variant) or appear in part (part variant) |
| 2 | D16: partitioned convergence (Robin flux tolerance 5e-3; IQN-ILS and RN differ by 2.2e-4) | the reference itself spreads by 2e-4; but the mono − part offset is too constant across Δt for a tolerance effect | B3: Robin-Neumann m2 n50 with `robinFluxTolerance 5e-4`, `outerCorrTolerance 1e-7` | part wall amplitude moves by ≥ 1e-4 |
| 3 | D17: slowly decaying start-up transient | the transient decays slowly; mono starts differently | B4 (no run): Fourier coefficients over periods 4-5 and 5-6 from the existing histories, mono and part | the mono − part offset changes between windows |
| 4 | D5: Robin pressure without viscous term, D11 mesh motion | h-dependent (O(h), O(h^2)); the m1 row differs from m2/m4, so a part of this kind exists at m1 only | none needed | – |

Excluded: D9, D10 (Δt-dependent, observed offset independent of Δt from 50 to
400 steps per period), D12, D13 (identical schemes), D1, D2 (convection
relative size 1.5e-3, same scheme), D3, D4 (h-dependent), D8.

## Recommendations and open questions for Philip

1. **Interface traction on a deforming wall.** The `nuEff*snGrad(U)`
   traction is exact and conservative on stationary or rigidly moving walls
   (blobInTreacle, ringAddedMass, the cavity at steady state). On a deforming
   wall it drops `mu grad(u.n)`, which is O(mu omega R/(E h)) of the
   pressure. This is small for the 3D tube and arterial parameters but
   3e-4 in the scaled womersley case. Two consistent fixes:
   (i) the `pimpleFluid` route, adding `div(nuEff*dev2(T(grad(U))))` to the
   `newtonIcoFluid` residual (the Jacobian can omit it under
   `snes_mf_operator`) and using `n & devReff` as the traction, which is then
   the discrete wall flux again (part converges at order 2.2 in blob with
   this);
   (ii) adding `mu grad_s(u.n)` and `mu (d_n u_n) n` evaluated from the
   interface velocity (surface gradient, and `d_n u_n = -div_s(u_t)` minus
   curvature terms) to both the traction and the momentum wall flux.
   Either is a small change. The M claim "interface traction as the momentum
   equation's wall flux; `devReff` traction: first order" should be worded
   as being about the stationary-wall case of blobInTreacle, and the
   deforming-wall term discussed. Decide whether this is within "no
   substantial new solver development".
2. **Cavity:** if run A1 confirms D4, M Section 5 should state the
   interpolation used for the continuity flux on each side, or rerun mono
   L2-L4 with `interpolate(U) linear` for the comparison table.
3. **README fix:** womersley README "3.3-3.5e-4 ... on every mesh" is not
   true for m1 (−8.0e-5 at L/2).
4. **Mixed-unit `snes_stol`:** worth checking in the logs that mono
   womersley terminates by `rtol` (SNES converged reason
   `CONVERGED_FNORM_RELATIVE`), not `CONVERGED_SNORM_RELATIVE`.
5. **Unverified here:** that OpenFOAM v2512 `mesh.phi()` with `backward` is
   GCL-consistent at second order (QMI:2468-2476 asserts it), and that
   `fvc::flux(HbyA)` uses the `flux(HbyA)` scheme name (D4). Both need the
   OpenFOAM source, which is not in this environment.

## Draft text for M Section 5

```latex
The quasi-monolithic and partitioned couplings share the solid discretisation, the face interpolation of the stresses and the solid stabilisation, and, for the linear solid, their time integration: the BDF2 velocity formulation with BDF2 kinematics is algebraically identical to the backward second time derivative used by the displacement solid.
They differ in the fluid and at the interface.
In the fluid, \texttt{newtonIcoFluid} solves the convection with the flux of the current iterate, adds the Rhie--Chow term to the continuity residual as a stabilisation without a time-step correction, and builds the continuity flux from the same interpolated velocity that convects momentum, whereas \texttt{pimpleFluid} convects with the flux of the previous pressure corrector and imposes continuity on the Rhie--Chow-corrected flux.
At the interface, the monolithic fluid sets the normal pressure gradient from the normal momentum equation, receives the solid velocity extrapolated to the interface faces, and moves its mesh once per step to the extrapolated interface displacement with a pseudo-solid, whereas the partitioned fluid uses a zero-gradient or Robin pressure, takes its wall velocity from the motion of its own mesh, and moves the mesh with a Laplacian smoother to the current solid displacement in every coupling iteration.
The monolithic interface traction is the wall flux of the momentum equation's viscous term, $\mu\,\partial\mathbf{u}/\partial n$, whereas the partitioned traction is $\mathbf{n}\cdot 2\mu\mathbf{D}(\mathbf{u})$.
All of these differences vanish under mesh and time-step refinement except the last, which on a deforming wall omits $\mu\nabla(\mathbf{u}\cdot\mathbf{n})$, a term of relative size $\mu\omega R/(Eh)$ \todo{confirm with run B2; fix or quantify}.
In the steady cavity the two couplings differ by 0.14\%, 0.08\% and 0.05\% in the plate displacement on the three finest meshes and extrapolate to within 0.04\% of each other; the difference is attributed to the skew-corrected interpolation of the continuity flux in the monolithic set-up \todo{confirm with run A1}.
```
