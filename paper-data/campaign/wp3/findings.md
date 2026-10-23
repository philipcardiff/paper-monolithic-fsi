# WP3 findings: robustness maps (3a, 3b)

Settings, failure criterion and caps: `README.md`. Data: `3a/` and `3b/`
(`runs.csv`, `qois.csv`, `provenance/`, draft maps `map_3a.pdf`,
`map_3b.pdf`). Code `85b0c1de6`; QM rows are `pre-vST-fix` (to be rerun
with the fixed build).

## 3a ringAddedMass (MeluXina 5377695)

79/80 pass. The only failure is Robin–Neumann at the strong level with 12
steps per period (200-iteration cap at step 10). Mean iterations per step:
QM 2.0 everywhere, IQN-ILS 3.0–6.1, Aitken 3.2–10.2, RN 3.0–42. All
couplings agree on ω to ~0.1% (`qois.csv`); the +6.3% error at 200 steps
is the standard solid at mesh 2, the same for every coupling. On this case
the partitioned couplings (with predictor and the strict test) survive even
μ ≈ 100: the map separates them by iterations, not by failure.

## 3b collapsibleChannel (XenoSim 13279, 4.6 h, 55.7 core-hours CPU)

| Coupling | Passes (of 20) | Failures |
|---|---:|---|
| QM | 15 | Δt 0.025: all five densities stop at t = 0.275 s in the fluid mesh-motion SNES (`mesh`, `DIVERGED_LINEAR_SOLVE` of the pseudo-solid motion solver; the coupled Newton solve converged in 3 iterations per step up to then) |
| RN | 11 | ρs/ρf 0: floating-point exception on the first coupling iteration at every Δt (the Robin coefficient ∝ wall density vanishes; `nan`); ρs/ρf 0.01: cap at Δt 0.025, 0.00625, 0.003125 |
| IQN-ILS | 9 | cap at ρs/ρf ≤ 0.1 for Δt ≤ 0.00625 (ρs/ρf 0: Δt ≤ 0.0125), and at ρs/ρf 1, Δt 0.003125 (t = 0.23 s), as in the verification README |
| Aitken | 7 | cap at every Δt for ρs/ρf ≤ 0.1, except ρs/ρf 0 at Δt 0.025 |

QM needs 2.0–3.0 Newton iterations per step in every passing cell,
independent of the density; the partitioned couplings need 8–98 coupling
iterations per step where they pass. Partitioned failures come within the
first few steps (cap at the 200-iteration limit); the smaller the time
step, the earlier the failure, the classical added-mass trend.

Trough of the wall midpoint (ρs/ρf 1, against oomph-lib): partitioned
−1.79/−0.78/−0.51/−0.43% at Δt 0.025/0.0125/0.00625/0.003125; QM
−0.97/−0.71/−0.65% (Δt 0.0125 → 0.003125). QM and partitioned differ by
about 0.2 points at the small steps (different solid formulation —
velocity TL vs displacement TL with linear reconstruction — and the
conservative AMI traction; QM `pre-vST-fix`). ρs/ρf 0 against the massless
reference: QM −0.95/−0.70/−0.64%.

## Open points

- The QM Δt 0.025 failures are mesh motion, not coupling; a more robust
  mesh-motion set-up (or Euler start) might remove them. Not investigated
  (no QM runs until the vST fix).
- RN is undefined at ρs = 0 with the secant Robin coefficient; the map
  should say "not applicable" rather than "failed" if Philip prefers.
