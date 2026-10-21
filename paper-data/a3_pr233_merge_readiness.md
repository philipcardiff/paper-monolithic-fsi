# A3: merge readiness of solids4foam/solids4foam#233

Assessed 2026-10-20, read-only (GitHub API + local clone `/home/user/solids4foam`, no fetch).

- PR: draft, open, "Quasi-monolithic Newton FSI coupling (NewtonQuasiMonolithic): second order, parallel, non-conformal interfaces", milestone "Monolithic FSI solver".
- Head `origin/feature-petsc-snes-quasi-monolithic` = `257b2e5640bb` (merge of #599, 2026-10-19); the GitHub API reports the same head SHA, so the local refs are current.
- Base `origin/development` = `65de26a00ae8` (merge of #584, 2026-10-19).
- Size: 448 commits (GitHub), 364 files changed, +27 644 / −1 068 (280 added, 84 modified, 0 deleted).

Classification: **BLOCKER** = must be done before merge or before tagging the paper's version; **SHOULD** = expected for a clean merge, low effort; **NICE** = optional.

## 1. PR status

| Item | Finding | Class |
|---|---|---|
| Draft state | Still draft. Philip's comment of 2026-04-02 said to wait until the benchmarks and paper are ready. | BLOCKER (mark ready for review when the rest is done) |
| Unchecked checklist: "GitHub Actions CI on the current head (green on `ba41dab` ...)" | Out of date: all 21 check runs on `257b2e5` completed `success` (one, preCICE, `skipped`). Tick it and drop the `ba41dab` note. | SHOULD |
| Unchecked checklist: "`tutorials/Alltest-regression` passes" | CI job "Build and regression test on OpenFOAM-v2512-PETSc" (job 118289559503) ends with "All regression tests PASSED", total 02h:08m:31s; the OpenFOAM-9-PETSc and foam-extend-4.1-PETSc regression jobs also pass. Tick it. | SHOULD |
| Review threads | 10 threads (iBatistic, 2026-03-31/04-02), all `is_resolved: true`. No open review threads. | – |
| Approving review | None. All 19 reviews are `COMMENTED`; iBatistic's summary review was on `8fa81a0f` (March). The branch has changed fundamentally since (#580–#599). | BLOCKER (re-request review from iBatistic) |
| Open conversation item | iBatistic (2026-04-13) asked about `applications/scripts/solidModelDicts/linearGeometryTotalDisplacement.snes/`; Philip agreed to remove it. That directory is no longer in the branch tree (checked `git ls-tree`), so done, but not acknowledged in the thread. | NICE (reply) |
| Stacked PR #581 (split `foamPetscSnesHelper`) | Open, not draft, base = this branch at `b6c7743e5`, reviewer requested (iBatistic). Its base is now behind #593/#594/#596/#597/#599. Decide: merge into #233 first, or retarget to `development` after #233. | SHOULD (decision) |
| Description currency | Lists merged PRs #580, #582, #586, #589, #590 only; #593, #594, #596, #597 and #599 are merged on the branch but not mentioned. #594 and #597 change results (#597: Hron–Turek rigid-plate lift amplitude 13% → 3% below `pimpleFluid`, per CHANGELOG). Most "Test Cases and Results" numbers predate #594/#597. | SHOULD |
| Mergeability | GitHub: `mergeable_state: clean`. | – |

## 2. Merge into current development

`git merge-tree --write-tree --name-only origin/development origin/feature-petsc-snes-quasi-monolithic` exited 0 and printed only the tree id (`7ebcb134bcf5`): **no conflicts**. The branch is 7 commits behind `development` (2 178 ahead), and those 7 merge cleanly.

## 3. Development artefacts and dead code

No scratch result/TODO markdown files of the form `MONOLITHIC_PETSC_*.md`, no `.dev/agent_log.md` (removed in `9d987257`), and no `*.snes/` debug dictionaries are in the branch tree.

| Path | Finding | Class |
|---|---|---|
| `.claude/skills/solids4foam/SKILL.md`, `.agents/skills/solids4foam/SKILL.md` | Present, but already on `development`; not part of this PR's diff. | – (out of scope) |
| `src/solids4FoamModels/fluidSolidInterfaces/newtonQuasiMonolithicCouplingInterface/newtonQuasiMonolithicCouplingInterface.{C,H}`: `precondition()` (C ~l. 3341 onwards, "Work in progress ... Newton iterations stall"), member `solidSubKSP_` (H l. 142) | The coupler's physics-based block preconditioner: unused by every tutorial, does not work on `ringAddedMass`, dropped from the paper. Dead code in a new class. Remove (or move to a follow-up branch). | SHOULD |
| `newtonQuasiMonolithicCouplingInterface/README.md` l. 191; `fluidModels/newtonIcoFluid/newtonIcoFluid.H` l. 363–364 | Document the WIP physics preconditioner; update with the above. | SHOULD |
| `tutorials/fluidSolidInteraction/{3dTube,TurekHron2006,beamInCrossFlow,blobInTreacle,cavityFlexibleBottom,collapsibleChannel,mokLidDrivenCavity,perpendicularFlap,ringAddedMass,womersleyTube}/system/fluid/fvSolution.monolithic` | Each carries a block "Physics PC inner solvers (used only with pc_type physics)", i.e. settings for the WIP preconditioner. Remove with it. | SHOULD |
| `src/solids4FoamModels/numerics/foamPetscSnesHelper/foamPetscSnesHelper.C` (`PCApplyPhysics`, `-pc_type physics` registration) | The generic `physics` PC hook already exists on `development`; not introduced here. Keep. | – |
| `src/solids4FoamModels/fluidModels/newtonIcoFluid/README.md` (new file), "Related Files" | Lists `tutorials/fluids/cylinderInChannel/system/fvSolution.newtonIcoFluid` and `fvSolution.newtonIcoFluid.physicsPC`; neither file exists on the branch. Also documents `pc_type physics` / `pc_physics_type model` (l. 146–226, 383–414). Fix references; trim or label the physics-PC section. | SHOULD |
| `newtonQuasiMonolithicCouplingInterface.C` l. 938 `// TODO: use the corrected version of fixedValue`; `foamPetscSnesHelper.C` l. 2032 `// TODO: add the extra Newton linearisation tensor terms` | New TODOs. Harmless, but each should either become an issue or be reworded as a note. | NICE |
| `tutorials/fluidSolidInteraction/womersleyTube/verification/temporal/production/verification_summary_monolithic.md`, `womersleyTube_results_monolithic.csv` | Committed results (commit `54a5c6916`, 2026-10-16), i.e. before #594 and #597 were merged (2026-10-18/19). Same convention as the committed partitioned `production/` files on `development`, so not a stray file, but likely stale. Rerun after #597 or label with the commit they were produced with. | SHOULD |
| Debug options `interfaceFluxDiagnostics`, `stopOnPetscError`, `logTimeStepAdjustments` | Documented user options with defaults off; acceptable. | – |
| Pending fix branches | `origin/fix/foilInWind-monolithic-timestep` (1 commit, `b157ecaf3`) and `origin/verification/cavityflexiblebottom-partitioned-fine` (2 commits incl. the post-#597 monolithic rerun `f356c3242`) are not on the PR branch. | SHOULD (merge into the branch before the tag) |

## 4. Build coverage and guards

CI on `257b2e5` (workflows `buildAndTest.yml`, `buildAndRegressionTest.yml`): build succeeds on OpenFOAM v2312, v2412, v2512, OpenFOAM-9 and foam-extend-4.1, each with and without PETSc (v2312/v2412/v2512/9/fe-4.1 "-PETSc" jobs; plain v2312/v2412/v2512/9/fe-4.1 jobs). No job builds OpenFOAM-v2606 on the PR (`buildAndTest-v2606.yml` is manual).

Guards (read from the branch):

- `newtonQuasiMonolithicCouplingInterface.C`: whole file inside `#ifdef USE_PETSC` → `#ifdef OPENFOAM_COM` (l. 20/22, closed at l. 3478/3480). The `.H` includes `foamPetscSnesHelper.H` unguarded but is only included by the guarded `.C`. Listed in both `Make/files.openfoam` and `Make/files.foamextend`, so it compiles to an empty unit off OpenFOAM.com or without PETSc.
- `nonLinGeomTotalLagVelocitySolid.H`: PETSc-specific members inside `#ifdef USE_PETSC` (l. 256–280); version differences via `OPENFOAM_COM`/`OPENFOAM_NOT_EXTEND`. `linGeomVelocitySolid` derives from it and has no guards of its own. Both are in both file lists.
- `fsiSteadyStateControl.C`: `#ifdef OPENFOAM_COM` around the whole file; listed only in `files.openfoam`.
- `twoDPointCorrectorS4f`: listed only in `files.openfoam` (an alias of `twoDPointCorrector` off OpenFOAM.com per the PR text).
- `Make/options`: PETSc include/link only under `ifdef PETSC_DIR`.
- Tutorials: `./Allrun monolithic` stops with `solids4Foam::caseDoesNotRunWithOpenFOAMOrg` / foam-extend checks (fixed after the March review, commit `8fa81a0f`).

Assessment: non-PETSc and non-OpenFOAM.com builds are covered by CI and pass. **No blocker.** Note for the paper and README: the coupler is OpenFOAM.com + PETSc only (tested v2512; CI also builds v2312 and v2412 with PETSc).

## 5. Tests

| Tutorial | Monolithic regression arm | Runs in CI |
|---|---|---|
| `beamInCrossFlow` | yes (`regressionTest.sh`, `coupling == monolithic`) | yes, v2512-PETSc job |
| `blobInTreacle` | yes (l. 258–263, only if `WM_PROJECT_VERSION` starts with `v` and `PETSC_DIR` is set) | yes, v2512-PETSc job |
| `cavityFlexibleBottom` | yes (l. 210–214, same condition) | yes, v2512-PETSc job |
| `ringAddedMass`, `womersleyTube`, `3dTube`, `mokLidDrivenCavity`, `collapsibleChannel`, `TurekHron2006` | no; opt-in verification drivers only (`Allverify ...`) | no (hours each) |
| `perpendicularFlap`, `membraneRoof`, `foilInWind` | no | no |

All three arms are in `tutorials/Alltest-regression` (l. 176–178). On OpenFOAM-9-PETSc and foam-extend-4.1-PETSc the arms print a skip. Not verified: that the v2512 log actually ran (rather than skipped) the monolithic arms — the tail of the log shows only the final cases; the run conditions are met in that container (`PETSc sanity check` step, `v2512`).

| Gap | Class |
|---|---|
| No monolithic regression check against an exact solution. A short `ringAddedMass` monolithic arm (a few periods on mesh 1, check against the exact wet/dry frequency ratio) would protect contribution 2 of the paper. | SHOULD |
| No parallel or AMI (non-conformal) monolithic regression. A 2-rank `blobInTreacle` or the ringAddedMass `nonconformal` study's smallest case would cover `decomposeParMonolithic` and `conservativeTractionTransfer`. | NICE |
| Confirm in a log that the three monolithic arms ran on v2512-PETSc (search the job log for "Running monolithic"). | SHOULD |

## 6. Documentation

| Item | Finding | Class |
|---|---|---|
| `CHANGELOG.md` `[Unreleased]` | Has an "Added" entry for the coupling, velocity solids, `fsiSteadyStateControl`, `foilInWind`; "Changed" for quieter mapping logs; "Fixed" entries for #597 and the SNES Jacobian. Complete in substance. The "Added" paragraph is one ~40-line bullet; splitting into 4–5 bullets would help. | NICE |
| Coupler README options vs code | Keys read in `newtonQuasiMonolithicCouplingInterface.C`: `adjustTimeStep`, `conservativeTractionTransfer`, `fluidSystemScaleFactor`, `interfaceFluxDiagnostics`, `logTimeStepAdjustments`, `maxDeltaT`, `maxTargetNIter`, `maxTimeStepRetries`, `minDeltaT`, `minTargetNIter`, `optionsFile`, `passViscousStress`, `petscOptions`, `solidSystemScaleFactor`, `stopOnPetscError`, `timeStepLogFile` (+ `interfaceTransferMethod` from the base class). All appear in the README. No documented-but-removed option found. | – |
| Removed options | `quasiMonolithicInterfaceFluxMode`, `liuInterfaceCondition`, `extrapolateSolidInterfaceDisplacement`, `zeroPressureStabilisationFluxOnFsiInterface`, `extrapolateTractionBoundaries`, `linearElasticFormulation`: no occurrence left in `src/`, `tutorials/`, `applications/`. | – |
| `newtonIcoFluid/README.md` | References two non-existent tutorial files (see §3); physics-PC section. | SHOULD |
| Top-level `README.md` | Not touched by the PR. A one-line mention of the monolithic coupling (OpenFOAM.com + PETSc) and its paper would help users find it. | NICE |
| PR "Known limitations" | Lists the physics preconditioner as WIP; update once removed. The beamInCrossFlow 4–5% gap, 3x-mesh Newton stall and solid pressure oscillations are open technical items; they need not block the merge if stated in the coupler README. Check they are in the README, not only the PR body. | SHOULD |
| Citation | `CITATION.cff` is `version: "2.4"`, `date-released: "2026-08-24"`. | see §7 |

## 7. Reproducible tag for the paper

| Item | Finding | Class |
|---|---|---|
| Version string | Latest tag is `v2.4` (CITATION 2026-08-24); the coupler exists only on the PR branch. The paper must cite either a release (e.g. v2.5) containing the merged PR, or an explicit tag on `development` after the merge. A commit SHA on a feature branch is not durable (branches get deleted after merge). | BLOCKER |
| Commit recorded by tutorials | The verification drivers (`ringAddedMass`, `womersleyTube`, `3dTube`, `channelLeaflet`) record hashes of `0/`, `constant/`, `system/`, `Allrun`, the OpenFOAM version, and a fingerprint of the solids4foam executable and library in `verification_settings.json`; none records the git commit (`git rev-parse HEAD` / `git describe --dirty`). The fingerprint identifies a build, not a source revision. | SHOULD (add the commit and dirty flag to the settings/summary) |
| PETSc / HYPRE / MUMPS versions | Not recorded by any driver. `etc/check-petsc.sh` reads `petscversion.h` at build time (prints it) but it is not stored. Verification READMEs mention versions ad hoc (`collapsibleChannel`: "OpenFOAM v2412 and PETSc 3.24 ... also on macOS with PETSc 3.22"); others give only "OpenFOAM v2512". Write `PETSC_VERSION_*`, `PETSC_ARCH` and the HYPRE/MUMPS versions from `petscconf.h` (or `-log_view` header) into each driver's settings file, and state them in the paper. | BLOCKER for the paper (SHOULD for the merge) |
| Results produced before #594/#597 | Any number in the paper must come from runs at or after the tagged commit; committed `womersleyTube` monolithic production files and most PR-body numbers predate #594/#597. | BLOCKER for the paper |
| Pending fix branches | foilInWind Δt/4 and the post-#597 cavityFlexibleBottom rerun must be on the tagged commit. | BLOCKER for the paper |
| Docker image | CI images (`philippic/openfoam-v2512:ubuntu-22.04-petsc-no-openmp-system-blas-gmsh`) are tagged by name, not digest. Recording the image digest (or a released solids4foam Docker image via `docker-release.yml`) would give a reproducible environment. | NICE |
| Zenodo DOI | Not checked whether solids4foam releases are archived on Zenodo; CMAME data-availability statements generally expect a DOI. | NICE |

## Checklist for the PR (paste-ready)

```markdown
### Before merge
- [ ] Update the description: add merged #593, #594, #596, #597, #599; refresh result numbers after #594/#597
- [ ] Tick CI (all green on 257b2e5) and Alltest-regression (v2512-PETSc, OF-9-PETSc, fe-4.1-PETSc jobs pass)
- [ ] Confirm in the v2512-PETSc regression log that the three monolithic arms ran (not skipped)
- [ ] Decide on #581: merge here first, or retarget to development afterwards
- [ ] Merge fix/foilInWind-monolithic-timestep and verification/cavityflexiblebottom-partitioned-fine into this branch
- [ ] Remove the coupler's WIP physics preconditioner (`precondition()`, `solidSubKSP_`), its README/header notes and the "Physics PC inner solvers" blocks in 10 `fvSolution.monolithic` files
- [ ] newtonIcoFluid README: fix references to non-existent `cylinderInChannel/system/fvSolution.newtonIcoFluid{,.physicsPC}`; trim or label the physics-PC section
- [ ] Rerun or label (with commit) `womersleyTube/verification/temporal/production/*_monolithic.*` (produced before #594/#597)
- [ ] Move open limitations (beamInCrossFlow gap and 3x-mesh stall, solid pressure oscillations) into the coupler README
- [ ] Re-request review from @iBatistic; mark ready for review
- [ ] (optional) ringAddedMass monolithic regression arm against the exact frequency ratio
- [ ] (optional) turn the two new TODOs into issues; split the CHANGELOG "Added" bullet; one line in the top-level README

### For the paper tag
- [ ] Verification drivers record `git describe --always --dirty` and PETSc/HYPRE/MUMPS versions in `verification_settings.json`
- [ ] Merge, then tag a release (e.g. v2.5) or a named tag on development; update CITATION.cff
- [ ] All paper results produced at the tagged commit; record OpenFOAM, PETSc, HYPRE versions and the Docker image digest
```
