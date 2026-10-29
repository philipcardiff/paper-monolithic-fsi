#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
# 3dTube 5 ms restart states for timing rows 6b/6c (QM L2, RN L2, RN L3), build qm-a421 (a421f063d)
export QM_ROOT=/project/home/p201287/philip/qm-a421
echo "farm $SLURM_JOB_ID on $(hostname) $(date)"
for r in p5-tube-mono-L2 p5-tube-robin-L2 p5-tube-robin-L3; do ( source $QM_ROOT/env.sh > /dev/null 2>&1; env | sort > /project/home/p201287/philip/qm-a421/runs/prefix5ms/$r/env.txt; which mpirun > /project/home/p201287/philip/qm-a421/runs/prefix5ms/$r/which_mpirun.txt 2>&1 ); done
/usr/bin/python3.12 /project/home/p201287/philip/qm-final/runs/r4r5-scripts/scripts/farm.py /project/home/p201287/philip/qm-a421/runs/prefix5ms/tasks.txt --state /project/home/p201287/philip/qm-a421/runs/prefix5ms/farm_state.$SLURM_JOB_ID.json --poll 30
echo "farm done $(date)"
