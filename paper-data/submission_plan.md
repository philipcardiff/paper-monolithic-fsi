# Solver paper: plan to submission

Status: 22 October 2026, draft v5 (`manuscript/conclusions`, PR #11; 65 pages,
builds cleanly). The solver is `feature-petsc-snes-quasi-monolithic` at
`85b0c1de6`. This file lists what each part of the paper still needs, the
figures to make, and the exact runs to do. Runs are listed here, not
started; Philip decides how many agents to launch.

## 1. Status by section

"Writing" means it can be finished now without results; "results" means
it waits for runs (Section 4 of this file).

| § | Section | Writing left | Waits on results |
|---|---|---|---|
| – | Title, abstract, keywords | Final pass after the results. | 9 `\tbd` in the abstract |
| – | Front matter | Emad Tandis's school or department at Aston; data and scripts archive (DOI); named solids4foam tag plus Zenodo DOI at submission | – |
| 1 | Introduction | Done. Two `\citetodo{companion …}` remain until the companion paper has a reference. | – |
| 2 | Governing equations | (a) Boundary conditions of each case, in an appendix or table pointing to the tutorials (todo). (b) Check the constitutive laws against the final case list (todo). | – |
| 3 | Method | Checked against the code (`paper-data/method_code_audit.md`). Eight of its 11 todos ask for **per-case settings**: ddt and convection schemes, α_d, tolerances, s_F and s_S, lag, mesh-motion law, solid-block preconditioner, decomposition, conservative transfer. **Recommendation:** put these in one case-settings table (already planned in §4, "one row per case"), fill it from `runs.csv`, and delete those todos. The other three: the BDF2 start-up `\tbd` (ring and Womersley), the `J_pp` scale-factor note, and the traction form (see §5). | Case-settings table |
| 4 | Verification against exact solutions | Text is written; there are 3 figure and 3 table placeholders. | WP1 |
| 5 | Consistency with partitioned coupling | The traction paragraph waits for the `viscousStressTranspose` check (WP0). | WP0, WP2 |
| 6 | Robustness | Collapsible-channel geometry figure (F-geo). | WP3 |
| 7 | Accuracy and cost | FSI3 figure update (conformal mesh; fix the stray arrow and blank space). | WP4, WP5 |
| 8 | 3-D performance and scaling | – | WP6 (timings on one machine with exclusive nodes) |
| 9 | Limitations | – | WP7, B1 |
| 10 | Conclusions | Done; all 34 `\tbd` repeat values from §§4–9. | Results |
| App. | Additional cases | Decide after the first full draft (keep, shorten or drop). | Optional |

**Journal template:** keep `sn-jnl` for the review stage (Philip, 22 Oct);
CMAME accepts any reasonable template there.

## 2. Figures

### F-geo: geometry and coarse mesh, one per case, same style

Tooling (done, 22 Oct): `figures/scripts/mesh_layer.py` draws the mesh
layer from ASCII `polyMesh` files to PDF, with a JSON bounding box.
`figures/tikz/geomstyle.tex` holds the shared annotation styles
(`geom outline`, `geom interface`, `geom dim`, `geom bc`, `geom point`,
`\geomdimx`, `\geomdimy`). Both were tested on a synthetic two-region
mesh.

Model: the existing Fig. 4 (cavityFlexibleBottom): a grey coarse mesh,
black outline, dimension arrows, boundary-condition labels and the monitor
point. The five existing figures (cavity, FSI3, blob, 3dTube, foilInWind)
were drawn by hand in Inkscape and vary in fonts and line weights. FSI3 also
has a stray arrow and blank space, and shows the non-conformal mesh.

**Proposed pipeline, so that every figure looks the same:**

1. **Mesh layer:** the case's coarsest mesh, exported by script. `blockMesh`
   is run, then a short Python script reads `constant/*/polyMesh` and draws
   the cell edges (fluid light grey, solid mid grey) to PDF with fixed line
   widths. For 3dTube, use a ParaView `pvpython` render of the surface mesh
   from a fixed camera.
2. **Annotation layer:** TikZ over the mesh image (`\includegraphics`
   inside a `tikzpicture`), so that dimensions, labels and arrows use the
   paper's fonts. One shared style file `figures/tikz/geomstyle.tex` sets
   the arrow tips, line widths and label font.
3. **Width:** full text width for elongated domains, single column for the
   ring and the tube cross-section.

Cases: ringAddedMass and womersleyTube (§4); collapsibleChannel (§6);
cavityFlexibleBottom (§5); FSI3 and blobInTreacle (§7); 3dTube (§8);
foilInWind (§9). The appendix cases are optional.

**Who:** step 1 needs OpenFOAM (`blockMesh`, a few seconds per case) on
Philip's machine. The coordinator, or one subagent, makes the mesh layers
and commits them to `figures/mesh/`. Step 2 needs only TeX and can run here
(TeX Live is installed in the coordinating session). It is one agent, and it
checks each figure as an image before committing. The existing
Inkscape-drawn figures are redrawn the same way, for consistency.

### F-field: field images (one per main case where it adds value)

These are made from the finished runs (or, for presentation only, from a
coarse level). One `pvpython` script, `campaign/scripts/field_images.py`,
fixes the colour maps, colour-bar placement, background and resolution:
perceptually uniform colour maps (viridis or cividis for magnitudes, a
diverging map for signed fields) and no rainbow maps. Proposed images:

- **FSI3:** vorticity, or velocity magnitude, around the flag at maximum
  tip deflection; the flag coloured by von Mises stress.
- **3dTube:** the pressure pulse on an axial cut at three instants, with
  the wall coloured by radial displacement (magnified).
- **cavityFlexibleBottom:** velocity magnitude with streamlines; the plate
  coloured by von Mises stress on its deformed shape.
- **collapsibleChannel:** velocity magnitude at the first trough; the
  deformed wall.
- **blobInTreacle:** velocity magnitude with the deformed half-cylinder
  coloured by stress.
- **ringAddedMass:** the pressure field of the vibration mode (optional).

These are presentation figures. They go next to each case's geometry figure
or as a single gallery figure, Philip's choice.

### F-data: data figures (from the results sections' placeholders)

Ten figures and nine tables are specified in §§4–9: axes, columns and
markers are already written in their `\todo`s. One shared plotting script
per section, under `campaign/scripts/`, reads `runs.csv` and `qois.csv` and
writes PGF/PDF in one style: Matplotlib with the paper's font and fixed
marker and line conventions (filled markers for quasi-monolithic, open for
partitioned).

## 3. Decisions (Philip, 22 October 2026)

1. **`viscousStressTranspose`:** decided after WP0 (0b/0c).
2. **Block with flexible tail:** dropped from the paper. A tutorial request
   is logged as solids4foam#615.
3. **Journal template:** keep `sn-jnl` for review.
4. **Field images:** next to each case's geometry figure. Final images come
   from a **medium or fine** level; coarse-level images may serve as
   placeholders or as a first look at the set-up.
5. **Animations** of the transient cases go in the supplementary material.
   They are made with `pvbatch`/`pvpython` scripts stored in this repository
   (`campaign/scripts/animations/`). Run a cheap test first and show Philip
   a short sample (a few frames or a GIF) before the full renders.
6. **ParaView on XenoSim:** render on the NVIDIA GPU. Check with
   `nvidia-smi` that `pvbatch` runs on the GPU, using an EGL/headless
   ParaView build if available; do not fall back silently to software
   rendering.
7. **MeluXina projects:**
   - use the **Amir/Colm project** first, from 22 October;
   - the "xenosim" project only if needed;
   - **never** the project running Hron–Turek x8 (Petar and Simon).

   Confirm the project IDs with `myquota` (and with Philip if unclear)
   before submitting. MeluXina is also the timing machine (exclusive nodes).
8. **WP0 and 8a** (mesh layers) are approved to start now.

## 3a. Decisions (Philip, 23 October 2026)

1. **FSI3 comparison (§7):** option (b) for now. Compare QM-AMI on the
   tutorial meshes with the verification paper's IQN-ILS tutorial-mesh runs
   (1x/2x/4x, already done). QM-AMI 1x/2x exist; the 4x is a new run (4a).
   QM against IQN-ILS on the conformal meshes (option a) may come later.
2. **3dTube (§8):** QM uses `directMap`, the verification paper's
   Robin–Neumann runs use AMI on the same meshes. State this in §8; no rerun.
3. **Cavity:** the partitioned runs reduce Δt with the level; this is fine
   for a steady case and is the point of the cost comparison.
4. **ringAddedMass:** run Robin–Neumann with the standard solid (1d).
5. **MeluXina project p201136** is Amirhossein and Colm's project (the
   "Amir/Colm project" of decision 7 above).
6. **Shared run registry:** `campaign/registry/registry.csv` (branch
   `campaign/registry`), seeded from `paper-data/reuse_map.md`. Every run
   is checked against it and claimed there before submission. Run agents
   follow `campaign/RUN_AGENT_BRIEF.md`.
7. **Schemes (23 Oct):** no `cellLimited` or similar limiters. QM runs use
   the same schemes as the case's partitioned tutorial: least-squares
   gradients, `linearUpwind grad(U)` (or `Gauss linear` where the
   partitioned file has it), `backward` in time. solids4foam branch
   `tutorials/monolithic-schemes-consistent` makes this the tutorial default.
   The `linearUpwind cellLimited leastSquares 1` entries never applied a
   limiter (one word is read as a gradient-scheme name; solids4foam#553),
   so earlier QM results are unaffected; only `ddt(U)` Euler to `backward`
   changes results.
8. **`viscousStressTranspose` (open):** `yes` is the formulation consistent
   with `pimpleFluid` (the term is in the residual and the traction). WP0 on
   blob shows QM `yes` differing from partitioned by −2.34/−1.04/−0.44%
   (x1/x2/x4) against −0.33/−0.29/−0.16% for `no`; a diagnostic (agent A)
   looks for the discrete mismatch. FSI3 4x and 3dTube L3 production runs
   wait for the decision.

## 3b. Transpose viscous term: fix, then rerun (23 October 2026)

`viscousStressTranspose no` leaves a mesh-independent wall offset on
womersleyTube (phase 4.8e-4 rad at every mesh); `yes` removes it, but on
blobInTreacle it turns the QM wall divergence into an O(h) spurious wall
force (`evidence/m-runs-a`: `paper-data/campaign/wp0/vST_diagnostic.md`,
`paper-data/campaign/m-runs-a/WP1_findings.md`). Agent A is fixing the
wall/interface evaluation of the term. Philip's decision: then **remove the
option** and hard-code the term with the corrected wall evaluation
(solids4foam branch from agent A; PR by the coordinator), together with
solids4foam#617 (schemes).

Every QM result at the current head is then superseded and rerun on the
fixed build ("R-fix"); partitioned results are unaffected:

| Case | QM runs to repeat | Who |
|---|---|---|
| blobInTreacle | x1/x2/x4 steady (0b/5a), temporal study (5b) | A |
| womersleyTube | m1/m2/m4 n200, m2 n50–n400 (1e) | A |
| ringAddedMass | 1a sweep, 1b, 1c, 1d (wall moves; effect expected small at ν = 1e-7) | A |
| cavityFlexibleBottom | L1–L4 (2a), 2b | A |
| foilInWind | Δt 0.0025, 0.005, 0.01 (7a) | A |
| collapsibleChannel | B2 (13109–13111) and the QM arm of 3b | B |
| ringAddedMass | QM arm of 3a | B |
| TurekHron2006 FSI3 | QM-AMI 1x check, then 4x (4a), 4e | C |
| 3dTube | QM L1/L2 (E597 values superseded), L3 (6a), 6e | C |

The QM results recorded so far (E597 and head) remain as the
"before the fix" record and may be cited for the effect of the fix.

## 3c. Ownership of runs (26 October 2026)

The coordinating session (claude.ai, owner of this plan) is in charge of the
campaign. Run owners:

| Owner | Work |
|---|---|
| M coordinator (xenosim session, subagent α; branch `evidence/campaign-r4r5`) | R4 FSI3 conformal QM and IQN-ILS 1x/2x/4x and tolerance sweep (option a, now included); R5 3dTube QM/RN L1–L3 (exact-arc L3); all timing windows (4b, 6b, 6c, 4c; needs #616/#624); block with tail (draft #623) |
| Agent C | FSI3 QM-AMI tutorial meshes 4x (option b) and its analysis; FSI3 field run (4e) if R4 does not cover it |
| Agent B | Robust QM mesh motion in the other tutorials (after #622) |
| Agent A | Done (`evidence/m-runs-a-rfix`) |

Every run is checked against and claimed in `campaign/registry` first.

**Block with tail:** back in the paper (Philip, 26 Oct) if the solids4foam
result matches the literature; otherwise left out (solids4foam#615, #623).

## 4. Runs (not started)

All runs: the solver branch head at the time of the run (with its commit
recorded); BDF2 (`backward`) for fluid and solid in transient cases;
tolerances set per case by the B1 rule (iterative error at most 5% of the
discretisation error; HANDOFF §10); provenance, `runs.csv` and `qois.csv` as
in `campaign/HANDOFF.md` §6. "QM" means quasi-monolithic; "part." means
partitioned with the strict coupling test. "Timing" means exclusive nodes on
the timing machine; everything else can run anywhere.

### WP0 — prerequisites (before the rest)

| ID | Case | Runs | Purpose | Notes |
|---|---|---|---|---|
| 0a | all | Rebuild at the solver head | One code version for the campaign | – |
| 0b | blobInTreacle | QM x1, x2, x4 × `viscousStressTranspose` yes/no; part. x1, x2, x4 | Decide the traction default (§5, Conclusions) | Serial, about 5 min each at x1 |
| 0c | womersleyTube | QM m2 n50, yes/no; RN and IQN-ILS m2 n50 | Same | About 80 s each |
| 0d | B1 | Cavity L3 and 3dTube L2 preconditioner windows (running on XenoSim) | Solid-block preconditioner per case | Under way |
| 0e | B2 | collapsibleChannel AMI 640×8 (running) | Solid resolution for §6 | Under way |

### WP1 — §4 exact solutions (2-D, cheap)

| ID | Case | Runs | Output |
|---|---|---|---|
| 1a | ringAddedMass | QM, 3 added-mass levels × mesh 1/2/4 × 25/50/100/200 steps per period (`--study monolithic` + mesh sweep) | Fig. 4.1, case-settings table |
| 1b | ringAddedMass | QM zero-gradient pressure, moderate and strong levels × mesh 1/2/4, 100 steps per period | Fig. 4.3 |
| 1c | ringAddedMass | QM non-conformal (`--study nonconformal`), conservative/interpolated × coarser/finer solid | Fig. 4.4 |
| 1d | ringAddedMass | Strong level, mesh 2, 25/50/100 steps per period: QM, IQN-ILS, RN, all with the standard solid (**timing**) | Table 4.2 |
| 1e | womersleyTube | QM m1/m2/m4 at 200 steps; m2 at 50/100/200/400 (`--monolithic`); RN and IQN-ILS on the same (for §5) | Table 4.3, Fig. 5.2 |
| 1f | ring and Womersley | BDF2 start-up check: the same QoIs with a second-order first step, or a start-up window excluded | `\tbd` in §3 |

### WP2 — §5 consistency

| ID | Case | Runs | Output |
|---|---|---|---|
| 2a | cavityFlexibleBottom | QM and part. (Aitken, strict) L1–L4, steady; Newton/coupling counts, time to steady state (**timing** for the time column) | Table 5.2, Fig. 5.1a |
| 2b | cavityFlexibleBottom | QM L2, L3 with `interpolate(U) linear` | Fig. 5.1b |
| 2c | cavityFlexibleBottom | `checkMesh` on final states (QM and part.) | Skewness note in §5 |

### WP3 — §6 robustness maps (many short runs; array job)

| ID | Case | Runs | Output |
|---|---|---|---|
| 3a | ringAddedMass | {Aitken, IQN-ILS, RN, QM} × {12, 25, 50, 100, 200 steps per period} × {weak, moderate, strong, extended} ≈ 80 runs, 2 periods each | Fig. 6.1 |
| 3b | collapsibleChannel | {Aitken, IQN-ILS, RN, QM} × Δt {0.025, 0.0125, 0.00625, 0.003125} × ρs/ρf {10, 1, 0.1, 0.01, 0} = 80 runs, to the first trough (fluid L2; solid per B2) | Fig. 6.3 |
| 3c | cavityFlexibleBottom (optional) | QM and Aitken, L3, Δt {0.0625 … 1.0} | Text or small table |

### WP4 — §7 FSI3 (heavy)

| ID | Case | Runs | Output |
|---|---|---|---|
| 4a | TurekHron2006 FSI3 | Option (b): QM-AMI on the tutorial meshes, 4x full run (1x/2x and IQN-ILS 1x/2x/4x exist; see the registry). Option (a), QM and IQN-ILS on the conformal meshes, deferred | Table 7.1, accuracy axis of Fig. 7.1 |
| 4b | TurekHron2006 FSI3 | Timing windows (2 periods from a periodic restart), same ranks per level for both (**timing**) | Cost axis of Fig. 7.1 |
| 4c | TurekHron2006 FSI3 | 2x tolerance sweep: QM `snes_rtol` 1e-4/1e-6/1e-8; IQN-ILS strict 1e-4/1e-5/1e-6 | Fig. 7.1 inset |
| 4d | TurekHron2006 FSI3 | Order of the QM u_x mean on 2x→4x (from 4a) | Sentence in the verification paper |
| 4e | TurekHron2006 FSI3 | Coarse run for the field image | F-field |

Cost guide: the earlier QM 4x took 3.6 h on 12 ranks; partitioned 4x took
about 40 h on 32 ranks.

### WP5 — §7 blobInTreacle (cheap)

| ID | Case | Runs | Output |
|---|---|---|---|
| 5a | blobInTreacle | QM and part., mesh x1/x2/x4, steady (BDF2, as the case is transient to steady) | Table 7.2 |
| 5b | blobInTreacle | QM temporal study, Δt 0.25 … 0.03125 s, error at t = 1 s (Liu et al. metric) | Fig. 7.2 |

B3 estimate: all of WP5 is under 0.1 core-hours.

### WP6 — §8 3dTube (heavy; timings)

| ID | Case | Runs | Output |
|---|---|---|---|
| 6a | 3dTube | QM L3, full 20 ms (driver: BDF2, BoomerAMG solid, `directMap`); L1/L2 exist (registry) | Table 8.1 |
| 6b | 3dTube | Strong scaling, L2 at 1–64 ranks and L3 at 16–128, QM and RN, 50-step windows (**timing**) | Fig. 8.1 |
| 6c | 3dTube | Preconditioner and Jacobian settings, L2, 8 ranks, 7 variants (**timing**) | Table 8.2 |
| 6d | 3dTube and ring | Newton residual histories, matrix-free against assembled Jacobian | Fig. 8.2 |
| 6e | 3dTube | Field image run (coarse) | F-field |

### WP7 — §9 foilInWind

| ID | Case | Runs | Output |
|---|---|---|---|
| 7a | foilInWind | QM Δt 0.01/0.005/0.0025 to 0.2 s, Newton histories at the stall; IQN-ILS Δt 0.01 | Fig. 9.1, Table 9.1 |

### WP8 — figures (see §2 of this file)

| ID | Task | Needs |
|---|---|---|
| 8a | Coarse meshes and mesh layers for 8 cases | OpenFOAM (minutes) |
| 8b | TikZ geometry overlays, shared style | TeX (coordinating session) |
| 8c | Field images | Runs from WP1–WP6 and ParaView |
| 8d | Data figures and tables from the CSVs | Runs |

## 5. Suggested agents and order

1. **Now (no new decisions needed):** finish WP0 (0b/0c are about 1 h of
   serial runs) together with 8a.
2. **After WP0 and the decisions in §3:** three run agents in parallel,
   each with at most two subagents:
   - **Agent A, 2-D and cheap:** WP1, WP2, WP5 and WP7 (correctness runs
     anywhere; its timing rows go to the timing machine);
   - **Agent B, maps:** WP3 as array jobs;
   - **Agent C, heavy:** WP4 and WP6 (accuracy runs now; timing windows
     from 1 November on MeluXina).
3. **In parallel, here:** 8b (geometry figures),
   then the data figures and tables as the CSVs arrive (8d), then 8c.
4. **Last:** fill the `\tbd`s, final pass on the abstract and Conclusions,
   case-settings table, named tag and Zenodo, cover letter and highlights.
