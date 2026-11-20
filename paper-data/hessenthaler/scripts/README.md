# Hessenthaler Phase I analysis scripts

These scripts turn the raw run output of the Hessenthaler Phase I cases into the files in
`paper-data/hessenthaler/`. The paper uses them for Section 6.3, Table 6 and Figure 23. The
verification paper can use them on its own runs.

## Files

- `hv_analysis.py`: for each run, computes:
  - window statistics of the tip deflection (t = 40–45, 20–25 and 5–10 s);
  - the mean deformed centreline over t = 40–45 s and its RMS, maximum and mean deviation from the MRI centreline;
  - the voxel-averaged velocity over t = 40–45 s and its mean difference from the MRI velocities, relative to 630 mm/s;
  - quasi-monolithic runs: the Newton iterations per step, counted from the solver logs;
  - partitioned runs: the coupling iterations per step, counted from `fsiResiduals.dat`.

  It writes one JSON file.
- `hv_export.py`: writes the CSV files of `paper-data/hessenthaler/` from that JSON:
  - `tip_history.csv`
  - `summary.csv`
  - `centreline.csv`
  - `profiles.csv`
- `flapCentreline`: function objects for the 65 solid points on the flap centreline. Include them in the run's `controlDict`.
- `voxelHistory.dict`: function object that samples the fluid velocity at the 4 × 4 × 12 sub-points of every MRI voxel (1.302 × 1.302 × 6 mm). Include it in the run's `controlDict`.

Other scripts used for the paper's figures:

- `figures/scripts/hessenthaler_voxel_check.py`: compares voxel-averaged with voxel-centre (pointwise) velocities, and gives the plane flow rates.
- `figures/scripts/paraview/hessenthaler_profiles.py`: pointwise and voxel-averaged v_z along the MRI lines, from a reconstructed field.
- `figures/scripts/hessenthaler_results.py`: draws the figure.

Both analysis scripts load the `hessenthalerFsi` tutorial's validation module, which also provides the MRI reference data:

`tutorials/fluidSolidInteraction/hessenthalerFsi/validation/scripts/hessenthaler_fsi_validation.py`

## Expected layout of ANALYSIS_DIR

```
ANALYSIS_DIR/
  runs/
    <RUN>/                      e.g. QM_rF0 ... QM_rF2, P_rF0 ... P_rF2
      log.solids4Foam*          quasi-monolithic only: the solver logs, for the Newton counts
      postProcessing/
        <t0>/                   one folder per restart segment (0, 10, 19.93, ...), each with
          solidPointDisplacement_flapTip.dat
          solidPointDisplacement_flapCentrelineN00.dat ... N64.dat
        voxelHistory/fluid/<t>/voxels_U.xy
        fsiResiduals.dat        partitioned only
```

How the restart segments are combined:
- Segments are read in numerical order of their start time.
- Where two segments overlap, the later one wins.
- `log.solids4Foam.1`, `.2`, … are read in order, then `log.solids4Foam`.

## Commands

The run names default to the six runs above. To analyse other runs, give their names as extra
arguments.

```
V=<solids4foam>/tutorials/fluidSolidInteraction/hessenthalerFsi/validation/scripts/hessenthaler_fsi_validation.py
python3 hv_analysis.py ANALYSIS_DIR $V ANALYSIS_DIR/hv_results.json [RUN ...]
python3 hv_export.py   ANALYSIS_DIR ANALYSIS_DIR/hv_results.json $V paper-data/hessenthaler [RUN ...]
python3 ../../../figures/scripts/hessenthaler_voxel_check.py ANALYSIS_DIR <validation/reference>/phaseI_velocity.csv [RUN ...]
```

Pointwise profiles (`profiles_pointwise.csv`) need a reconstructed fluid velocity field:

```
reconstructPar -region fluid -time T -fields '(U)'
foamToVTK -region fluid -time T -fields '(U)' -no-boundary -no-point-data
pvbatch ../../../figures/scripts/paraview/hessenthaler_profiles.py <fluid internal .vtu> out.csv
```

Then join the `vz_point` column of `out.csv` into `profiles_pointwise.csv` under the run name.

`hv_export.py` labels the timing and iteration columns as quasi-monolithic (`QM_*`) or
partitioned (`P_*`) from the run name.
