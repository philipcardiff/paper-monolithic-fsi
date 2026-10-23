# Run agent C: heavy cases (WP4 FSI3, WP6 3dTube) — progress

Branch `evidence/m-runs-c`. Machine: MeluXina, account p201136. Code: the
R0 build `/project/home/p201287/philip/qm-head` (solids4foam
`v2.4-1103-g85b0c1de6`, head of `feature-petsc-snes-quasi-monolithic`).
Run directories: `/project/home/p201136/philip-agentC/runs/`.

## Decisions in force (23 Oct 2026)

- QM run copies use the partitioned fluid schemes: no `cellLimited`,
  `div(phi,U) Gauss linearUpwind grad(U)`, `gradSchemes default
  leastSquares`, `ddt(U) backward` (Philip, via the coordinator).
- `viscousStressTranspose` (decided 23 Oct): the option is removed and the
  corrected wall treatment of the transpose term is hard-coded (agent A).
  FSI3 4x and 3dTube L3 wait for the fixed build; then the 1x check is
  rerun on it first.

## 4a — FSI3 QM-AMI, tutorial meshes

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

Registry row claimed (M run agent). Waiting for the fixed build.

## 6a — 3dTube QM L3

Registry row claimed (M run agent). Waiting for the fixed build.

## Timing jobs (4b, 6b, 6c, 4c)

Job list and estimates: `TIMING_JOBS.md` (≈ 34 node-hours). Not submitted;
approved by Philip 23 Oct (decisions in `TIMING_JOBS.md`); submit from
1 November on the fixed build with #616.

## Core-hours

| Project | Job | Node-hours |
|---|---|---|
| p201136 | 5377601 (4a 1x check, 1 exclusive node, 25.8 min) | 0.43 |
