#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=00:30:00
# Smoke test of redecomp.sh: QM L1 t = 0.02 state (8 ranks) -> 4 ranks and serial, 5 steps; RN not tested here.
export QM_ROOT=/project/home/p201287/philip/qm-a421 QM_SCRIPTS=/project/home/p201287/philip/qm-final/runs/r4r5-scripts
D=$QM_ROOT/runs/timing-6b; SRC=$QM_ROOT/runs/r5/r5-tube-mono-L1-t6
cpus=$(python3 -c "import os; print(\",\".join(map(str, sorted(os.sched_getaffinity(0)))))")
for n in 4 1; do
  R=$D/smoke/L1-n$n; rm -rf $R; mkdir -p $D/smoke
  bash $D/redecomp.sh $SRC 0.02 $R $n 0.020125 || { echo "redecomp n$n failed"; continue; }
  FARM_CORES=$(echo $cpus | cut -d, -f1-$n) bash $QM_SCRIPTS/scripts/run_task.sh $R; echo "rc $? n$n"
  grep -E "^Time =" $R/log.solids4Foam | tail -1; tail -3 $R/log.solids4Foam
done
