# Suspected defect: foilInWind (monolithic, 128 ranks) aborts on a processor-patch face mismatch after mesh motion

**Status (25 Oct 2026): root cause found; fixed in solids4foam PR #621
(https://github.com/solids4foam/solids4foam/pull/621, branch
`fix/foilInWind-processor-point-sync`, commit `c8ef68a2d` on `a46bcbae7`),
open and not merged. See "Resolution" at the end.**

## Minimal case and commands

- solids4foam `feature-petsc-snes-quasi-monolithic` at `85b0c1de6`
  (`v2.2-1713-g85b0c1de6`), OpenFOAM v2512, PETSc 3.22.0, MeluXina.
- `tutorials/fluidSolidInteraction/foilInWind`, copied by
  `scripts/r0_setup.py foil <dir> --ranks 128`. The copy adds
  `system/controlDict.monolithic` from `b157ecaf3` (Δt = 0.0025 s, #602),
  sets `numberOfSubdomains 128` in `decomposeParDict.monolithic` (scotch,
  `decomposeParMonolithic`), and sets `writeInterval 1` and `purgeWrite 2`
  (file quota).
- Command: `./Allrun monolithic parallel` on one 128-core node (job
  5375613, run `r0-foil-backward-e`). It needs about 6 000 s to reach the
  failure.
- The fluid mesh motion is `solids4foamSolidModel` with
  `linearGeometryTotalDisplacement`.

## Expected and observed behaviour

Expected: the run continues to t = 12 s. Every coupled step up to the
failure converged, in 2–4 Newton iterations (mean 2.44, `runs.csv`).

Observed: at t = 0.9525 s, right after the mesh-motion solve (`D`, converged
in 1 iteration), two neighbouring ranks disagree on the geometry of a shared
processor face, and the run aborts. The face is near the flag, in the
refined region (`log.solids4Foam`, run directory on MeluXina
`/project/home/p201287/philip/qm-head/runs/r0/r0-foil-backward-e`, with the
OBJ dumps in `processor42/` and `processor116/`):

```
Time = 0.9525

Updating the mesh
Solving the momentum equation for D using PETSc SNES
  0 SNES Function norm 1.777354654335e-08
  1 SNES Function norm 3.923787493534e-13
  Nonlinear solve converged due to CONVERGED_FNORM_RELATIVE iterations 1
[42] --> FOAM FATAL ERROR: (openfoam-2512)
[42] face 17 area does not match neighbour by 0.00675498% -- possible face ordering problem.
patch:procBoundary42to116 my area:7.343e-07 neighbour area:7.34349e-07 matching tolerance:4.76899e-11
Mesh face:3018 vertices:4((0.0925 0.0546997 0.04) (0.0925 0.0541123 0.04) (0.09125 0.0541123 0.04) (0.09125 0.0546997 0.04))
[116] face 17 area does not match neighbour by 0.00675498% -- possible face ordering problem.
patch:procBoundary116to42 my area:7.34349e-07 neighbour area:7.343e-07 matching tolerance:4.7691e-11
Mesh face:4119 vertices:4((0.0925 0.0546998 0.04) (0.09125 0.0546998 0.04) (0.09125 0.0541123 0.04) (0.0925 0.0541123 0.04))
    From virtual void Foam::processorPolyPatch::calcGeometry(Foam::PstreamBuffers&)
```

The two copies of the face differ in one edge, y = 0.0546997 against
0.0546998. From the area difference, that is about 1e-7 m. This is of the
order of the flag displacement itself at that time (trailing-edge |u| up to
4.3e-7 m at t = 0.925 s; `qois.csv`) and far above round-off for
coordinates of 0.05 m. The ordering is consistent, so this is not a
face-ordering problem.

Earlier, in-tree runs on 2 ranks (`b157ecaf3` notes) only reached
t = 0.2 s, where the displacements are below 1e-7 m. They would not have
reached this tolerance.

## Commit

`85b0c1de6`.

## Hypothesis

The points shared by two ranks move by different amounts. The pointD (or
pointDisplacement) of the fluid mesh-motion solid model is not synchronised
across processor boundaries. Candidates:
- points on, or next to, the `flag` interface, whose displacement comes from
  the solid;
- the solid model's cell-to-point interpolation, applied per rank with no
  `syncPointList`.

The mismatch grows with the flag displacement until it exceeds the
processorPolyPatch match tolerance (1e-4 of the face size).

Discriminating checks (not run):
- the same case to t ≈ 1 s on 2–8 ranks;
- after one step, compare the pointD values that neighbouring processors
  hold for the same points.

The failure stops the foilInWind run at tutorial resolution, so R7
(foilInWind time-step limit) cannot use this run.

## Resolution (25 Oct 2026)

**Cause.** The hypothesis is confirmed, more narrowly. In
`solidModel::correctPointDisplacement`, `pointD.correctBoundaryConditions()`
applies a fixed-value point patch only on the ranks that hold faces of that
patch. The interface displacement mapped from the solid onto the fluid
mesh-motion `flag` patch is one such patch. A rank that shares a point
on the patch edge but holds no `flag` face at it keeps the value
interpolated from the cells (`enhancedVolPointInterpolation`, which is itself
synchronised). Its copy of the point therefore moves differently.
OpenFOAM's `pointConstraints::constrain` syncs these "dangling" points, but
the solid-model path did not. In the failed run, the two differing points
(0.0925, 0.0547, 0.04) and (0.09125, 0.0547, 0.04) are on the `flag` patch on
rank 42 and on no `flag` face on rank 116 (from
`processor42/116/constant/fluid/polyMesh`).

**Fix.** After the boundary conditions and the symmetry correction, every point
constrained on any rank (`fixesValue()` patch or symmetry plane) gets the
constrained value on all ranks (`pointConstraints::syncUntransformedData`).
This is a no-op in serial and where no constrained point is dangling. The
debug switch `solids4foamSolidModel` prints the largest processor-point
mismatch of the moved mesh at every step. Nothing was loosened: the
`processorPolyPatch` matching tolerance is unchanged.

**Verification** (MeluXina, v2512, PETSc 3.22.0). Each "old" run uses the
same binary with the sync switched off by a temporary environment variable.
Logs and postProcessing are on XenoSim in
`~/OpenFOAM/philipc-v2512-qmfoil/evidence/`, compared with `compare.py`
there.
- Mismatch of the moved mesh, old against fix:
  - foilInWind, 128 ranks (failing decomposition): 1.33e-8 m at step 1,
    growing to 5.0e-8 m on 27 point copies, against 0 at all 600 steps;
  - foilInWind, 16 ranks: 3.55e-9 m against 0;
  - foilInWind 8 ranks, ringAddedMass 2/8 ranks, cavityFlexibleBottom 4/8
    ranks: 0 for both, because no constrained point is dangling.
- foilInWind, 128 ranks, old code at `a46bcbae7`: it stops at t = 0.9 s
  with the same error (ranks 42/116, 35). With the fix it runs to t = 1.5 s:
  600 steps, 1200 converged SNES solves, mismatch 0 (run `foil128-fix`,
  9540 s).
- Results unchanged where no mismatch existed: foilInWind 8 ranks (10 steps)
  and 32 ranks (40 steps), ringAddedMass 2/8 ranks and cavityFlexibleBottom
  4/8 ranks (40 steps each). The QoI histories and every SNES function norm
  are bitwise identical.
- Where the old code had a mismatch, the results change:
  - foilInWind 16 ranks, to t = 0.05 s: the same Newton iteration counts;
    the displacement differs by up to 6.2e-12 m out of 7.7e-8 m;
  - foilInWind 128 ranks, up to t = 0.8975 s: the flag displacement differs
    by up to 4.0e-9 m out of 3.5e-7 m (1.1%, largest just before the
    failure), and the force by 3.6e-5 relative.
- The pre-fix r0 run (`85b0c1de6`) is not a controlled comparison for the
  QoIs, because the head has merged PRs #602, #616, #617 and #618 since.

**Consequence for the campaign.** foilInWind monolithic runs need PR #621,
or a head that contains it. A full 12 s run at 128 ranks takes about 21 h.
