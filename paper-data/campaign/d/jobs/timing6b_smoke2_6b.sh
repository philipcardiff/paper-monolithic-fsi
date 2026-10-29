#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=00:30:00
# Control: QM L1 t = 0.02 restart at the source rank count (8), plain (A) and via reconstruct + re-decompose (B), 5 steps.
export QM_ROOT=/project/home/p201287/philip/qm-a421 QM_SCRIPTS=/project/home/p201287/philip/qm-final/runs/r4r5-scripts
D=$QM_ROOT/runs/timing-6b; SRC=$QM_ROOT/runs/r5/r5-tube-mono-L1-t6; S=$QM_SCRIPTS/scripts
cpus=$(python3 -c "import os; print(\",\".join(map(str, sorted(os.sched_getaffinity(0)))))")
export FARM_CORES=$(echo $cpus | cut -d, -f1-8)
A=$D/smoke/L1-n8-plain; B=$D/smoke/L1-n8-redecomp; rm -rf $A $B
( source $QM_ROOT/env.sh >/dev/null 2>&1; /usr/bin/python3.12 $S/qm_setup.py restart --from 0.02 --end 0.020125 --write-final-only $SRC $A )
bash $D/redecomp.sh $SRC 0.02 $B 8 0.020125
for R in $A $B; do bash $S/run_task.sh $R; echo "rc $? $R"; done
