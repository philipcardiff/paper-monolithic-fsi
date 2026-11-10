# Hron-Turek FSI3 (Section 7.1): provenance

Runs: MeluXina `/project/home/p201136/philip-ht/fsi3g/runs/{qm,iqn}_{1,2,3}`
and the level-2 checks `qm_2_dt1e-4`, `qm_2_dt2e-4` and `qm_2_sf2`, built with
solids4foam `a421f063d` (`qm-a421`), cases from `mk_fsi3_case.py` (gmsh
tip-refined meshes t1-t3, AMI interface, BDF2 in both regions).

- `steps.sh`: run on MeluXina, writes `steps.txt` (per step: elapsed
  increment, Newton and Krylov iterations, IQN-ILS coupling iterations).
- `qoi.py`: benchmark statistics with the TurekHron2006 verification
  driver's `periodic_statistics` over the closing window; writes `qoi.csv`.
- `cost.py`: cost and iterations over a window from `steps.txt`.
- `build_csv.py`: writes `../fsi3_runs.csv`, read by
  `figures/scripts/fsi3_work_precision.py`.

The costs are from the production runs, which shared one exclusive
128-core node per level side by side; they are indicative and do not follow
the timing protocol of Section 4.
