# Gate G1: campaign specification

Coordinator report, 22 October 2026. Branch `evidence/campaign-g1`. Every
number below has its source in `paper-data/campaign/<stream>/`.
Code for all phase-B runs: solids4foam `257b2e564`
(`v2.2-1692-g257b2e564`, PR #233 head on 20 Oct), OpenFOAM v2512, on two
machines that are never compared for timing:

| Machine | PETSc / HYPRE / MUMPS | Flags | Used for |
|---|---|---|---|
| MeluXina (EPYC 7H12, exclusive nodes, bound) | 3.22.0 / 2.31.0 / 5.7.3 | `-O2 -fno-tree-vectorize -march=znver2` | B0, B1 ring, B2 step 1 |
| XenoSim (EPYC 9684X, shared, load ~185/192, unbound) | 3.24.1 / 2.33.0 / 5.8.1 | `-O3` | B1 cav/tube, B2 step 2 |

MeluXina project p201287 used 1 376 of 1 389 node-hours in October, so the
rest of phase B ran on XenoSim (Philip, 21 Oct). XenoSim clock times are
indicative: ≈10% differences are noise there.

## Phase B results

**B0 (smoke, `b0/findings.md`).** Passed. ringAddedMass 2.00 Newton/step
(serial, 4 ranks), as in its README. Cavity L1 Dy = −0.201546 m,
Fy = −5.122611 N, identical in serial, on 4 ranks and in every repeat.
Solver-time spread over 3 repeats ≤ 0.8%.

**B1 (solid-block preconditioner, `b1/findings.md`).** Criterion: the
cheapest PC per case (Philip, 21 Oct). Window = 50 steps after a spin-up;
all configurations 2.00 Newton/step.

| Case | Ranks | S0 `redundant`+LU (s) | S1 BoomerAMG (s) | S2 `bjacobi`+LU (s) | Cheapest |
|---|---:|---:|---:|---:|---|
| ringAddedMass (MeluXina) | 1 / 4 | **39 / 17** | 54 / 33 | – / 32 | S0 |
| cavityFlexibleBottom L3 | 1 / 4 / 16 | **352 / 99 / 42** | 386 / 109 / 48 | – / 137 / 59 | S0 |
| 3dTube L2 | 4 / 16 | 1 194 / 1 296 | **279 / 108** | 337 / 132 | S1 |

S0 does not scale on 3dTube: every rank factorises the whole solid block,
so time stays flat from 4 to 16 ranks and memory grows (9.2 → 24.8 GB,
against 6.0 GB for S1).

*Accuracy at the revised test (§10, 21 Oct).* Tight references S0ref and
S1ref (`snes_rtol` 1e-10, `ksp_rtol` 1e-8) agree with each other in every
written digit. Against them, at the tutorial tolerances, every
configuration meets "≤ 5% of the discretisation error". Cavity Uy and Fy
differ by ≤ 1.9e-7, against thresholds of 3.5e-4 and 2.9e-5. 3dTube
u_r(A) and u_z(A) differ by 4.6e-6, against 2.5e-5 and 9.3e-4. The choice
is therefore decided by cost: **S0 for the 2D cases, S1 for 3dTube**. At
reference tolerances S1 is again 7× cheaper on 3dTube (227 s on 16 ranks
against 1 573 s on 4). Caveat: the 3dTube window ends before the u_r peak
(7.2 ms), so its `snes_rtol` 1e-4 is confirmed only for the early pulse.
The full-run check belongs in R5.

**B2 (collapsibleChannel with AMI, `b2/findings.md`).** The static solid
needs 640×8 cells to be within 1% (−0.22%). Monolithic fluid level 2,
Δt = 0.00625 s, `ddt(U) Euler` (the README's scheme; submitted before the
`backward` decision):

| Interface | Trough error vs oomph-lib | Newton/step | Krylov/Newton | Clock |
|---|---:|---:|---:|---:|
| conformal 160×8 (directMap) | −4.28% (README −4.1%) | 2.70 | 286 | 4 420 s |
| AMI, 640×8, conservative traction | −1.91% | 2.59 | 272 | 4 694 s (+6%) |

AMI works and removes the solid-mesh limit at no convergence penalty. The
handoff rule ("≤ 1% → accuracy case, otherwise robustness-only") gives
**robustness-only**: the remaining −1.9% is the fluid mesh and time step
(README level-2 time study: 0.5%), not the solid. See Q3.

**B3 (estimate only, `b3/estimate.md`).** blobInTreacle monolithic temporal
study (Δt 0.25 → 0.03125 s, 60 steps): < 0.1 core-h; all of R6 2–12 core-h.
Its fluid `ddt(U)` must change Euler → `backward`. Block with flexible tail:
3–3.5 person-days of set-up plus ~20–60 core-h (a guess; the book was not
available to me). Recommendation: run blobInTreacle; build the block with
tail only if the paper needs a self-excited oscillation case beyond FSI3.

**Suspected solver defect (§9, `b1/issue_mesh_motion_restart.md`).** A
restarted monolithic run fails at its first step: the fluid mesh-motion
SNES starts at a residual 1000× too large (3.41 against 3.3e-3) and its
linear solve does not converge, with or without the mesh-motion restart
fields. No phase-B result depends on restarts (windows ran from t = 0).
**The timing protocol does**: its windows start from a restart.

## Proposed final run matrix

Section 4 of the handoff, minus what §10 dropped (stiffening and route-B
ablations; no runs for mokLidDrivenCavity, beamInCrossFlow, membraneRoof,
perpendicularFlap), plus the §10 additions (5% tolerance calibration,
`viscousStressTranspose` yes/no for blobInTreacle and Womersley m2). Costs:
`campaign/G1_cost_estimate.md` (sources per row; [A] = assumption).

| Stream | Core-h | Dominant item |
|---|---:|---|
| R1 ring, Womersley, ablations | 7–22 | ring non-conformal study twice (AMI traction ablation) |
| R2 cavityFlexibleBottom L1–L4 | 22–51 | monolithic L4 (55–80 s/step serial) |
| R3 robustness maps | 12–60 | collapsibleChannel 20 cells × 4 schemes |
| R4 FSI3 work–precision | 170–830 | IQN-ILS on the conformal 4x mesh (never run) |
| R5 3dTube | 320–1 315 | monolithic L3 to 20 ms; L3 scaling (optional, 115–800) |
| R6 blobInTreacle | 5–20 | timed mesh study |
| R7 foilInWind | 3–10 | Δt = 0.0025 s |
| **Total** | **≈ 540–2 300** | R4 + R5 ≈ 90%; without L3 scaling ≈ 425–1 500 |
| Block with tail (if approved) | +20–60 | plus 3–3.5 person-days |

Correctness runs (any machine): ≈ 370–1 200 core-h. Timing runs (one
machine, exclusive): ≈ 170–1 100 core-h of compute, but **16–80 node-hours
of wall time; billed per 128-core MeluXina node that is ≈ 2 000–10 000
core-h**, since most timing runs use 1–16 ranks. Without working restarts,
R4's timing windows become full runs (+400–1 600 core-h, not in the range).

## Settings to freeze

| Case | `snes_rtol`/`stol` | `ksp_rtol` | Solid block | Fluid `ddt(U)` at 257b2e564 → campaign |
|---|---|---|---|---|
| ringAddedMass, womersleyTube | 1e-6 → per 5% rule (≈1e-8 expected) | 1e-4 | S0 | backward |
| collapsibleChannel | 1e-6 | 1e-4 | S0 | Euler → backward |
| cavityFlexibleBottom | 1e-6 (meets the 5% rule at L3) | 1e-4 | S0 | Euler → backward |
| TurekHron2006 FSI3 | 1e-6 | 1e-4 | S0 (2D) | backward |
| 3dTube | 1e-4, lag 8 (meets the rule in the B1 window; full-run check in R5) | 1e-3 | **S1 BoomerAMG** | Euler → backward |
| blobInTreacle | 1e-6 | 1e-4 | S0 | Euler → backward |
| foilInWind (3D) | 1e-4 | 1e-4 | S0 now; S1 if its solid block is large (not tested) | backward |

Common to all: `snes_mf_operator`, LGMRES, Schur fieldsplit for the fluid,
options as in each tutorial's `system/fvSolution.monolithic` otherwise.
S1 = the membraneRoof BoomerAMG settings (HMIS, ext+i, P_max 1, trunc 0.3).
No case is known to need Euler; `backward` ran without problems in B1
(cav, tube). Tolerances become final only after the per-case 5% check,
which is part of each R stream.

## Items for the fixed code version (formerly the A3 tag list)

With the 21 Oct decisions there is no tag before the cases run; these
still apply to the version Philip fixes later: include `f356c3242`
(cavity rerun) and `b157ecaf3` (foilInWind Δt/4); remove the physics-PC
code and the "Physics PC inner solvers" blocks; v2.4 does not contain the
coupling; drivers do not record the commit or library versions, so every
run uses `campaign/scripts/provenance.py`. Add: **the restart defect**,
which the timing protocol needs fixed.

## Open questions for Philip

1. **Restart defect:** fix before the timing runs (recommended), or time
   windows from t = 0 (R4 +400–1 600 core-h)?
2. **Timing machine:** exclusive MeluXina nodes cost 2 000–10 000 core-h for
   mostly 1–16-rank timing runs. A smaller dedicated machine for the small
   cases, or accept the charge?
3. **collapsibleChannel:** robustness-only (the rule), or one more run with
   AMI at fluid level 3 to see if the trough error reaches 1%
   (≈ 3–6 core-h)?
4. **Block with flexible tail:** build it (3–3.5 days + 20–60 core-h) or not?
5. **3dTube L3 strong scaling** (115–800 core-h): keep or drop?
6. The B1 cav/tube runs used `257b2e564`; §10 asks for a rebuild from the
   branch head before they are reused for the paper. I propose to rebuild
   on XenoSim and repeat only the chosen configuration per case
   (≈ 1 core-h).

The campaign stops here for G1.
