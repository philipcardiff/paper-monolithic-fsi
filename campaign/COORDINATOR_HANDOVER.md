# Handover: solver-paper coordinator (29 October 2026)

This file hands the solver-paper ("M") coordination over from the claude.ai
cloud session `session_012eCpLcNxxfzvWqVxKGHaeu` to a single new session
on Philip's mac-studio. From now on that one session coordinates, runs and
writes. There are no other M run agents: agents A, B and C and the M campaign
coordinator are stopped, and their environments are gone.

Read in this order:

1. This file.
2. `paper-data/submission_plan.md` (this branch): §§1–4 give the section
   status and the run plan, §§3–3c the decisions.
3. The coordination board, philipcardiff/paper-monolithic-fsi PR #13
   (draft, "Campaign coordination board", do not merge). Its comments from
   26 Oct onwards are the most recent record.
4. `campaign/RUN_AGENT_BRIEF.md` (hard rules for runs) and
   `campaign/registry/README.md` (branch `campaign/registry`).

## 1. The two papers

- **M (this paper):** philipcardiff/paper-monolithic-fsi, target CMAME. A
  quasi-monolithic (QM) cell-centred FV FSI method: JFNK with the assembled
  approximate Jacobian as fieldsplit preconditioner, in solids4foam with
  PETSc.
  - Authors: Cardiff, Tandis (Aston), Batistić last.
  - Draft: `main`, built with `latexmk -pdf article.tex`.
- **V (verification paper):** philipcardiff/paper-fsi-verification.
  - It has its own coordinator ("Verification coordinator" on the board).
  - It uses partitioned results. Monolithic results may stay in V for now.
  - Its runs use MeluXina project **p201141**.
  - Coordinate with it on the board; do not direct it.

## 2. Code state (solids4foam)

The solver branch is `feature-petsc-snes-quasi-monolithic`, head
**`a421f063d`**. Draft PR solids4foam/solids4foam#233 merges it into
`development`. Merged since 22 Oct, all reviewed:

| PR | What | Effect on QM results |
|---|---|---|
| #616, #624 | restart fixes | continuous runs bit-identical |
| #617 | QM tutorial schemes = partitioned; `cellLimited` was never active (#553 notation); `ddt(U)` `backward` | backward changes some tutorials |
| **#618** | `viscousStressTranspose` option **removed**: transpose term always in residual, wall pressure gradient and traction; wall value from a decomposition-independent least-squares surface fit of the wall velocity; cached once per residual (+2% wall) | **all QM results before `4ae081609` superseded** |
| #619, #621 | tutorial root; processor point sync (fixes the 4-rank FSI3 t = 2.002 crash; confirmed) | – |
| #622, #626 | QM mesh-motion predictor (`predictor yes`, `ddt(D) backward`) in collapsibleChannel (+ `diffusionHyperElastic`, quadratic inverseDistance), blob, cavity, TurekHron2006 | converged results unchanged (≤ 1.3e-7) |
| #625 | 3dTube exact wall arcs (fluid/solid walls coincide; L3 `directMap` works) | ≤ 1e-6 m geometry |
| #628 | `development` merged in (#554 couplers, #578, …) | QM A/B **bitwise identical** in 7 cases |
| #630 | PETSc SNES option for `meshMotionTotalDisplacement` (opt-in) | none (not used by tutorials) |

Decisions that stand:
- **Time stepping:** BDF2 (`backward`) for fluid and solid in transient cases; Euler is fine for the steady cavity.
- **Schemes:** least-squares gradients and `linearUpwind grad(U)`, matching each case's partitioned file. `interpolate(U) skewCorrected linear` stays where the partitioned file has it. Plain `linear` was tested and rejected on FSI3: it moved u_y by −11%.
- **QM mesh motion stays as it is** (total-Lagrangian pseudo-solid with the predictor). `meshMotionTotalDisplacement` was tested and **not adopted**:
  - FSI3 differences shrink only 1.2–2.4× per level.
  - The blob u_y difference levels off at about 2.4% and does not shrink.
  - On the Hessenthaler flap it inverts the mesh at t = 0.62 s, where `velocityLaplacian` survives.
  - PETSc is 2.3–10× slower.
  - Details: board comments of 27–28 Oct.
  - Philip has not overruled the recommendation not to switch; confirm with him once.
- **Block with tail** (draft #623): goes in M if it matches the literature.

## 3. Results in hand (fixed code, ≥ `1252bd2e5`)

| Case | Where | Note |
|---|---|---|
| ring 1a–1d, Womersley 1e, blob 5a/5b, cavity 2a/2b, foilInWind 7a | `evidence/m-runs-a-rfix`, `paper-data/campaign/m-runs-a-rfix/RFIX_findings.md` | Womersley vST offset gone; blob order 1.9; foil Δt 0.01 still stalls at 0.05 s |
| robustness maps 3a (ring), 3b (collapsible), B2 | `evidence/m-runs-b`, `paper-data/campaign/wp3/` | 3b QM 20/20 after the mesh-motion fix; RN ρ=0 "not applicable" |
| FSI3 QM-AMI tutorial meshes 1x/4x (option b) | `evidence/m-runs-c`, `paper-data/campaign/c/4a_findings.md` | 4x within 3.3% of Featflow; IQN-ILS 4x overshoots. The 2x on the fixed build was requested from agent C and **probably not run**: check the registry |
| FSI3 conformal QM 1x/2x/4x, IQN-ILS 1x (diverged 5.94 s)/2x, 2x tolerance sweep; 3dTube QM and RN L1/L2 | `evidence/campaign-r4r5` (`paper-data/campaign/r4/`, `r5/`) | at `18a24427f`; still valid (A/Bs above) |
| WP0, vST diagnostic | `evidence/m-runs-wp0`, `evidence/m-runs-a` (`paper-data/campaign/wp0/`) | history of the #618 fix |
| mesh layers (8a) | `figures/mesh-layers` (not merged) | 9 layers; thin ones need cropping |

## 4. Open work, in order

1. **Read the board and the registry.** Stale `running` rows by "M coordinator (merge A/B)" (Mx 5388478) are finished: set them to `done`, results in the #628 description. The `M R0` foilInWind row is stale too.
2. **Blob steadiness:** blob x4, current vs `meshMotionTotalDisplacement` + SNES set-up, both to t = 6. Report u_x and u_y at t = 3, 4.5 and 6, and the residual mesh motion. Asked on the board on 28 Oct; not done.
3. **FSI3 mesh audit**, meshes only: the maximum neighbour cell-size ratio per level, and where it occurs, for the tutorial and the conformal FSI3 meshes. Compare with V's finding (≤ 1.43 standard family, 2–2.8 ring+box, which is not asymptotic at 8x′). Not done.
4. **FSI3 QM-AMI 2x on the fixed build,** if not already run, so the 1x/2x/4x series is on one code version.
5. **3dTube QM L3** (approved, QM only).
   - Scripts: `evidence/campaign-r4r5`, `paper-data/campaign/r5/jobs/l3_setup.sh`, `farm_job_l3.sh`; build at `a421f063d`.
   - About 1,250 core-h on 64 ranks; fields only at 20 ms.
   - Record `env | sort` and `which mpirun` in each run directory. A start-up rc 139 seen once came from the launcher environment; 15 of 15 clean launches since.
6. **Timing windows** (exclusive MeluXina nodes, run once for both papers):
   - Start from `TIMING_JOBS.md` on `evidence/m-runs-c` (about 34 node-hours) plus agent A's claimed timing rows (ring 1d, cavity 2a; registry, "from 1 November").
   - **Post the final list and core-hours on the board and get Philip's go before submitting.**
7. **Paper writing,** once results land (`submission_plan.md` §1):
   - **Case-settings table** from `runs.csv` files; then delete the Method section's per-case todos.
   - **Method text:**
     - the transpose term is always on, with the wall surface fit;
     - the mesh-motion predictor;
     - the schemes rule;
     - the BDF2 Euler first step (Nishikawa2019bdf2); 1f found no start-up effect.
   - **§5:** blob vST story (WP0 → #618), as a short paragraph if useful.
   - **§7:** FSI3 option (b) tables (4a) plus R4 conformal; mesh-family caveat after item 3.
   - **§8:** QM uses `directMap`, RN in V uses AMI on the same meshes.
   - **Figures:** TikZ geometry figures over the mesh layers (`figures/tikz/geomstyle.tex`, `figures/scripts/mesh_layer.py`); field images from medium/fine runs (ParaView on xenosim must use the NVIDIA GPU); animations as supplementary material, with pvbatch scripts in `campaign/scripts/animations/` (show Philip a cheap test first).
   - **Housekeeping:** fill the `\tbd`s; sync V's bibliography with `Nishikawa2019bdf2`.
8. **Merge housekeeping:** this branch (`manuscript/submission-plan`) has 6+ commits not on `main`; PR to `main`. Also `figures/mesh-layers` and, at the end of the campaign, `campaign/registry`.

## 5. Rules

- **Machines:**
  - MeluXina: **p201136** (Amirhossein and Colm) first; the "xenosim" project only if needed; **never** the project used by Petar and Simon for Hron–Turek x8. The verification paper uses p201141.
  - p201136 has a **file quota**: write fields sparingly, delete fields after extracting QoIs.
  - Timing rows count only on exclusive MeluXina nodes.
  - From the mac-studio: `ssh -i ~/.ssh/id_ed25519_mlux meluxina`; xenosim by SSH as well.
- **Registry:**
  - Check, then claim, in `campaign/registry/registry.csv` before every submission.
  - Close rows with `result_path`.
  - Mark superseded rows.
- **Code:**
  - Record the solids4foam commit (`git describe`) per run.
  - No solver changes without a PR.
  - solids4foam PRs go to `feature-petsc-snes-quasi-monolithic`; merge commits (repo convention) after green CI and a before/after QM A/B for anything that touches QM code.
  - Tell Philip before merging anything that changes QM results.
- **Writing:**
  - No AI model names in files or commits.
  - Commit trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  - GitHub comments end with the Claude Code footer.
  - British spelling, one sentence per line in LaTeX, never a number without a source.
- **Decisions:** Philip makes them. Put **DECISION:** questions on the board or to Philip directly, with a recommendation.
- **Board etiquette:** comments start with `**From:** … · **To:** … · **Re:** …`. Read it before each submission.

## 6. People and other sessions

- **Philip Cardiff** (philip.cardiff@ucd.ie): decides.
- **Verification coordinator:** posts on the board. Its FSI3 8x′ result: the ring+box mesh family is not asymptotic; it is running a smooth-mesh replay on p201141.
- **Hessenthaler session:** works with the verification coordinator.
- **Emad Tandis and Željko Tuković:** the ANSYS and material-law discussion on V #12 (cavity; StVK vs neo-Hookean). It only affects M if V's cavity reference changes.
