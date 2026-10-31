# womersleyTube: quasi-monolithic vs Robin-Neumann velocity profile (31 Oct 2026)

Runs on MeluXina (`/project/home/p201136/philip-ma`): QM after the traction
correction `runs-rfix/rf-wom-qm-*` (1252bd2e5), QM before `runs/ma-wom-qm-vstno-*`,
RN `runs/ma-wom-rn-*`, IQN-ILS `runs/ma-wom-iqn-*`. Script:
`womersley_profile_diag.py` (reuses the tutorial driver's `analyse`).

## What the paper's "profile" number is
`profile` = max over the cells at x ~ L/2 of |u1 - u1_exact| / max|u1_exact|
(first harmonic over the last 2 periods). The QM - RN value in the paper
(-2.4 to -3.2e-4) is the difference of two error norms: the QM profile is
closer to the exact solution (m2: 4.65e-3 vs 4.96e-3; m4: 9.60e-4 vs 1.20e-3).

## Profile difference itself (first harmonic, / peak)
| cell | QM-RN max (r/R) | axis | wall cell | IQN-RN max |
|---|---|---|---|---|
| m1-n200 | 6.1e-4 (0.85) | 4.8e-5 | 4.8e-4 | 1.3e-4 |
| m2-n100 | 7.1e-4 (0.93) | 4.1e-5 | 4.5e-4 | 5.3e-5 |
| m2-n200 | 7.1e-4 (0.93) | 3.9e-5 | 4.5e-4 | 3.7e-5 |
| m2-n400 | 7.1e-4 (0.93) | 3.7e-5 | 4.5e-4 | 5.1e-5 |
| m4-n200 | 7.9e-4 (0.96) | 3.9e-5 | 4.4e-4 | 1.1e-4 |

- Maximum always in the second cell from the wall; independent of mesh and step.
- Unchanged by the traction correction (QM before: 6.1/6.9/6.9/6.9/7.6e-4).
- Same in each of the last two periods (m2-n200: 7.09e-4 both): not start-up.
- Snapshot at t = 300 (m2/m4): QM - RN is smooth along x (no odd-even
  pattern), +2.1 to +2.8e-4 in the core and -4 to -6e-4 in the last three
  cells: flow moves from the wall layer to the core, so the flow rate
  (face-interpolated U at the mid-plane) agrees to 4e-5.
- After the correction the wall radial and axial displacement, pressure and
  flow rate agree to 6e-5 or better.

## Set-up differences checked
Same mesh, nu, rho, inlet/outlet conditions, fvSchemes (div, laplacian,
interpolation; ddt backward), sampling (`cell`, midPoint). Differences: fluid
model (newtonIcoFluid with Rhie-Chow pressure stabilisation vs pimpleFluid),
wall velocity condition (fixedValue set by the coupling vs
`elasticWallVelocity` from the mesh motion), solid model (velocity vs total
displacement), mesh motion law. Not isolated; candidates that do not vanish
with h and dt: the fluid wall velocity condition.
