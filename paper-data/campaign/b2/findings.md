# B2: collapsibleChannel with a non-conformal (AMI) interface

Code `257b2e564` (`v2.2-1692-g257b2e564`). Set-up: `scripts/b2_setup.py`
(imports the tutorial's verification driver); jobs: `jobs/b2_static.sh`,
`jobs/b2_mono.sh`; post-processing: `scripts/b2_post.py` → `runs.csv`;
per-run status: `status.txt`; provenance: `provenance/<run_id>.json` and
`provenance/<run_id>.run_meta.json`.

Question: the quasi-monolithic coupling needs matching interface meshes
unless AMI is used. Its collapsibleChannel error (−4.1% at fluid level 2,
README) is limited by the linear solid on the conformal 160 × 8 mesh. Does
AMI let the solid be refined on its own, and at what cost?

## Step 1: solid mesh that resolves the wall (static wall)

Partitioned linear solid, static external pressure, wall midpoint against the
static oomph-lib beam (−0.143628 m). MeluXina, job 5364293.

| Solid mesh | wallMid (m) | Error |
|---|---:|---:|
| 320 × 8 | −0.142024 | −1.12% |
| 640 × 8 | −0.143311 | −0.22% |
| 1280 × 8 | −0.143410 | −0.15% |
| 640 × 16 | −0.143226 | −0.28% |

640 × 8 is the coarsest mesh within 1%; chosen for step 2. The README gives
6.0% too stiff for 160 × 8. The remaining ~0.2% does not fall with length
(1280 × 8) or thickness (640 × 16) refinement; it is below what matters here.

## Step 2: monolithic FSI, fluid level 2, Δt = 0.00625 s, ρs/ρf = 1, t = 0–1.5 s

XenoSim (shared node, load ~185/192, not exclusive, no core binding;
clock times indicative only), serial, jobs 13024 and 13025, run side by
side. Fluid `ddt(U) Euler` (tutorial; the same scheme as the README values).

| Run | Interface | Trough (m) | vs oomph-lib (−0.21573 m) | Newton/step (max) | Krylov/Newton | Clock (s) |
|---|---|---:|---:|---:|---:|---:|
| 160 × 8 conformal | directMap | −0.20650 | −4.28% | 2.70 (3) | 286 | 4 420 |
| 640 × 8 | AMI, conservative traction | −0.21162 | −1.91% | 2.59 (3) | 272 | 4 694 |

(Sources: `runs.csv`, `status.txt`.)

- **Baseline reproduced.** The conformal run's trough is −0.20650 m against
  the README's −0.20691 m (−4.1%, macOS, older commit), 0.2% apart.
- **AMI works and removes the solid-mesh limit.** With the 640 × 8 solid the
  error falls from −4.3% to −1.9%, better than the conformal fluid level 4
  run in the README (−2.4%, 320 × 8 solid, 7 901 s on macOS), at fluid
  level 2.
- **Convergence unchanged.** Newton iterations per step (2.59 vs 2.70, max
  3 in both) and Krylov iterations per Newton (272 vs 286) are no worse with
  AMI.
- **Cost.** +6% clock time on the same (shared) node with four times the
  solid cells; indicative only, as XenoSim was loaded.
- The remaining −1.9% is not the solid (static wall at 640 × 8: −0.22%).
  It is the fluid mesh and time step: the README's level-2 time study moves
  the trough by 0.5% from Δt 0.00625 to 0.003125 s, and the fluid is at
  level 2.

## Caveats

- Euler `ddt(U)` (runs submitted before the 20 Oct decision to use
  `backward`, then kept for comparability with the README values).
- Different machine from step 1 (MeluXina) and from the README (macOS);
  costs are compared only between the two step-2 runs.
