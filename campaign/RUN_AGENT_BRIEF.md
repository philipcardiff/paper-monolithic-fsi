# Run-agent brief (solver paper, from 23 October 2026)

You run the simulations the solver paper still needs. Read this file, then
`paper-data/submission_plan.md` (§§3, 3a and 4: decisions and run tables),
`campaign/HANDOFF.md` (§6 provenance and CSV format, §10 decisions log) and
`campaign/registry/README.md` (branch `campaign/registry`). Do not edit the
LaTeX; the coordinating session writes the text from your CSVs and notes.

## Hard rules

1. **Registry first.** Before submitting anything, run
   `campaign/registry/registry.py check <case> ...` on the latest
   `campaign/registry` branch. Reuse a matching `done`/`running` row; ask
   before running anything someone else has `claimed`. Rows claimed by
   "M run agent" are yours: set your agent name in `owner`, add the job ID,
   set `running`, and later `done` with `result_path`. Commit and push the
   registry change before each submission (small commits; pull first).
2. **Also check the verification paper** (philipcardiff/paper-fsi-verification:
   main, open PRs, especially draft #13, and its `paper-data/`) and the
   PROGRESS files of other agents on xenosim, MeluXina and the mac-studio
   for the same case. If in doubt, ask Philip.
3. **Code:** the head of `feature-petsc-snes-quasi-monolithic` at build time;
   record `git describe` in every run (`code_commit`). One build for the
   whole campaign unless Philip says otherwise. Timing windows that restart
   from a saved state need solids4foam#616 (restart fix); until it is merged,
   build it on top of the head for those runs only and note it.
4. **Schemes:** BDF2 (`backward`) for fluid and solid in every transient
   case; check `fvSchemes.monolithic`, several tutorials still say Euler.
   Euler is acceptable for steady pseudo-transient cases (cavity). IQN-ILS
   on the head uses `couplingReuse 0`; the `development` default is 5, so
   do not mix the two.
5. **Partitioned runs** use the strict coupling test
   (`requireAllResidualMeasures yes`).
6. **Tolerances:** the B1 rule (iterative error at most 5% of the
   discretisation error against a tight reference; HANDOFF §10). Record
   `snes_rtol`, `snes_stol`, `ksp_rtol` and the coupling tolerance.
7. **Machines:**
   - MeluXina: project **p201136** (Amirhossein and Colm) first; the
     "xenosim" project only if p201136 is out of hours; **never** the
     project running the Hron–Turek x8 runs (Petar and Simon).
   - Timing rows count only on MeluXina exclusive nodes. Correctness runs
     can go anywhere.
   - ParaView on xenosim must run on the NVIDIA GPU (check `nvidia-smi`
     while `pvbatch` runs; do not fall back to software rendering).
8. **At most two subagents at a time.** Do not change solver code; report
   failures to Philip with the log excerpt.
9. **Outputs:** one row per run in `runs.csv` and the QoIs in `qois.csv`
   (HANDOFF §6 columns, as in `paper-data/campaign/r0/` on branch
   `evidence/campaign-r0`), a provenance JSON per run, and a short findings
   note per work package. Push to a branch `evidence/m-runs-<wp>` on
   paper-monolithic-fsi and tell Philip; do not merge.
10. No model names in files or commit messages; end commit messages with
    the Co-Authored-By and Claude-Session lines given in your session.

## Order

### Step 1 — prerequisites (start now)

- **0b blobInTreacle:** QM x1, x2, x4 with `viscousStressTranspose` yes and
  no (BDF2). The partitioned x1/x2/x4 exist (registry); rerun them only if
  the registry row's code class or set-up does not match.
- **0c womersleyTube:** QM m2 n50 with the transpose yes and no; RN and
  IQN-ILS m2 n50 at the head.
- Report the 0b/0c differences (QM minus partitioned, both settings) in one
  table: they decide the traction default. These runs also serve the
  verification paper's pending QM reruns (#13), so record them in the
  registry promptly.
- **8a mesh layers:** from the R0 run directories on MeluXina
  (`/project/home/p201287/philip/qm-head/runs/r0/r0-*-backward-a`, plus
  `r0-foil-*` when done), convert the polyMeshes to ASCII
  (`foamFormatConvert -constant`, per region) and run
  `figures/scripts/mesh_layer.py` (branch `manuscript/submission-plan`) for
  the 2-D cases: cavityFlexibleBottom, TurekHron2006 (FSI3 conformal and
  tutorial meshes), blobInTreacle, ringAddedMass, womersleyTube (wedge),
  collapsibleChannel, foilInWind. Use the coarse (tutorial or L1) level.
  For 3dTube, render a ParaView surface view of the L1 mesh (GPU). Push the
  PDFs and their JSON bounding boxes to `figures/mesh/`.

### Step 2 — the gaps

Only the items marked MISS or PART in `paper-data/reuse_map.md` (branch
`evidence/reuse-map`), as planned in `submission_plan.md` §4, each checked
against the registry first. In order of value to the paper:

1. **1a, 1d, 1e** (ring QM sweep; ring QM, IQN-ILS and RN with the standard
   solid at the strong level; Womersley QM cells) — cheap, 2-D.
2. **2a** cavity QM L1–L4 Newton counts and time to steady state (the
   partitioned values exist), then the timing repeats on Mx.
3. **5a QM, 5b QM** (blobInTreacle backward; the partitioned arms exist).
4. **4a option (b):** QM-AMI FSI3 on the tutorial 4x mesh, full run
   (1x/2x QM-AMI and IQN-ILS 1x/2x/4x exist). Option (a) is deferred.
5. **6a** 3dTube QM L3 (`directMap`; RN L3 exists with AMI and must not be
   rerun).
6. **1b, 1c, 1f, 2b, 2c** (ring ablations, cavity interpolation, BDF2
   start-up check, `checkMesh`).
7. **Timing (Mx exclusive, from 1 November):** 1d, 2a, 4b, 6b, 6c; then
   **3a/3b** robustness maps as array jobs, **4c** and **6d**.
8. **7a** foilInWind: wait for the R0 foilInWind run and reuse it for
   Δt 0.0025.

Field images (8c) and animations come after the medium or fine runs exist;
make one cheap test render per case first and show Philip before full
renders (scripts in `campaign/scripts/animations/`).

## Reporting

After each step, post to Philip: what ran (registry rows), where the CSVs
are, anything that disagrees with an earlier result by more than the
expected discretisation error, and core-hours used per project.
