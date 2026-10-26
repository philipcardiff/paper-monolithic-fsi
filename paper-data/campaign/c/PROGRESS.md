# Run agent C: heavy cases (WP4 FSI3, WP6 3dTube) — progress

Branch `evidence/m-runs-c`. Machine: MeluXina, account p201136.
Code: since 24 Oct the **#618 build** `/project/home/p201136/philip-agentC/build-4ae0816`
(compiled at 4ae081609, tree moved to `v2.4-1115-g1252bd2e5` = #618 +
#617, which changes tutorials only). The 23 Oct 1x checks below used the
R0 build (`v2.4-1103-g85b0c1de6`, pre-#618) and are superseded.
Run directories: `/project/home/p201136/philip-agentC/runs/`.

## Decisions in force (23 Oct 2026)

- QM run copies use the partitioned fluid schemes: no `cellLimited`,
  `div(phi,U) Gauss linearUpwind grad(U)`, `gradSchemes default
  leastSquares`, `ddt(U) backward` (Philip, via the coordinator).
- `viscousStressTranspose` (decided 23 Oct): the option is removed and the
  corrected wall treatment of the transpose term is hard-coded (agent A).
  FSI3 4x and 3dTube L3 wait for the fixed build; then the 1x check is
  rerun on it first.

## #618 build (24 Oct)

Tutorial files at 1252bd2e5 used as they are (partitioned schemes;
TurekHron2006 keeps `interpolate(U) skewCorrected linear`, 3dTube has none,
as its partitioned file); no `viscousStressTranspose` in any run copy. The
3dTube driver copy takes `writeInterval` from `$AGENTC_WRITE_INTERVAL`
(`jobs/setup_copy.py`). Registry: pre-#618 FSI3/3dTube QM rows superseded.

**Batch 1** (Mx 5382225, 1 exclusive node, 36 min, 3 × 8 ranks):

- **FSI3 QM-AMI 1x check: passes.** Against the V IQN-ILS tutorial 1x:
  `u_x` mean +6.43% (smaller magnitude), `u_y` amplitude −4.61%, drag mean
  −0.65%, lift amplitude −4.39%; agent A: +6.4 / −4.6 / −0.6 / −4.4%.
  Against pre-#618 QM-AMI 1x: `u_y` amplitude 28.474 vs 28.831 mm (−1.2%),
  `u_x` mean −2.0886 vs −2.1424 mm. 1.80 Newton per step (max 4).
- **3dTube QM L1: done.** `u_r,max(A)` 0.159658 mm (pre-fix 0.15949,
  +0.1%), `t` 7.225 ms (same), `u_z,min(A)` −0.089023 mm (+0.07%).
- **3dTube QM L2: failed** at t = 5 ms (could not create its first field
  directory): the p201136 **file quota** (1 M files) was full. Cause: the
  1x run wrote fields every 10 steps (702 times × 9 directories). I deleted
  the 1x times below 6.8 s (187 000 files freed, quota 80%). The 1x solver
  had finished; its analysis was rerun with `--reuse`. L2 rerun in batch 2.

**Batch 2** (Mx 5382421, 1 exclusive node, submitted 24 Oct ~23:20):
FSI3 QM-AMI 4x (32 ranks, writes t = 7 s only), 3dTube QM L3 (32 ranks,
fields every 2.5 ms incl. the 5 ms restart state), 3dTube QM L2 (8 ranks,
fields every 2.5 ms).

**Batch 2 status (25 Oct ~09:30)**, Mx 5382421 survived the MeluXina login
maintenance:

- **3dTube QM L2: done.** `u_r,max(A)` 0.159826 mm (pre-fix 0.15978,
  +0.03%), `u_z,min(A)` −0.0867136 mm (+0.03%). Clock 8657 s on 8 ranks
  (pre-fix on xenosim 3398 s); not a timing row, as the node is shared with
  the 4x.
- **FSI3 QM-AMI 4x: done** (27.5 h, driver PASS). Analysis: `4a_findings.md`.
- **3dTube QM L3: failed at start-up** (`directMap`: "interfaces are not
  conformal", 5120 unmatched faces; `fix/mfix-tube-L3.failure.txt`). Cause:
  the tutorial blockMeshDicts give the curved wall with 4-digit arc points,
  the fluid as two 45° arcs (`0.004619 0.001913`, vertex `0.003536`), the
  solid as one 90° arc. The two walls differ by up to 1.0 µm (mean 0.67 µm).
  The `directMap` tolerance is hard-coded at 1% of the smallest edge: about
  2.5 µm on L1, 1.3 µm on L2 (passes narrowly) and 0.63 µm on L3. A
  geometry issue in the tutorial, not the solver. Philip chose the upstream fix: **solids4foam PR #625** (exact arc
  points; fluid and solid walls coincide to 2e-17 m on L1 and L3).
  3dTube runs (L3, 6b, 6c, 6e) moved to the M coordinator (R5) on 26 Oct;
  not rerun here.

## 4a — FSI3 QM-AMI, tutorial meshes (23 Oct, pre-#618, superseded)

### 1x check (Mx job 5377601, one exclusive node, 3 × 8 ranks)

Driver: `./verification/Allverify --coupling monolithicAMI --levels 1
--cores 8` (Δt 1 ms, t = 7 s, last 1 s analysed), as in the V runs.
Set-up edits: `jobs/fsi3_setup.py`; job: `jobs/fsi3_1x_check.sh`.

| Variant | div(phi,U) | vST | Purpose |
|---|---|---|---|
| A | `linearUpwind cellLimited leastSquares 1` (tutorial) | no | reproduce V QM-AMI 1x |
| B | `linearUpwind grad(U)` | no | scheme effect |
| C | `linearUpwind grad(U)` | yes | transpose effect |

V QM-AMI 1x (paper-fsi-verification `ring-monolithic`,
`paper-data/hronturek_fsi3_monolithic_tutorial_meshes.csv`; M1, 8 ranks,
831 s): `u_x` mean −2.1424 mm, `u_x` amplitude 2.0720 mm, `u_y` amplitude
28.831 mm, `u_y` frequency 5.5945 Hz, drag mean 453.97 N/m, drag amplitude
22.331 N/m, lift amplitude 221.74 N/m.

Status: **done** (job 5377601, 25 min 46 s, all three complete, no failed
Newton solve; 2–3 Newton iterations per coupled step, max 4). The driver
exits 1 only on its accuracy check (1x is below the tutorial-2x tolerances;
the V 1x row has `pass False` too). CSVs: `runs.csv`, `qois.csv`,
`4a/*.sweep.csv`, `4a/*.history.csv`; provenance in `provenance/`.

| QoI | V 1x | A | A − V | B − A | C | C − B |
|---|---:|---:|---:|---:|---:|---:|
| `u_x` mean (mm) | −2.14240 | −2.14241 | −0.0003% | 0 | −2.16908 | −1.25% (magnitude +) |
| `u_x` amplitude (mm) | 2.07201 | 2.07201 | +0.0001% | 0 | 2.10025 | +1.36% |
| `u_y` amplitude (mm) | 28.8311 | 28.8312 | +0.0002% | 0 | 29.0188 | +0.65% |
| `u_y` frequency (Hz) | 5.59447 | 5.59447 | −0.0001% | 0 | 5.60016 | +0.10% |
| drag mean (N/m) | 453.971 | 453.971 | 0.0000% | 0 | 454.232 | +0.06% |
| drag amplitude (N/m) | 22.3313 | 22.3314 | +0.0003% | 0 | 22.5997 | +1.20% |
| lift amplitude (N/m) | 221.738 | 221.739 | +0.0003% | 0 | 223.724 | +0.90% |

- **A reproduces V** to ≤ 3e-6 relative in every primary QoI (different
  machine, compiler and node: M1/Clang vs Mx/GCC).
- **B = A bit for bit.** In OpenFOAM v2512 `linearUpwind` reads a single
  word as the name of its gradient scheme and looks it up with
  `mesh.gradScheme(name)`. In `linearUpwind cellLimited leastSquares 1` that
  word is `cellLimited`, which has no entry in `gradSchemes`, so the lookup
  returns `default leastSquares` and `leastSquares 1` is never read: the
  limiter was never active. The same holds for every tutorial whose
  `fvSchemes.monolithic` has this line (3dTube, beamInCrossFlow, blob,
  cavity, foilInWind, membraneRoof, Mok, TurekHron2006; all have
  `gradSchemes default leastSquares` and no `grad(U)` entry). Existing QM
  results therefore already use the partitioned convection scheme; the
  scheme decision changes text, not numbers.
- **vST yes (C − B)**: 0.06–1.4% on the primary QoIs, moving `u_y`
  amplitude towards Featflow (error 17.6% → 17.1%) and towards IQN-ILS.
  Same Newton count (1.8068 vs 1.8046 mean over all steps).

### 4x production

Running in batch 2 (Mx 5382421).

## 6a — 3dTube QM L1–L3

L1 and L2 done; L3 failed at start-up (directMap tolerance vs tutorial arc rounding); decision pending.

## Timing jobs (4b, 6b, 6c, 4c)

Moved to the M coordinator on 26 Oct (it owns timing, with #616/#624);
`TIMING_JOBS.md` left here for it. Job list and estimates: `TIMING_JOBS.md` (≈ 34 node-hours). Not submitted;
approved by Philip 23 Oct (decisions in `TIMING_JOBS.md`); submit from
1 November on the fixed build with #616.

## Core-hours

| Project | Job | Node-hours |
|---|---|---|
| p201136 | 5377601 (4a 1x check, 1 exclusive node, 25.8 min) | 0.43 |
| p201136 | 5382214 (build, 32 cores, short QOS, 5.5 min) | 0.09 |
| p201136 | 5382225 (batch 1, 1 exclusive node, 36 min) | 0.60 |
| p201136 | 5382421 (batch 2, 1 exclusive node, 27.5 h) | 27.5 |
