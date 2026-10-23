# WP1 findings (agent A): ringAddedMass 1a–1d, 1f; womersleyTube 1e

Run on 23 October 2026 on MeluXina, account p201136, as farm jobs of
serial runs (5377679, 5377777), solids4foam `85b0c1de6`
(`v2.4-1103-g85b0c1de6`), OpenFOAM v2512, GCC 13.3, PETSc 3.22.0. No
solver code changes. Every run completed. Rows: `runs.csv`, `qois.csv`,
`provenance/`. Timings are indicative (up to 77 serial runs per node).

Set-up: `viscousStressTranspose` set explicitly (`no` unless stated);
schemes as the tutorials' partitioned files (ring and Womersley already
match: Gauss linear, leastSquares, `backward`); partitioned with
`requireAllResidualMeasures yes`, IQN-ILS `couplingReuse 0`.
Tolerances: ring QM tutorial (snes 1e-6/1e-6, ksp 1e-4), with a tight
check (1e-8/1e-8/1e-6) at m2 n100 changing ω by ≤ 4e-9 and the loss by
≤ 1e-8 (B1 met); Womersley QM tight, as WP0.

## 1a ring QM sweep (3 levels × mesh 1/2/4 × 25/50/100/200 steps)

Wet/dry frequency-ratio error (%) against the exact ratio (dry ring:
standard solid, same mesh and steps):

| Level | Mesh | n25 | n50 | n100 | n200 |
|---|---|---:|---:|---:|---:|
| weak | 1 / 2 / 4 | −0.0043 / −0.0004 / +0.0002 | −0.0035 / −0.0004 / −0.0001 | −0.0028 / −0.0003 / −0.0000 | −0.0022 / −0.0001 / +0.0000 |
| moderate | 1 / 2 / 4 | −0.0245 / −0.0036 / −0.0004 | −0.0206 / −0.0028 / −0.0004 | −0.0165 / −0.0018 / −0.0002 | −0.0134 / −0.0010 / +0.0000 |
| strong | 1 / 2 / 4 | −0.0468 / −0.0074 / −0.0012 | −0.0397 / −0.0057 / −0.0009 | −0.0324 / −0.0039 / −0.0005 | −0.0267 / −0.0025 / −0.0001 |

- 2.00 Newton iterations per step everywhere (max 3 on a few m4 steps).
- Mesh 2 reproduces the README's pre-#597 QM table to 1e-5 in ω
  (strong n25/50/100: 0.79935/0.81246/0.81601 against 0.79936/0.81246/0.81602).
- Amplitude loss: the dry ring's BDF2 loss (2.6%, 0.36%, 0.046%, 0.006% per
  period at m2) plus a coupling part that does not depend on Δt and is
  ≤ 0.09% per period: −0.09/−0.004/+0.045% (strong, m1/m2/m4), i.e. a
  slight amplitude gain on m1 turning into a small loss on m4. Not
  interpreted further (possibly the resolved viscous layer at ν = 1e-7).

## 1d strong level, mesh 2, standard solid (accuracy and iterations)

| Steps | Coupling | ω | Ratio error | Loss/period | Iter./step (max) | Wall (s) |
|---:|---|---:|---:|---:|---:|---:|
| 25 | QM | 0.79935 | −0.0074% | 2.57% | 2.00 (2) | 60 |
| 25 | IQN-ILS | 0.80042 | +0.126% | 3.77% | 4.23 (6) | 81 |
| 25 | RN | 0.79936 | −0.0058% | 2.59% | 46.5 (144) | 444 |
| 50 | QM | 0.81246 | −0.0057% | 0.358% | 2.00 (2) | 97 |
| 50 | IQN-ILS | 0.81333 | +0.101% | 1.50% | 5.09 (8) | 151 |
| 50 | RN | 0.81244 | −0.0085% | 0.379% | 37.3 (63) | 572 |
| 100 | QM | 0.81601 | −0.0039% | 0.048% | 2.00 (2) | 156 |
| 100 | IQN-ILS | 0.81632 | +0.033% | 1.15% | 5.24 (8) | 260 |
| 100 | RN | 0.81598 | −0.0085% | 0.062% | 11.7 (20) | 360 |

- IQN-ILS ω and ratio match the README (legacy test) to 1e-5; the strict
  test adds iterations (4.23/5.09/5.24 against 3.86/4.63/4.92).
- Robin–Neumann with the standard solid agrees with QM to 0.004% in the
  ratio but needs 12–47 iterations per step, many more than with the
  high-order solid (12.3 at n100 in the README).

## 1b zero-gradient interface pressure (n100)

Ratio error (%), fixedGradient (1a) → zeroGradient:
moderate m1/m2/m4 −0.0165/−0.0018/−0.0002 → −0.183/−0.109/−0.059;
strong −0.0324/−0.0039/−0.0005 → −0.336/−0.199/−0.108. First order in the
mesh, as the README's "before" numbers (−0.194/−0.117/−0.063,
−0.355/−0.213/−0.115), and 5–6% smaller in magnitude (those also contain
the old face-velocity change). Newton count unchanged (2.00).

## 1c non-conformal interface (AMI), n100

Solid with 32f (coarser) and 72f (finer) circumferential cells against the
fluid's 48f, interpolated and conservative traction transfer, dry ring on
the same solid mesh. Ratio errors are all within 0.015% (largest: strong m1
finer solid, −0.0147/−0.0136%), from m2 within 0.005%, and m4 within
0.0017%; conservative and interpolated differ by ≤ 0.0025%. 2.00 Newton
iterations per step in every run. On m1 the non-conformal runs are closer
to the exact ratio than the conformal one (the dry ring with the same solid
mesh cancels the solid's error).

## 1e womersleyTube (QM vST no and yes, RN, IQN-ILS; m2 n50 from WP0)

Errors against the exact linear solution, and QM minus RN (wall mid
station; phase in rad):

| Cell | RN wall amp | RN wall phase | QM no − RN: amp / phase / atten. | QM yes − RN: amp / phase / atten. | IQN − RN amp |
|---|---:|---:|---|---|---:|
| m1 n200 | −1.03e-2 | −2.37e-3 | −0.8e-4 / −5.2e-4 / −7.2e-4 | +0.5e-4 / +0.8e-4 / −1.1e-4 | +3.8e-4 |
| m2 n200 | −2.19e-3 | −1.48e-3 | −3.3e-4 / −4.8e-4 / −4.1e-4 | −1.7e-4 / +0.1e-4 / +0.4e-4 | +1.7e-4 |
| m4 n200 | −1.74e-4 | −1.15e-3 | −3.6e-4 / −4.8e-4 / −3.5e-4 | −1.8e-4 / −0.2e-4 / +0.3e-4 | −0.7e-4 |
| m2 n50 | +5.28e-3 | −6.12e-3 | −3.4e-4 / −4.8e-4 / −4.1e-4 | −1.8e-4 / +0.2e-4 / +0.5e-4 | +1.9e-4 |
| m2 n100 | −6.63e-4 | −2.34e-3 | −3.3e-4 / −4.8e-4 / −4.0e-4 | −1.7e-4 / +0.1e-4 / +0.4e-4 | +2.2e-4 |
| m2 n400 | −2.58e-3 | −1.28e-3 | −3.2e-4 / −4.8e-4 / −4.0e-4 | −1.7e-4 / +0.1e-4 / +0.5e-4 | +1.8e-4 |

- **vST no leaves a mesh-independent wall offset.** The QM-no wall phase
  is 4.8e-4 rad behind RN at every mesh and step, and the wall amplitude
  offset does not fall with refinement (−0.8, −3.3, −3.6e-4 on m1/m2/m4).
  At m4 the phase offset is 40% of RN's own phase error (1.15e-3), so it
  would show in a mesh study. This confirms the newtonIcoFluid README
  claim that WP0 (m2 n50 only) could not test.
- **vST yes removes the phase and attenuation offsets** (≤ 2e-5 and ≤ 5e-5
  from m2). Its wall amplitude stays 1.7–1.8e-4 below RN from m2 to m4,
  which is the size of the RN/IQN-ILS spread (−0.7 to +2.2e-4). The
  profile, flow and wave-speed errors agree with RN to within 3e-4 for
  both settings.
- All offsets are independent of Δt (m2 n50–n400 identical to 1e-5), so
  they are spatial: the wall traction or interface treatment.
- Together with the blob diagnostic (`../wp0/vST_diagnostic.md`: with vST
  yes a first-order wall-divergence error in the steady blob case), the
  two cases still pull in opposite directions; at the finest levels the
  Womersley vST-no offset (4.8e-4 rad, mesh-independent) is the one that
  does not converge.
- Cost: QM 2.00 Newton/step; RN 10.9–17.7 and IQN-ILS 13.0–16.1
  iterations/step; QM wall time 0.5–0.8 of RN on the same farm node.

## 1f BDF2 start-up

The QM runs start BDF2 with one Euler step. Ring: refitting every 1a run
with the first period excluded changes ω, the wet/dry ratio and the loss by
at most 2.2e-5 (`1f/ring_startup_window.csv`). Womersley: the driver
analyses periods 5–6 of 6; the periodicity (change between the last two
periods) is 6e-6–7e-5 in every run, the size of the RN/IQN-ILS values. No
start-up effect is visible in either case, so no second-order start was
run.

## Cost

Allocations (MeluXina bills whole nodes; every job got a full node):
batch-1 farm 2.1 node-hours; smoke tests 0.2. Solver core-hours of the
WP1 runs: 16.4 (1e 10.3, 1a 2.6, 1c 2.6, 1d 0.5, 1b 0.4).
