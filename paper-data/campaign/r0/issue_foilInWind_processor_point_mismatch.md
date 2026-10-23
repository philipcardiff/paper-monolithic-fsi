# Suspected defect: foilInWind (monolithic, 128 ranks) aborts on a processor-patch face mismatch after mesh motion

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
