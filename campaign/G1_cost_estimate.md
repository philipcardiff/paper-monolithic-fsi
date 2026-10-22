# Core-hour estimate for the proposed final run matrix (R1–R7)

Estimate only; nothing was run. Scope: `paper-fsi-verification/HANDOFF.md`
Section 4, as amended by the decisions log (`paper-monolithic-fsi`
`origin/campaign/handoff:campaign/HANDOFF.md` §10, 20–21 Oct): no
mesh-motion ablation, no route-B ablations, no runs for mokLidDrivenCavity,
beamInCrossFlow, membraneRoof or perpendicularFlap; `backward` fluid `ddt(U)`;
per-case tolerances under the 5% rule (+~40% for ring/Womersley);
`viscousStressTranspose` yes/no for blobInTreacle x1/x2/x4 and Womersley m2.

"Core-h" = ranks × wall time. Abbreviations: README = the case's
`verification/README.md` under
`~/OpenFOAM/philipc-v2512-qmpaper/solids4foam/tutorials/fluidSolidInteraction/`
(at 257b2e564 unless stated); CAMP = `paper-monolithic-fsi/paper-data/campaign/`.
**[A]** marks an assumption (no measured basis).

## Summary

| Stream | Core-h (low–high) | Correctness | Timing | Dominant item |
|---|---:|---:|---:|---|
| R1 ring + Womersley, ablations | 7–22 | 5–18 | 2–4 | ring non-conformal study run twice (AMI-traction ablation) |
| R2 cavityFlexibleBottom | 22–51 | 19–31 | 3–20 | monolithic level 4 (55–80 s/step serial) |
| R3 robustness maps | 12–60 | 12–60 | – | collapsibleChannel 80-cell map (to t = 1.5 s) |
| R3 cavity L3 map (optional) | +5–21 | +5–21 | – | monolithic Δt = 0.0625 s (3 200 steps × 7 s) |
| R4 FSI3 work–precision | 170–830 | 150–740 | 21–90 | partitioned IQN-ILS on conformal 4x (never run) |
| R5 3dTube | 320–1 315 | 180–335 | 140–980 | monolithic L3 to 20 ms (160–300); L3 scaling if restarts are fixed (115–800) |
| R6 blobInTreacle | 5–20 | 4–10 | 1–10 | timed mesh study (B3 estimate) |
| R7 foilInWind | 3–10 | 3–10 | – | monolithic Δt = 0.0025 s to 0.2 s |
| **Total** | **≈ 540–2 300** | **≈ 370–1 200** | **≈ 170–1 100** | R4 + R5 are ≈ 90% |
| Block with flexible tail (only if approved) | +20–60 | +20–60 | – | B3 guess, plus 3–3.5 person-days set-up |

- Without the optional 3dTube L3 strong scaling: **≈ 425–1 500 core-h**.
- **Correctness** runs (can run anywhere): ≈ 370–1 200 core-h, ~55–70% of the
  total. **Timing** runs (one machine, exclusive nodes): ≈ 170–1 100 core-h of
  compute.
- **Billing caveat for timing.** On exclusive nodes (MeluXina CPU node = 2×
  EPYC 7H12, 128 cores) the charge is node-hours, not ranks × hours. The timing
  items sum to roughly **16–80 node-h of wall time, i.e. ≈ 2 000–10 000
  allocated core-h**, because most timing runs use 1–16 ranks on a 128-core
  node (R1/R2 serial timings, R5 1–8-rank scaling points). This, not the
  compute, dominates the allocation unless small timing runs are moved to a
  dedicated workstation-class machine or several are packed per node (which
  breaks exclusivity).
- **Restart failure** (`CAMP/b1/issue_mesh_motion_restart.md`) is the largest
  single cost lever: without restarts, every timing window must run from t = 0
  (R5 windows ×4–7, R4 two-period windows become near-full runs, adding
  ≈ 400–1 600 core-h to R4).

## Machine factor used throughout

Most recorded times are from an Apple M1 Ultra (often shared) or XenoSim at
~185/192 load. Same case, same code, different machine: collapsibleChannel
monolithic fluid level 2, Δt = 0.00625, to 1.5 s = 2 008 s (README,
"Quasi-monolithic coupling" table, macOS) vs 4 420 s (`CAMP/b2/runs.csv`,
`b2-mono-F2-S160x8-directMap`, XenoSim loaded). Hence **[A] machine factor 1–2.2**
applied to M1 numbers in the high bound where noted.

## R1. Exact solutions and ablations

| Run | Couplings × repeats | Cost basis | Core-h |
|---|---|---|---:|
| ring `--study monolithic` rerun: 3 levels × 25/50/100 steps/period, factor 2 (21 runs) | mono + IQN-ILS (+ dry) × 1 | ring README "Quasi-monolithic Newton against IQN-ILS" table: Time column sums to ≈ 930 s (mono 480 s, IQN 453 s; dry [A] ~120 s); ×1.4 tol on mono; ×1–2.2 machine | 0.3–1 |
| ring `--study nonconformal`: factors 1/2/4 × solid cells {conformal, 32f, 72f} × 3 levels + dry (36 runs, `reference/…references.json` l. 24–30), twice for `conservativeTractionTransfer` (2nd arm only the 24 non-conformal runs) | mono × 1 | **No recorded time.** [A] mono 100 steps/period on factor 2 ≈ 90 s (README table, strong/100: 91 s), factor 1 ≈ 25 s, factor 4 ≈ 4–8× factor 2; ×1.4 tol; ×1–2.2 | 3–9 |
| Interface-pressure ablation (zero gradient), factors 1/2/4 × 3 levels | mono × 1 | as above [A] | 0.5–1.5 |
| womersleyTube `--monolithic` (7 runs) | mono (+IQN-ILS m2 n100) × 1 | Womersley README l. 320–321: "seven runs take 1.3 to 18 minutes each in serial"; [A] sum 0.7–2.1 h; ×1.4 tol | 1–3 |
| Womersley m2 `viscousStressTranspose` yes/no | mono × 2 | inside the 1.3–18 min range | 0.1–0.6 |
| 5%-rule tolerance calibration (tight `snes_rtol` 1e-10 reference + 1–2 candidates, ring and Womersley finest levels) | mono | [A] ~4 runs per case; B1 tight ≈ 1.4× S0 (`b1_windows.csv`: ring S0tight 0.56 vs S0 0.39 s/step) | 0.5–3 |
| **Timing**: ring weak/moderate/strong, factor 2, 100 steps/period | mono, IQN-ILS, Robin × 3 | ring README "IQN-ILS against Robin-Neumann" (125–575 s) + mono table (86–91 s): 1 931 s per set; ×1–2.2 | 1.6–3.5 |
| **Timing**: Womersley tutorial | mono, IQN-ILS, Robin × 3 | Womersley `README.md` l. 133–134: ~1, 4, 2 min serial | 0.35–0.8 |
| **Total** | | | **7–22** |

Dropped per 20 Oct: continuity arm (`98211d90e`), force lag (`dcbe04505`),
mesh-motion stiffening; cited only. Jacobian and PC ablations are costed in R5.

## R2. cavityFlexibleBottom consistency

Code has changed since the 20 Oct reruns (`ddt(U)` Euler→backward,
`viscousStressTranspose`), so full reruns are counted, not timing only.

| Run | Couplings × repeats | Cost basis | Core-h |
|---|---|---|---:|
| Mono L1–L4, Δt = 0.5, to 300 s (600 steps each) | mono × 1 | L1: `CAMP/b0/status.txt` `b0-cav-s1` 138 s / 400 steps; L2: [A] 1–2 s/step; L3: `b1_windows.csv` `b1-cav-S0-p1` 7.04 s/step; L4: f356c3242 README l. 235–236 "serial took about 55 to 80 s per step" | 10.5–15 |
| Partitioned Aitken strict L1–L4 | Aitken × 1 | `four_level_partitioned_monolithic.csv` at f356c3242, `partitioned_strict` clock_s 20/127/936/4 074 s (L4 on 4 ranks); ×1–2 | 4.8–10 |
| Discriminating: mono L2, L3 with `interpolate(U) linear` | mono × 1 | as L2/L3 above | 1.4–1.5 |
| Tolerance calibration (tight reference on L3) | mono | B1: S0tight 9.92 vs S0 7.04 s/step | 2–4 |
| **Timing**: L1–L4 | mono, Aitken × 3 | low: 50-step windows from a restart (per-step costs above; partitioned 0.05/0.16/0.58/1.27×4 core-s/step); high: windows from t = 0 as in B1 (~250 of 600 steps) | 3–20 |
| **Total** | | | **22–51** |

Womersley traction variant: superseded by the `viscousStressTranspose`
comparison (R1). `checkMesh` is negligible.

## R3. Robustness maps (correctness; array job)

| Run | Couplings | Cost basis | Core-h |
|---|---|---|---:|
| ring: [A] 8 density ratios (3 existing + ~5 lower) × 12/25/50/100/200 steps/period, 4 periods, factor 2 = 40 cells | Aitken, IQN-ILS, Robin (≤100 it), mono = 160 runs | mono: `b1-ring-S0-p1` 0.39 s/step (MeluXina) × 1 548 steps per ratio × 1.4 tol ≈ 840 s; partitioned [A] 1–6× mono (ring README: IQN-ILS 120 s, Robin 575 s vs mono 91 s, strong, 100 steps) | 6–26 |
| collapsibleChannel fluid L2: ρs/ρf 10/1/0.1/0.01/0 × Δt 0.025/0.0125/0.00625/0.003125 = 20 cells | 4 schemes = 80 runs | mono: README table, L2 1 072/2 008/2 896 s for Δt 0.0125/0.00625/0.003125 (macOS), Δt 0.025 fails at 0.25 s [A] ~300 s; ×1–2.2. Partitioned: Robin L2 Δt 0.00625 = 2 022 s ("Fluid mesh" table), scaled by the Robin time-step table (526–2 796 s); completes only at ρs/ρf ≥ 1 (Robin) / high ratios (IQN-ILS); failures [A] 10–30% of a full run. High = to t = 1.5 s, low = to first trough (t ≈ 0.46 s, `b2/runs.csv` notes) | 6–34 |
| *optional* cavity L3: Δt 0.0625–1.0 (5), to 200–300 s | 4 schemes = 20 runs | mono 7.04 s/step × 6 200 steps (to 200 s) ≈ 12 core-h, ×1.5 to 300 s; partitioned 0.58 s/step (`partitioned_strict` L3: 936 s / 1 600 steps) ≲ 3 core-h. Not "cheap": the small Δt dominates | 5–21 |
| **Total** | | | **12–60 (+5–21)** |

Assumed monolithic/partitioned cost ratio for collapsibleChannel L2: **1.0**
on comparable machines (mono 2 008 s macOS vs Robin 2 022 s Linux, same Δt and
end time) up to **2.2** (B2 XenoSim 4 420 s, loaded node).

## R4. Hron–Turek FSI3 work–precision (conformal 1x/2x/4x, t = 7 s)

| Run | Couplings × repeats | Cost basis | Core-h |
|---|---|---|---:|
| Accuracy runs 1x/2x/4x | mono × 1 | TurekHron2006 README l. 575–576: conformal 4x "ran on 12 ranks in 3.6 h" = 43 core-h (M1, pre-#597, old mesh motion). 2x and 1x scaled by the FSI1 mono clock ratios 6 146/668/146 s (README FSI1 table): ≈ 4.7 and 1.0; ×1–2 | 49–100 |
| Accuracy runs 1x/2x/4x | IQN-ILS strict × 1 | **No record on conformal meshes or at 4x.** Tutorial meshes: 1x serial 1.1 h, 2x 8 ranks 4.1 h = 33 core-h (README l. 220–221). [A] 4x = 8× the 2x work: 70 (ideal serial-equivalent 8.8 core-h at 2x) to 264 (observed 8-rank efficiency); strict test +0–50% | 80–450 |
| Tolerance sweep on 2x: `snes_rtol` 1e-4/1e-6/1e-8; strict 1e-4/1e-5/1e-6 | 6 runs × 1 | 2x costs above; low = 2 s from a periodic restart, high = full runs | 10–170 |
| Tight reference for the 5% rule (2x, 1e-10) | mono × 1 | 2x mono × 1.4–2 | 9–20 |
| **Timing**: 2 periods (~0.37 s of 7 s ≈ 5%) per level | mono, IQN-ILS × 3, same ranks | 3 × 5% of the accuracy-run costs. **Requires working restarts**; otherwise ≈ 3 full runs per level and coupling (+400–1 600 core-h) | 21–90 |
| **Total** | | | **170–830** |

Optional: FSI1 rerun (A1 marks it stale but R4 does not list it): mono
1x/2x/4x serial 146 + 668 + 6 146 s and IQN-ILS 781 + 2 × 3 062 s (README FSI1
tables) ≈ **3–6 core-h**, not in the total.

## R5. 3dTube consistency, scaling, PC ablation (end time 20 ms)

| Run | Couplings × repeats | Cost basis | Core-h |
|---|---|---|---:|
| Consistency L1/L2/L3 to 20 ms (800/1 600/3 200 steps) | mono × 1 | L2: `b1-tube-S1-p4` 5.58 s/step × 4 = 22 core-s/step, `-p16` 2.16 × 16 = 35 → 10–15 core-h; L1 ≈ L2/8 per step → 0.6–1; L3: README l. 155 "about sixteen times as expensive as level 2" → 160–250, [A] up to 300 for ≥64-rank efficiency | 170–315 |
| Tight reference for the 5% rule (L2, S0tight-like tolerances) | mono × 1 | `b1-tube-S0tight-p4` 29.98 vs S0 23.88 s/step (×1.25) | 12–20 |
| **Timing**: L2 strong scaling 1–64 ranks (7 points), 50 steps | mono, Robin × 3 | measured 4/16 ranks above; [A] 20–28 core-s/step at 1–8 ranks, 45 at 32, 70 at 64. Robin L2: README mesh table 7 197 s × 4 ranks / 1 600 steps = 18 core-s/step (M1), [A] same scaling. Low: restart windows; high: windows from t = 0 (B1 used 210 steps) | 18–85 |
| **Timing**: L3 scaling 16/32/64/128 ranks, 50 steps (if allocation allows) | mono, Robin × 3 | [A] L3 per step = 8× L2 work; ~1 400 core-s/step summed over the 4 rank counts. High: from t = 0 (spin-up 2 ms = 320 steps) | 115–800 |
| **Timing**: PC ablation, L2, 8 ranks, 50 steps: baseline + 6 variants (Schur full, lag 1, `ksp_rtol` 1e-4, alt. solid PC, BoomerAMG velocity, assembled Jacobian) | mono × 3 | baseline [A] ~26 core-s/step; variants [A] 1–3× baseline (B1: bjacobi+LU solid 4.3× BoomerAMG at 4 ranks); high: from t = 0 | 8–95 |
| **Total** | | | **320–1 315** |

Not counted: partitioned L3 runs if V does not already have them (V's README
has L1/L2 only; Robin L3 by the ×16 rule ≈ 130+ core-h, IQN-ILS ≈ 4× Robin per
the README coupling table, 3 075 vs 758 s).

## R6. blobInTreacle (Liu) and block with tail

| Run | Couplings × repeats | Cost basis | Core-h |
|---|---|---|---:|
| Mesh study x1/x2/x4 to 3 s, Liu Δt study 0.25–0.03125 s, timing ×3 both couplings | mono, IQN-ILS | `CAMP/b3/estimate.md` §1 Cost: "about 2–12 core-h" (partitioned x1/x2/x4: 91 s, 376 s ×4, 1 430 s ×4, README l. 167–172; assumes mono ≈ partitioned) | 2–12 |
| `viscousStressTranspose yes` mesh study x1/x2/x4 | mono × 1 | one more mesh-study pass, 2 core-h × [A] mono/part 1–3 | 2–6 |
| Tolerance calibration (tight reference, x2) | mono | [A] | 0.5–2 |
| **Total** | | | **5–20** (timing share ≤ 10) |
| Block with flexible tail (only if approved) | both | `CAMP/b3/estimate.md` §2: "about 20–60 core-h ... a guess, not a measurement"; set-up 3–3.5 person-days | 20–60 |

## R7. foilInWind time-step limit (to t = 0.2 s, one run per Δt)

| Run | Coupling | Cost basis | Core-h |
|---|---|---|---:|
| Δt = 0.0025 s | mono | b157ecaf3 `foilInWind/README.md`: "about 55 min ... on 2 processes (80 time steps ...), or about 94 min in serial" (M1) → 1.6–1.8 | 1.6–4 |
| Δt = 0.005 s | mono | **No record.** [A] 0.5–1× the 0.0025 s run | 0.8–4 |
| Δt = 0.01 s | mono | stalls at t = 0.05 s (b157ecaf3 message): ≤ 5 steps + stalled step [A] | ≤ 0.5–1 |
| Δt = 0.01 s (cost comparison) | IQN-ILS | same README: "about 13 min ... on 2 processes" = 0.43 | 0.4–1 |
| **Total** (×1–2.2 machine in high bound) | | | **3–10** |

## Largest uncertainties

1. **Restarts.** Monolithic restart is broken (`b1/issue_mesh_motion_restart.md`).
   If unfixed, R4 timing grows by ≈ 400–1 600 core-h and R5 windows ×4–7
   (already in the R5 high bounds, not in R4's).
2. **Exclusive-node billing** of timing runs: 16–80 node-h ≈ 2 000–10 000
   allocated core-h on 128-core nodes (see Summary), versus 170–1 100 core-h
   actually used.
3. **FSI3 partitioned IQN-ILS at conformal 4x**: never run; 80–450 core-h
   spread is the largest single item in R4.
4. **3dTube L3**: never run; "×16 of L2" from the README; parallel efficiency
   at 64–128 ranks unknown.
5. **Rerun multiplier**: the 21 Oct decision says cases affected by later fixes
   are rerun once the version is fixed. If the long cases (FSI3, 3dTube L3,
   cavity L4) are hit, add up to ≈ 1× their correctness cost (≈ 250–700 core-h).
6. **Machine and code drift**: recorded times are from M1 Ultra (shared) and a
   loaded XenoSim; `ddt(U)` backward, `viscousStressTranspose` and the new
   mesh-motion solid model change Newton/Krylov counts. Factor 1–2.2 applied
   only where noted.
7. **Tolerances**: +40% assumed for ring/Womersley only (decisions log);
   tutorial tolerances elsewhere. If the 5% rule forces tighter `snes_rtol` on
   FSI3 or 3dTube, add ~25–40% to their monolithic runs (B1 tight/S0 ratios
   1.25–1.4).

## Items with no cost basis (assumptions only)

- ring non-conformal study (no recorded times) and the R3 extension to lower
  density ratios (how many ratios "run" is unknown).
- cavityFlexibleBottom monolithic L2 per-step cost (interpolated).
- FSI3 IQN-ILS on the conformal meshes and at 4x; partitioned strict-test
  iteration increase.
- 3dTube L3 (both couplings), scaling beyond 16 ranks, Robin-Neumann beyond
  4 ranks, and the cost of each PC-ablation variant (assembled Jacobian, ILU
  velocity block, lag 1).
- foilInWind at Δt = 0.005 s.
- blobInTreacle monolithic/partitioned cost ratio (B3 assumed 1; no recorded
  monolithic clock time).
- Block with flexible tail (B3: an order-of-magnitude guess).
