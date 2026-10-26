#!/bin/bash
# 3dTube QM L3 (exact wall arcs), consistency settings t6 (as r5-tube-mono-L1/L2-t6).
# Set Q to the build to use (merged build when Philip gives the go).
Q=${Q:?build root, e.g. /project/home/p201287/philip/qm-<commit>}
S=/project/home/p201287/philip/qm-final/runs/r4r5-scripts/scripts
mkdir -p $Q/runs/r5 $Q/runs/farm-l3
cd $Q/runs/r5
QM_S4F=$Q/solids4foam /usr/bin/python3.12 $S/qm_setup.py tube r5-tube-mono-L3-t6 \
    --coupling mono --level 3 --ranks 64 --write-interval 0.02 \
    --tol snes_rtol=1e-6,snes_stol=1e-6,ksp_rtol=1e-4 --exact-arcs
echo "r5-tube-mono-L3-t6 64 - bash $S/run_task.sh $Q/runs/r5/r5-tube-mono-L3-t6" > $Q/runs/farm-l3/tasks.txt
# then: edit QM_ROOT in farm_job_l3.sh to $Q, copy it to $Q/runs/farm-l3/ and
#   sbatch --time=40:00:00 -J qm-l3 -o $Q/runs/farm-l3/slurm-%x-%j.out farm_job_l3.sh
