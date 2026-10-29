#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
# Timing row 6c (Table 8.2): 3dTube QM L2, 16 ranks, 50-step window from the
# t = 5 ms state of prefix5ms/p5-tube-mono-L2, one setting changed per variant
# relative to the base (the accuracy-run settings: snes_rtol = snes_stol 1e-6,
# ksp_rtol 1e-4, Schur full, lag as tutorial, BoomerAMG solid, snes_mf_operator).
# Runs are sequential on an exclusive node (one timing run at a time), ranks
# pinned to cores 0-15; 3 repeats, repeat loop outermost. Build a421f063d.
export QM_ROOT=/project/home/p201287/philip/qm-a421
export QM_SCRIPTS=/project/home/p201287/philip/qm-final/runs/r4r5-scripts
S=$QM_SCRIPTS/scripts; D=$QM_ROOT/runs/timing-6c
SRC=$QM_ROOT/runs/prefix5ms/p5-tube-mono-L2
END=0.005625
echo "6c $SLURM_JOB_ID on $(hostname) $(date)"
( source $QM_ROOT/env.sh > /dev/null 2>&1; env | sort > $D/env.txt; which mpirun > $D/which_mpirun.txt 2>&1 )
export FARM_CORES=$(seq -s, 0 15)
for rep in 1 2 3; do
  for v in base schur-upper lag1 ksp1e-3 solid-S0 vel-amg assembled; do
    R=$D/6c-$v-r$rep
    case $v in
      base) opt="" ;;
      ksp1e-3) opt="--tol ksp_rtol=1e-3" ;;
      *) opt="--pc $v" ;;
    esac
    [ -d $R ] || /usr/bin/python3.12 $S/qm_setup.py restart --from 0.005 --end $END --write-final-only $opt $SRC $R || { echo "setup $R failed"; exit 1; }
    echo "run $R $(date)"
    bash $S/run_task.sh $R; echo "rc $? $R"
  done
done
echo "6c done $(date)"
