# Reuse map: planned solver-paper runs against existing results

Status: 22 October 2026 (late evening). Read-only survey; nothing was run or
fetched. For every run ID of `paper-data/submission_plan.md` §4 (WP0–WP8) and
the partitioned counterparts each M figure or table needs, this note lists
what already exists, whether M can use it, what is running now, and the
minimum left to run.

Sources (all read with `git show`/`git log` from local clones):

- **M campaign**: `paper-monolithic-fsi` `origin/evidence/campaign-g1`
  (`campaign/PROGRESS.md`, `campaign/G1_report.md`,
  `campaign/G1_cost_estimate.md`, `paper-data/campaign/b0..b3`, head
  `1e386a4`, 22 Oct 23:16) and `origin/evidence/campaign-r0`
  (`paper-data/campaign/r0/runs.csv`, `qois.csv`, head `e6136bc`, 22 Oct
  23:09); `origin/main:paper-data/a1_monolithic_study_inventory.md` (A1),
  `a4_ablation_reproducibility.md` (A4).
- **V**: `paper-fsi-verification` `origin/main` (`paper-data/*`),
  `origin/ring-monolithic` (draft PR #13, head `9123bff`, 20 Oct),
  PR descriptions of #6, #12, #13, #16, #17.
- **solids4foam**: `origin/feature-petsc-snes-quasi-monolithic` at
  `85b0c1de6` (abbreviated *head*), `tutorials/fluidSolidInteraction/<case>/verification/README.md`
  at head (abbreviated *README*), branches `verification/*`, open PRs into the
  solver branch (#602 foilInWind Δt/4, #616 restart fix).

## 0. Code-equivalence classes (what "current" means)

Result-changing commits on the solver branch, oldest first: `c008e8dd1`
(BDF2 solid), `3e93daef6` (interface pressure gradient), `dbfda65ba` (wall-flux
traction), `0ed9c2a77` (#594, neutral for the tutorials), `5a03c7ad8`/`597cc6317`
(#597 continuity from the face flux), `987bd325a` (#611 transpose viscous term
**on**), `021affbc4` (transpose **off** by default). Between `257b2e564` and
head the only other changes are the #581 helper split, #599-era cost changes
and comments. B1 repeated on head gives the same iteration counts and QoI
histories in every written digit as on `257b2e564`
(`campaign-g1:campaign/PROGRESS.md`, log 22 Oct). Hence:

- **Class E597** = any build containing #597 with `viscousStressTranspose no`
  (the default from `021affbc4`): `257b2e564` … `85b0c1de6`. Results in this
  class are current; only the case set-up (ddt, tolerances, machine) can make
  them unusable. No QM result was found that was produced in the window
  `987bd325a`–`021affbc4` (transpose on), except the CI regression quoted in
  the `021affbc4` message (blob "2% further", no number recorded).
- **Pre-#597** QM results are stale (V note #16), except ringAddedMass
  (inviscid fluid, orthogonal-enough mesh; R0 at head reproduces the
  README's ring Newton counts).
- **#616** (restart fix, open PR, `abfcd3e32`) changes no continuous run
  (PR description: identical norms, counts and monitors on cavity, 3dTube,
  ring); it is needed only for restart-based timing windows.
- **Partitioned**: #597/#611 touch only `newtonIcoFluid`, so partitioned
  results are not staled by them. Relevant partitioned changes are #546
  (GCC `-O3` wall-viscous-force aliasing and AMI barycentric weights; 2-D
  cases are unaffected per `V:paper-data/hronturek_pr546_exposure.json`),
  #552 strict coupling test, and #598 (`couplingReuse 5` tutorial default,
  **merged into `development` but not into head**: head's partitioned
  tutorials still use reuse 0).

Abbreviations: QM = quasi-monolithic; part. = partitioned; RN =
Robin–Neumann; IQN = IQN-ILS; vST = `viscousStressTranspose`; Mx = MeluXina;
Xe = XenoSim (shared, load ~185/192, timings indicative only); M1 = Apple M1
Ultra shared (timings indicative only); MS = Mac Studio. Verdict: **YES** =
usable as is; **PART** = usable with the stated gap; **NO**; **MISS** =
nothing exists; **RUN** = in progress now.

## 1. WP0 — prerequisites

| ID | Existing result(s) and provenance | Reusable? | In progress (≤ 48 h) | Remains (minimal) |
|---|---|---|---|---|
| 0a | Head builds `v2.2-1713-g85b0c1de6`: Xe job 13104 (`~/OpenFOAM/philipc-v2512-qmhead`, no build errors), Mx 5375410 (`qm-head`, p201136); R0 ran on the Mx head build | **YES** | – | Rebuild only when #616 (restart) and #602 (foilInWind controlDict) merge; neither changes continuous results |
| 0b blob vST | QM vST-no x1/x2/x4: README "Quasi-monolithic coupling", row "Monolithic" (0.116851, 0.119346, 0.120020; E597, `835f81a4e`; **Euler** ddt(U), mixed macOS/Linux, serial, no timing). R0 x1 head **backward**: 0.11685406 at t = 10 s (`r0/qois.csv`), 2.6e-5 from the Euler value. vST-yes: only the CI regression in the `021affbc4` message (~2%, no value). Part. x1/x2/x4 IQN: README mesh study (0.117301/0.119698/0.120152, Linux v2512, backward, reuse 0, tol 1e-6) and macOS rerun (0.120224 at x4) | **PART**: vST-no x1 at head/backward exists; x2/x4 Euler (steady, so Δ ≈ 1e-5 relative expected); vST-yes missing; part. values reusable | – | QM vST-yes x1/x2/x4 (3 runs, backward); optionally QM vST-no x2/x4 backward on the same machine (2 runs). No partitioned run needed |
| 0c Womersley vST | QM m2 n50 vST-no: README "Quasi-monolithic coupling" and `V:ring-monolithic:paper-data/womersleyTube_monolithic.csv` (76.7 s), **pre-#597** (`54a5c6916`). R0 m2 **n100** at head: profile 4.685e-3 vs README 4.70e-3 (2 periods only). RN m2 n50: README "Results" (a507bfd41, Linux, fluxConsistentPatches, **pre-#546**). IQN m2 n50: none (IQN only at m2 n100) | **PART**: RN m2 n50 YES (wedge #546 exposure not assessed); QM pre-#597; IQN missing | – | QM m2 n50 vST yes/no at head (2 runs, ~80 s each); IQN m2 n50 (1 run, reuse 0 pinned) |
| 0d B1 solid PC | Done: `campaign-g1:paper-data/campaign/b1/` (S0 ring/cav, S1 BoomerAMG 3dTube), repeated on head (`b1/head/`, identical) | **YES** | – | – |
| 0e B2 collapsible AMI | Fluid L2, AMI 640×8: trough −1.91% (Xe 13025, `257b2e564`, **Euler**, 4 694 s indicative); conformal 160×8 −4.28% (13024) (`b2/findings.md`, `b2/runs.csv`) | **PART** (Euler; plan wants backward) | **RUN**: Xe head build, AMI 640×8 at fluid L2 (13109) and L4 (13110), conformal 320×8 L4 (13111), all Euler (PROGRESS "Current phase") | Decide the §6 configuration from 13109–13111; the 3b map then runs with backward |

## 2. WP1 — §4 exact solutions

| ID | Existing result(s) and provenance | Reusable? | In progress | Remains (minimal) |
|---|---|---|---|---|
| 1a ring QM | README "Quasi-monolithic Newton against IQN-ILS": 3 levels × mesh 2 × 25/50/100 steps, standard solid (`dcbe04505`/`c008e8dd1`/`3e93daef6`, pre-`dbfda65ba`, pre-#597; v2512 macOS, 10 concurrent serial runs, Newton yes, Krylov no, timing indicative). Mesh 1/2/4 at 100 steps for moderate and strong only. Same data with run CSVs in `V:ring-monolithic:paper-data/ringAddedMass_monolithic_{runs,mesh}.csv`. R0 head (factor 1, moderate, 100 steps, backward): 2.00 Newton, ω +20.6% (standard solid, as README) | **PART**: values almost certainly still valid (ring unaffected by #597 per V note #16; viscous traction negligible at ν = 1e-7) but pre-E597; weak-level mesh study and 200 steps missing | – | Rerun the whole 1a grid at head (≈ 36 runs, < 1 core-h; `--study monolithic` + mesh sweep). Cheaper to rerun than to argue equivalence |
| 1b ring zeroGradient | README "Defects found by this study" (−0.194/−0.117/−0.063% moderate, −0.355/−0.213/−0.115% strong; state of `c008e8dd1`, mixes the pressure BC with the old face-velocity change, A4 §1) | **PART**: citable "before" numbers (route C); not the same code | – | A-route: 6 runs (moderate, strong × mesh 1/2/4, 100 steps) at head with `p` interface `zeroGradient` |
| 1c ring non-conformal | None recorded (A1 §1.1; A4 §7: no numbers) | **MISS** | – | `--study nonconformal` × conservative/interpolated (G1 estimate 3–9 core-h) |
| 1d ring timing (strong, mesh 2, 25/50/100) | QM and IQN (standard solid): same README table (macOS, concurrent, indicative). IQN/RN (high-order solid, 100 steps): README "IQN-ILS against Robin-Neumann" (v2412, xenosim, 32 concurrent). RN with standard solid: none | **PART**: iteration counts usable for IQN; timings unusable (shared machines); RN at standard solid and 25/50 steps missing | – | 9 timing runs (3 couplings × 3 Δt) × 3 repeats on Mx, exclusive |
| 1e Womersley QM m1/m2/m4 n200, m2 n50/100/200/400 | README "Quasi-monolithic coupling" + `verification_summary_monolithic.md` (7 runs, **pre-#597**, serial, platform not stated, timings yes). R0 head m2 n100 matches the README to 1–3 digits | **PART**: pre-#597 → rerun (7 runs, 1.3–18 min each) | – | QM 7 runs at head, backward (tutorial), vST no |
| 1e part. counterparts | RN all 7 cells (m1/m2/m4 n200; m2 n50/100/200/400): README "Results" (Linux v2512, `a507bfd41` fluxConsistentPatches, pre-#546, iterations yes). IQN m2 n100 only (14.6 it/step, 524 s; reuse 0) | **PART**: RN reusable (same meshes/Δt; check #546 on the wedge with one A/B run); IQN only m2 n100 | – | IQN at the other 6 cells if Fig. 5.2 needs IQN at every cell (6 runs, reuse 0 pinned); one RN A/B run with a post-#546 build |
| 1f BDF2 start-up | None | **MISS** | – | 2–4 runs (ring, Womersley) |

## 3. WP2 — §5 consistency (cavityFlexibleBottom)

| ID | Existing result(s) and provenance | Reusable? | In progress | Remains (minimal) |
|---|---|---|---|---|
| 2a QM L1–L4 | `verification/cavityflexiblebottom-partitioned-fine` (merged as #609; on head): README "Rerun with the newtonIcoFluid continuity fix", `results/four_level_partitioned_monolithic.csv` rows `monolithic_597`: uy −0.201546/−0.228468/−0.235448/−0.237187, Fy …; `257b2e564` (E597), Xe GCC `-O3`, **Euler** ddt(U), Δt 0.5, end 300 s, L1–L3 serial, L4 4 ranks (mesh motion `redundant` LU). **No Newton/Krylov counts, no clock.** Extra: B0 L1 (Mx, exclusive, Euler, 2.025 Newton, 35.2 Krylov/Newton, repeats ≤ 0.8% solver time); B1 L3 windows (Xe, backward, 1/4/16 ranks, 2.00 Newton/step in window, 2.18 from t = 0); R0 L1 head backward (Mx farm, 2.0075 Newton, 156 s, uy −0.201575 at 200 s) | **PART**: steady values YES (steady state does not depend on ddt; R0 backward L1 within 1.1e-4 of Euler at 200 s); Newton counts L2/L4 and every time-to-steady value missing; timing must be Mx | – | QM L1–L4 backward at head on Mx with the campaign parsers (gives counts and time to steady; L4 ≈ 55–80 s/step serial, so 4 ranks) — 4 runs + 3 timing repeats |
| 2a part. L1–L4 (Aitken, strict) | Same CSV, rows `partitioned_strict`: `requireAllResidualMeasures yes`, Aitken, tol 1e-5, nOuterCorr 20 (L4: 40, fluid solver tol 1e-8, 4 ranks); **Δt 0.5/0.25/0.125/0.0625** per level (L4 diverges at larger Δt); MS (macOS, Clang), solids4foam `0698d55cd` (has #546); iterations and clock_s 20/127/936/4 074 s | **YES** for steady values and coupling counts; **PART** for the time column (MS, different Δt from QM's 0.5) | – | Timing repeats only, on Mx, at the same Δt as recorded (4 runs × 3) |
| 2b QM L2, L3 `interpolate(U) linear` | None | **MISS** | – | 2 runs |
| 2c `checkMesh` | None recorded | **PART** if the f356c3242 run directories (Xe) and the MS partitioned directories still exist | – | `checkMesh` on existing final states (no new runs); otherwise on the 2a reruns |

## 4. WP3 — §6 robustness maps

| ID | Existing result(s) and provenance | Reusable? | In progress | Remains (minimal) |
|---|---|---|---|---|
| 3a ring map {Aitken, IQN, RN, QM} × 5 Δt × 4 levels | Only single points: QM/IQN at mesh 2 × 25/50/100 × 3 levels (1a source, standard solid); IQN/RN at 100 steps × 3 levels (high-order solid). No Aitken, no "extended" level, no 12 or 200 steps | **MISS** (existing points are a different solid for RN and pre-E597 for QM) | – | Full 80-run array |
| 3b collapsible map {4 schemes} × 4 Δt × ρs/ρf {10, 1, 0.1, 0.01, 0} | V/README "Density sweep": IQN and RN, **cubic** solid 160×8, **fluid L1**, Δt 0.0125/0.00625/0.003125 (RN also 0.025), ρs/ρf {0, 1e-3, 1e-2, 0.1, 0.3, 1, 3}, failure = 200 iterations or solid Newton failure, v2412, Linux. QM: README "Quasi-monolithic coupling" (linear solid conformal, fluid L1/L2/L4, ρ 1 and 0, macOS, **pre-#597**, Euler) | **NO** for the map (different solid, fluid level, densities, failure criterion); usable only as qualitative context | 0e runs decide the solid/fluid configuration | Full 80-run array on M's configuration, backward. If Philip prefers alignment with V, set fluid L1 and V's density list instead, and then V's IQN/RN cells (cubic solid) still cannot be reused for the linear-solid QM comparison |
| 3c cavity L3 Δt map (optional) | None | **MISS** | – | 10 runs if kept |

## 5. WP4 — §7 FSI3 (Hron–Turek)

| ID | Existing result(s) and provenance | Reusable? | In progress | Remains (minimal) |
|---|---|---|---|---|
| 4a QM conformal 1x/2x/4x | README "Quasi-monolithic coupling" (FSI3 table) and `V:ring-monolithic:paper-data/hronturek_fsi3_monolithic_conformal.csv`: E597 (`541192be5`, parent `257b2e564`), backward, SNES 1e-6, 12 ranks, M1 shared; 4x in 3.7 h; Δt 0.001/0.0005/0.00025, t = 7 s, last 1 s. R0 conformal 1x at head (Mx) reproduces it (u_x mean −0.0013375 vs −0.0013375) | **YES** for accuracy (timing NO: M1) | – | – |
| 4a IQN conformal 1x/2x/4x | **None** on the conformal meshes (G1 cost estimate: "never run", 80–450 core-h) | **MISS** | – | 3 runs (4x ≈ 40 h on 32 ranks by analogy with V's tutorial 4x) — or switch the comparison (see §9) |
| 4a alt.: IQN on tutorial meshes | `V:main:paper-data/hronturek_fsi3_4x_findings.md` §2: IQN 1x/2x/4x, tol 1e-5, reuse 0, predictor yes, backward, nOuterCorr 30, xenosim v2512 GCC -O3, `d49552f4c` (from `aee0c8e35`, **pre-#546, legacy test**; #546 not exposed for FSI3 per `hronturek_pr546_exposure.json`); 1.4 h/5.5 h/40.8 h on 1/8/32 ranks. QM AMI on the same meshes: 1x/2x E597, 8 ranks, M1 (`V:ring-monolithic:…fsi3_monolithic_tutorial_meshes.csv`); 4x AMI missing | **PART**: only valid against QM **AMI** on tutorial meshes, not against QM conformal; legacy convergence test | – | QM AMI 4x (1 run) if this pairing is chosen |
| 4a alt.: V production (ring+box) | §20 of the same findings: IQN strict (#552), tol 1e-5, reuse 0, fluid 1x'/2x'/4x', solid 2x/4x/8x, Δt 5e-4 all levels, branch `verification/hronturek-production` (PR #554 mesh motion, not on head); ≈ 5 340 core-h | **NO** for M (different meshes, Δt and mesh-motion code) | – | – |
| 4b timing windows | None usable (M1 and Xe timings only). Requires #616 for restart windows | **MISS** | #616 open (fix verified on the B1 cavity mesh, job 13152) | 2 periods × 3 levels × 2 couplings × 3 repeats on Mx, after #616 merges |
| 4c 2x tolerance sweep | None at E597. (V: IQN tol 1e-4 vs 1e-5 at 1x' on ring+box only) | **MISS** | – | 6 runs |
| 4d QM u_x mean order 2x→4x | Derivable from 4a's existing conformal 2x/4x (and 1x) values; no new run | **YES** (computation only) | – | – |
| 4e field image (coarse) | R0 `r0-fsi3-backward-a` (conformal 1x, head, full 7 s, Mx run dir); driver writes fields only at the end time (README) | **PART**: one time instant; image at maximum tip deflection needs a short rerun with write output | – | 1 short run (last period, writing ~10 instants) |

## 6. WP5 — §7 blobInTreacle

| ID | Existing result(s) and provenance | Reusable? | In progress | Remains (minimal) |
|---|---|---|---|---|
| 5a QM x1/x2/x4 | See 0b: E597 Euler, serial macOS/Linux, no timing or Newton counts; R0 x1 head backward (1.42 Newton/step, Mx farm) | **PART** | – | QM x2, x4 backward + timing (merge with 0b; 2–3 runs + repeats) |
| 5a part. x1/x2/x4 | README mesh study (IQN, backward, Linux v2512, reuse 0, tol 1e-6; clock 91/376/1 430 s on 1/4/4 cores; 9.0–11.7 it/step). Note #598: `development` now defaults to reuse 5 | **YES** for values/iterations; **PART** for timing (not Mx, not exclusive) | – | Timing repeats on Mx only, reuse pinned to 0 |
| 5b QM temporal (Δt 0.25 … 0.03125, t = 1 s) | None (A1 §1.6: driver is partitioned only) | **MISS** | – | 4 runs (< 0.1 core-h, B3) |
| 5b part. temporal | README "Time-step study" (IQN, backward, tutorial mesh, orders 2.39/2.54) | **YES** | – | – |

## 7. WP6 — §8 3dTube

| ID | Existing result(s) and provenance | Reusable? | In progress | Remains (minimal) |
|---|---|---|---|---|
| 6a QM L1–L3 | README "Quasi-monolithic coupling" (#604, `44fe15e28` on `47209122d` + #599 settings; E597), `--coupling monolithic`, backward, BoomerAMG solid, 8 ranks on Xe (shared): L1 221 s, L2 3 398 s, 2.00 Newton; V copy `ring-monolithic:paper-data/3dtube_monolithic_mesh_study.csv`. R0 L1 head backward on Mx reproduces README to ≤ 4e-5. L3: none | **PART**: L1/L2 YES (accuracy); L3 missing; no Mx timing | – | QM L3 full 20 ms (G1: 160–300 core-h) |
| 6a part. counterpart | RN L1–L3 corrected (both #546 defects fixed): `V:main:paper-data/3dtube_level3_findings.md` §12.6 (L1/L2 Xe, L3 Mx 128 ranks, v2412) and RN same-node L1/L2 rows in the README QM table (8 ranks, identical values). IQN: L1 only (README coupling study, v2412 M1, tutorial `couplingReuse 2` → V PR #17 flags it) | **YES** for RN L1–L3 values; IQN L2/L3 missing (not needed unless the table compares IQN) | – | – |
| 6b strong scaling (QM and RN, L2 1–64, L3 16–128, 50-step windows) | B1 tube L2 windows on Xe (S0/S1/S2 at 4 and 16 ranks, non-exclusive, indicative); V FSI3 4x IQN strong-scaling note (not 3dTube) | **MISS** for the figure (B1 only indicative) | – | All scaling windows on Mx, exclusive; restart windows need #616 |
| 6c PC/Jacobian ablation (7 variants, L2, 8 ranks) | B1: 3 solid-block variants (S0 LU, S1 BoomerAMG, S2 bjacobi+LU) at 4/16 ranks, Xe; README: `redundant` LU 26 218 s vs AMG 3 398 s at L2 (Xe) | **PART**: variants 1–3 known qualitatively; timing must be redone on Mx | – | 7 variants × 3 repeats on Mx |
| 6d Newton histories (MF vs assembled) | None | **MISS** | – | 2 short runs (tube L2, ring) |
| 6e field image | R0 `r0-tube-backward-a` (L1, head, Mx run dir) — write interval not checked | **PART** | – | Short rerun with output at three instants if R0 did not write them |

## 8. WP7 and WP8

| ID | Existing result(s) and provenance | Reusable? | In progress | Remains (minimal) |
|---|---|---|---|---|
| 7a QM Δt 0.01/0.005/0.0025 to 0.2 s, IQN Δt 0.01 | PR #602 (`b157ecaf3`, E597 minus #599): Δt 0.01 stalls at t = 0.05 s; Δt 0.0025 to 0.2 s: 2–4 Newton/step, 94 min serial, 55 min on 2 ranks (M1). IQN Δt 0.01: 13 min on 2 ranks (README at `a1aa222c8`, **pre-BDF2**). Δt 0.005: none | **PART** | **RUN**: R0 `foilInWind` QM Δt 0.0025, endTime 12 s, at head on Mx (R0 commit message "foilInWind running") — covers 0–0.2 s if its log is kept | QM Δt 0.005 (1 run); QM Δt 0.01 at head with Newton histories (1 short run); IQN Δt 0.01 at head (1 run); reuse R0 for Δt 0.0025 |
| 8a mesh layers | R0 run directories on Mx hold `constant/*/polyMesh` for ring, Womersley, cavity L1, collapsible L1 (80×8), FSI3 conformal 1x, blob x1, 3dTube L1, foilInWind, all at head | **PART** (approved to start; reuse avoids `blockMesh` runs, except collapsible if the figure should show the §6 AMI 640×8 solid) | – | Copy ASCII polyMesh from the R0 run dirs (convert if binary) |
| 8c/8d | Depend on the runs above | – | – | – |

## 9. Partitioned counterparts: mesh and setting mismatches

- **cavityFlexibleBottom**: same four conformal meshes. The strict partitioned
  set uses Δt 0.5/0.25/0.125/0.0625 (L4 diverges at 0.5), QM uses 0.5 on every
  level; steady values are comparable, time-to-steady and cost per steady
  solution are not unless stated per Δt. Partitioned ran on MS (Clang),
  QM on Xe (GCC -O3). The legacy-test rows (`partitioned_legacy_test`) must not
  be used.
- **FSI3**: the QM conformal meshes have a quarter of the tutorial's solid
  cells at each factor (conformal 2x/4x ≙ tutorial 1x/2x plate). V's IQN
  results are on the tutorial meshes (1x/2x/4x, legacy test) or on the
  ring+box family with finer solids (strict test, PR #554 code). **No IQN run
  exists on the conformal meshes.** Two consistent options: (a) run IQN
  conformal 1x/2x/4x as planned (the 4x is the single largest new cost); (b)
  compare QM-AMI with V's IQN on the tutorial meshes (needs QM-AMI 4x only;
  QM-AMI 2x fails the 5% u_y check, README). Philip to choose.
- **3dTube**: identical meshes and Δt per level; QM uses `directMap`, RN the
  default AMI transfer on the matching interface (fixed by #546). RN L3 was
  run once on Mx (v2412), QM L3 not yet. IQN exists at L1 only and may carry
  `couplingReuse 2` (V PR #17).
- **womersleyTube**: same meshes and steps; partitioned `pimpleFluid` uses
  `fluxConsistentPatches`; IQN reuse 0; RN results predate #546 (wedge: check
  with one A/B run).
- **ringAddedMass**: QM must use the standard solid; the README's IQN/RN
  coupling table uses the high-order solid. Only the "QM vs IQN" table uses
  the standard solid for both. RN with the standard solid does not exist.
- **collapsibleChannel**: V's density sweep (cubic solid, fluid L1, its own
  density list, 200-iteration stall criterion) cannot be the partitioned half
  of M's map (linear velocity solid, AMI 640×8, fluid L2).
- **blobInTreacle**: same meshes and Δt; partitioned backward, QM recorded
  with Euler (rerun with backward); the x4 partitioned value differs by 0.06%
  between Linux and macOS, so compare on one machine.
- **foilInWind**: IQN only at Δt 0.01 and pre-BDF2.

## 10. Counts and savings

Rows above, counting each M run ID once and its partitioned counterpart as a
separate row where M needs one (37 rows; 0e and 7a are counted as RUN): **YES 8** (0a, 0d, 2a part.,
4a QM, 4d, 5a part., 5b part., 6a part. RN), **PART 15** (0b, 0c, 1a, 1b, 1d,
1e QM, 1e part., 2a QM, 2c, 4e, 5a QM, 6a QM, 6c, 6e, 8a), **MISS 11** (1c,
1f, 2b, 3a, 3c, 4a IQN conformal, 4b, 4c, 5b QM, 6b, 6d), **NO 1** (3b
from V's sweep), **RUN 2** (0e, 7a Δt 0.0025 via R0). 4a's alternative rows
are counted under 4a.

Largest savings (no rerun needed):

1. **FSI3 QM conformal 1x/2x/4x** (E597, R0 confirms on head): saves the
   QM accuracy arm of R4, ≈ 49–100 core-h (G1 estimate), including the 4x
   (3.7 h × 12 ranks).
2. **3dTube RN L1–L3** (V, corrected) and **QM L1/L2** (E597): saves the RN
   L3 accuracy run (G1: ≈ 130+ core-h) and the QM L1/L2 accuracy runs
   (≈ 10–16 core-h); only QM L3 and Mx timings remain.
3. **cavityFlexibleBottom partitioned strict L1–L4** (incl. L4, 4 074 s on
   4 ranks) and the QM steady values: only counts/timing reruns remain.
4. **blobInTreacle partitioned mesh and temporal studies**, Womersley RN
   (all cells), ring IQN (standard solid) iteration counts.
5. **Mesh layers (8a)** from the R0 run directories instead of new
   `blockMesh` runs.

## 11. Duplicate-run risks

1. **V's pending QM reruns.** Draft PR #13 (V) says "reruns follow" for the
   pre-#597 QM cross-checks of womersleyTube, collapsibleChannel, Mok,
   cavityFlexibleBottom and blobInTreacle. These are the same runs as M's
   1e, 0c, 3b (part), 2a and 0b/5a. Whichever agent runs them first must
   record them where the other can find them.
2. **FSI3 IQN 4x.** M's planned IQN conformal 4x (~40 h on 32 ranks) and any
   V follow-up on FSI3 4x/8x (V findings §20 "Open: no coupled 8x' level") are
   the most expensive candidates for double launching; R0 has already
   repeated V's QM conformal 1x run (identical result).
3. **3dTube L3.** QM L3 (M 6a) is not run anywhere; V's draft PR #13 shows QM
   L1/L2 and may extend to L3. RN L3 exists (V) and must not be rerun for
   accuracy by M; only scaling windows are new.
4. **blobInTreacle temporal study.** V's strengthening item S6 (time study
   with tolerances two decades tighter, partitioned) overlaps M 5b's
   partitioned arm; M 5b needs only the QM arm.
5. **collapsibleChannel.** V items S2 (Δt study on fluid L3/L4) and M's 0e
   (B2 L4 runs 13110/13111) and 3b all touch the fine-fluid partitioned/QM
   runs.
6. **cavityFlexibleBottom partitioned L4.** V item S5 (reduced pseudo-Δt,
   coupling comparison) vs M 2a timing repeats.
7. **Silent set-up divergence that forces a rerun.** (a) `couplingReuse`:
   `development` defaults to 5 (#598), head to 0; IQN runs launched by V on
   `development` and by M on head are not the same run. (b) ddt(U): the
   `*.monolithic` tutorials still use Euler for blob, cavity, collapsible,
   3dTube (the 3dTube driver overrides to backward); B2 13109–13111 are Euler.
   (c) Restart windows before #616 merges fail on cavity-type mesh motion.
   (d) Timing on Xe or M1 is indicative only; any timing row must be redone
   on Mx.

## 12. Proposed shared rule and registry

**Rule.** No agent of either paper submits a run (QM or partitioned) on any
machine without first checking, then claiming, a row in one shared registry.
A claim without a job ID lapses after 24 h; a row marked `done` is reused,
not rerun, unless its code class or a set-up key changes.

**Registry.** One file, `paper-data/campaign/registry.csv` on a dedicated
branch of `paper-monolithic-fsi` (say `campaign/registry`, pushed only by
the coordinator), referenced from V's `paper-data/manuscript_todos.md`. Each row is one run, keyed by:

`case, coupling (QM | QM-AMI | Aitken | IQN | RN), mesh_family (tutorial | conformal | ring+box | …), level, solid_mesh, interface_transfer (directMap | AMI-cons | AMI-interp), dt, ddt_fluid, ddt_solid, solid_model, rho_ratio, couplingReuse, convergence_test (strict | legacy), coupling_tol | snes_rtol, ksp_rtol, solid_pc, vST, code_class (E597 | pre597 | dev+546 | …), purpose (accuracy | timing)`

plus `machine, ranks, exclusive, owner (agent/session), branch, job_id,
status (claimed | running | done | failed | superseded), result_path
(repo:branch:file), date`. Timing rows additionally carry `machine` in the
key (only Mx counts).

Practical points:

- Seed the registry from this note (every YES/PART row with its path).
- `code_class` is decided by the coordinator, not inferred from the commit
  hash: E597 covers `257b2e564` … `85b0c1de6` today (B1 head repeat); a new
  result-changing merge opens a new class and lists which rows it stales.
- Every partitioned run states `couplingReuse` and `requireAllResidualMeasures`
  explicitly in its case files (not via tutorial defaults), so head and
  `development` runs are comparable.
- `campaign/scripts/status.py` (or a small `registry.py check <key>`) refuses
  to submit when a `done`/`running` row with the same key exists.
