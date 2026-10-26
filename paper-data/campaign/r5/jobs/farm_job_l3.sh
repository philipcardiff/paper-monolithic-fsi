#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
# 3dTube QM L3 (exact arcs) on build qm-496be (496be0c43); one 64-rank task,
# ranks pinned one per core by run_task.sh/bindwrap.sh
export QM_ROOT=/project/home/p201287/philip/qm-496be
export QM_SCRIPTS=/project/home/p201287/philip/qm-final/runs/r4r5-scripts
echo "farm $SLURM_JOB_ID on $(hostname) $(date)"
/usr/bin/python3.12 $QM_SCRIPTS/scripts/farm.py $QM_ROOT/runs/farm-l3/tasks.txt \
    --state $QM_ROOT/runs/farm-l3/farm_state.$SLURM_JOB_ID.json --poll 30
echo "farm done $(date)"
