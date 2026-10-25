#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#
# R4/R5 task farm on one exclusive 128-core MeluXina node (billing is per
# node): farm.py starts the tasks of $FARM_TASKS as cores become free, each on
# its own cores (one core per MPI rank). The node is shared by our own runs
# only. Submit with
#   sbatch --time=HH:MM:SS -J <name> -o <dir>/slurm-%x-%j.out \
#          --export=ALL,FARM_TASKS=<dir>/tasks.txt farm_job.sh
set -u
QM_ROOT=/project/home/p201287/philip/qm-final
SCR=$QM_ROOT/runs/r4r5-scripts
TASKS=$(readlink -f "${FARM_TASKS:?}")
echo "farm $SLURM_JOB_ID on $(hostname) $(date) tasks $TASKS"
/usr/bin/python3.12 "$SCR/scripts/farm.py" "$TASKS" \
    --state "$(dirname "$TASKS")/farm_state.$SLURM_JOB_ID.json" --poll 20
echo "farm done $(date)"
