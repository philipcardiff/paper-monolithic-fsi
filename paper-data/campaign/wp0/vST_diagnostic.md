# vST diagnostic on blobInTreacle x1 (D1, D3)

Run on 23 October 2026 on the mac-studio, serial, from the converged WP0
x1 states (`wp0-blob-qm-vstyes-x1`, `wp0-blob-qm-vstno-x1`,
`wp0-blob-iqn-x1`, t = 3 s; same build `85b0c1de6`, same machine). No
solver code was changed. Scripts: `scripts/vst_d1.py`, `scripts/vst_d3.py`.
The replacement-D2 was dropped: the WP0 `linearUpwind cellLimited
leastSquares 1` entry already reads as the unlimited default gradient
(solids4foam #553), so WP0 is the `linearUpwind grad(U)` result.

Question: with `viscousStressTranspose yes` the QM traction is meant to be
pimpleFluid's, yet QM-yes differs from partitioned by −2.34/−1.04/−0.44%
in `u_x` at x1/x2/x4, and QM-no by only −0.33/−0.29/−0.16%.

## D1: continue a QM state with the partitioned coupling

The converged partitioned x1 run was copied and its t = 3 s state replaced
by a QM state: the deformed fluid mesh points, the internal fields of U,
U_0, p, p_0, meshPhi, V0 and the solid D, D_0, D_0_0, D_0_0_0, pointD,
sigma, epsilon (both solids are linear elastic; partitioned boundary
conditions kept; Uf and phi removed so pimpleFluid rebuilds them;
`restart no` for the total-strain law). It then ran 1 s more (100 steps,
Δt 0.01, IQN-ILS, strict test). A control continued the partitioned state
itself.

| Start state | `u_x` start | t = 3.1 | t = 3.2 | t = 3.5 | t = 4 | `u_y` at t = 4 |
|---|---:|---:|---:|---:|---:|---:|
| partitioned (control) | 0.117231 | 0.117232 | 0.117235 | 0.117233 | 0.117233 | −0.013718 |
| QM vST yes | 0.114492 | 0.115706 | 0.116982 | 0.117328 | 0.117292 | −0.014492 |
| QM vST no | 0.116850 | 0.117017 | 0.117197 | 0.117296 | 0.117291 | −0.014505 |

- The control stays at its value (drift 2e-6, 0.002%).
- From either QM state the partitioned run returns to its own `u_x` within
  about 0.3 s, ending 0.05% above the control. The 2.3% QM-yes offset is
  not kept, so the partitioned discrete system does not have the QM-yes
  state as its steady state.
- Surprise: both restarts end at `u_y` −0.01449/−0.01450, 5.6% larger in
  magnitude than the control (−0.013718), and the same for both start
  states. The only remaining difference from the control is the interior
  fluid mesh, which keeps the QM mesh-motion layout (QM moves the fluid
  mesh as a solid; partitioned with velocityLaplacian increments). So
  `u_y` at x1 depends on the interior fluid mesh by ~5%, while `u_x` does
  not (0.05%). Compare QM-yes/QM-no `u_y` −0.014139/−0.014344: against the
  partitioned run on the same (QM) mesh, QM-no is 1.1% and QM-yes 2.4%
  smaller in magnitude, instead of the WP0 −0.56%/−0.13% against the
  partitioned run on its own mesh. The WP0 `u_y` comparison is therefore
  confounded by the mesh-motion layout and should not be used to judge vST.

## D3: interface traction on the same state

`postProcess -region fluid -func 'grad(U)'` (leastSquares, fvc::grad with
its boundary correction, so `n & grad(U)_b = snGrad(U)`) on each converged
state; traction per unit density, ν = 1, 24 interface faces, forces per unit
depth (`vst_diagnostic/d3.json`; D1 histories in `vst_diagnostic/d1_histories.csv`).

| State | max \|t_QM,yes − t_pimple\| | max \|t_pimple\| | mean \|transpose part\| | max \|tr grad U\| at wall | F_transpose x | F_viscous x | F_pressure x |
|---|---:|---:|---:|---:|---:|---:|---:|
| QM vST yes | 1.8e-15 | 9.13 | 0.403 | 0.852 | +0.167 | −6.368 | −8.622 |
| QM vST no | 1.8e-15 | 8.82 | 0.414 | 0.400 | +0.056 | −6.526 (no-term force) | −8.973 |
| partitioned | 1.8e-15 | 9.30 | 0.432 | 0.240 | −0.028 | −7.118 | −9.201 |

transpose part = `n & nu*dev2(T(grad(U)))`; QM yes = `nu*snGrad(U)` +
transpose part (`newtonIcoFluid::patchViscousForce`); pimple =
`n & nu*dev(twoSymm(grad(U)))` (`pimpleFluid::patchViscousForce`).

- **The two traction formulas are the same discrete expression.** On every
  state they agree to round-off (1.8e-15 against 9). This is algebraic:
  `dev(twoSymm(G)) = G + dev2(Gᵀ)` and `n & G_b = snGrad(U)`. D3 rules out
  the interface traction formula as the source.
- **The difference is in the QM velocity field next to the wall.** The wall
  value of tr(grad U), the discrete divergence of the cell-centred
  velocity, is 0.85 in the QM-yes state, 0.40 in QM-no and 0.24 in the
  partitioned state. The transpose part `n & dev2(Gᵀ) = n & Gᵀ − ⅔ tr(G) n`
  carries it straight into the traction. On this stationary no-slip wall
  the exact transpose part is zero. Its x force is +0.167 (1.1% of the
  total x load) for QM-yes and −0.028 (0.2%) for the partitioned run.
  With vST no, QM leaves this term out of the traction (and the residual),
  so its wall divergence error does not reach the solid.
- **Reading.** With vST yes, the QM momentum residual and traction take
  `nuEff*dev2(T(grad U))` from the QM cell-centred velocity. That velocity
  is not as close to divergence-free next to the wall as pimpleFluid's
  pressure-corrected velocity. The term adds a spurious wall force of order
  1% at x1, and it feeds back (QM-yes's own wall divergence, 0.85, is twice
  QM-no's, 0.40). The first-order decay of the QM-yes difference (2.34 →
  1.04 → 0.44%) fits an O(h) wall-divergence error. pimpleFluid has the
  same term, but on a velocity with a smaller wall divergence. So the
  formulations differ in the discrete continuity/velocity next to the wall
  (QM `interpolate(U)` face-flux continuity with momentum stabilisation,
  against pimpleFluid's Rhie–Chow pressure correction), not in the
  traction or the solid.
- This supports keeping `no` as the default for steady viscous cases. The
  Womersley level sweep (1e, both settings) tests whether the opposite
  trend there (vST yes closer to partitioned) persists under refinement.

## Not done / open

- D3 was evaluated on the converged states only. It was not run at x2 and
  x4. Repeating it there (cheap) would confirm that the wall divergence
  falls at first order in QM-yes.
- The `u_y` mesh-layout sensitivity (5.6% at x1) is a separate finding. It
  matters for any QM-against-partitioned `u_y` comparison on blob. It
  could be checked by D1 at x2/x4, or by running the partitioned case with
  the QM mesh-motion solver.

## Debugging and fix (23 October, after Philip: "yes is the correct solution")

Experiments on blobInTreacle x1/x2/x4 (mac-studio, WP0 set-up, `scripts/vst_debug.py`;
QM minus the WP0 partitioned u_x; Richardson limit from the three levels;
"wall force" = x force of the transpose part of the traction / total x load):

| Variant | x1 | x2 | x4 | Order | Limit vs part. | Transpose wall force x1/x2/x4 |
|---|---:|---:|---:|---:|---:|---|
| partitioned (IQN-ILS strict) | 0 | 0 | 0 | 2.26 | 0 | −0.18/−0.04/−0.004% |
| head, vST no | −0.33% | −0.29% | −0.16% | 1.89 | −0.06% | (not in traction) |
| head, vST yes | −2.34% | −1.04% | −0.44% | 1.67 | −0.08% | +1.1/+0.62/+0.33% |
| E1 vST yes + `interpolate(U) linear` | −1.84% | −0.89% | −0.40% | | | |
| E2 vST yes + zeroGradient interface p | −0.95% | −0.29% | −0.06% | | | |
| E3 vST yes + zeroGradient + linear | −0.50% | −0.15% | −0.03% | | | |
| fix 1: transpose term in the wall p gradient (63d2cc8a9) | −1.31% | −0.56% | −0.22% | 1.85 | −0.04% | +0.60/+0.39/+0.22% |
| fix 1 + zeroGradient + linear (E7) | −0.50% | −0.15% | −0.03% | 2.10 | +0.03% | +0.40/+0.24/+0.13% |
| **fix 2: wall value from the wall velocity (final)** | **−0.71%** | **−0.39%** | **−0.18%** | 1.88 | −0.06% | **0 (stationary wall)** |
| fix 2 + zeroGradient + linear (E9) | +0.31% | +0.11% | +0.06% | | | 0 |

Max |tr grad(U)| on the interface (cell-gradient boundary value):
partitioned 0.24/0.066/0.035; head vST yes 0.85/0.57/0.31; fix 1
0.50/0.34/0.20; fix 2 0.38/0.29/0.18 (x1/x2/x4).

1. **Defect 1, wall pressure gradient.** The fixedGradient interface
   pressure gets its gradient from the normal momentum equation in the
   adjacent cells (`updatePressureGradientBoundary`), with
   `laplacian(nuEff,U) - ddt(U)` only: with vST yes the residual also has
   `div(nuEff*dev2(T(grad(U))))`, so the wall pressure was inconsistent with
   the momentum equation. Fixed in 63d2cc8a9 (the term added; Astra
   independently identified the same omission). This halves the error.
2. **Defect 2, wall value of the transpose stress.** Taken from the
   boundary value of `grad(U)`, the transpose traction's tangential
   derivatives come from the adjacent cell values. In the partitioned
   solution the tangential (∂_t u_n, +0.30 at x1) and normal (∂_n u_n,
   −0.37) parts nearly cancel, as continuity requires; in QM the normal
   part is almost zero (−0.06) and the −⅔ tr term adds −0.20, so a
   spurious force of 0.6% (x1) remains, decaying at order 0.6–0.8. On a
   no-slip wall, n & grad(U)^T = grad(U & n) depends on the wall velocity
   only. Fix 2 sets the wall value from a least-squares surface gradient of
   the wall velocity (zero for a rigid translation, exact for a linear wall
   velocity, wedge images for the axisymmetric circumferential term). A
   first version with point averages was rejected in review (curvature,
   wedge, foam-extend); the least-squares version passes the reviewer's
   counter-examples exactly.
3. **What remains** is not an inconsistency: all series extrapolate to
   within 0.08% of the partitioned limit, and with the partitioned
   pressure condition and interpolation the sign flips (+0.31/+0.11/+0.06%).
   The remaining difference is the partitioned `zeroGradient` interface
   pressure (first order), the face interpolation of U and the face-flux
   construction (product interpolation, ddtCorr; Astra's list). QM's
   near-wall cell velocity still has a larger discrete divergence than
   pimpleFluid's pressure-corrected one, but it no longer reaches the
   traction.
4. **Other cases** (local, final build unless stated): womersleyTube m2
   n200 QM minus RN, wall phase −2.9e-5 rad, attenuation −1.3e-5, amplitude
   −1.5e-4 (vST no: −4.8e-4, −4.1e-4, −3.3e-4); ringAddedMass unchanged
   (strong m2 n100 ratio −0.0039%); serial and parallel runs agree. FSI3
   conformal 1x (Mx, fix 1 only): u_y amplitude −2.1%, drag mean −2.7%,
   u_x mean −3.4% against R0 (coarse mesh). The final-build MeluXina
   verification (Womersley m1/m2/m4 n200, ring 3×3 n100, FSI3 1x) is in
   `../m-runs-a/` when complete.

Astra consultations: `m-runs-a-work/astra/answer1.md` (diagnosis),
`answer2.md` (fix 1 review, no blocking issue), `answer3.md` (fix 2 first
version, blocking issues, resolved), `answer4.md` (fix 2 final).
