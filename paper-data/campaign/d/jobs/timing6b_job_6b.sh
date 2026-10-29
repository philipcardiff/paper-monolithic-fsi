#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
# Timing row 6b (Fig. 8.1): 3dTube strong scaling, 50-step windows from the
# t = 5 ms states. QM and RN; L2 at 1-64 ranks, L3 at 16-128 ranks. Each
# (case, ranks) is re-decomposed once from the reconstructed 5 ms state
# (redecomp.sh) and reused by the 3 repeats (repeat loop outermost). One run
# at a time on the exclusive node, ranks pinned to cores 0..N-1. Build
# a421f063d. The point-displacement monitor jumps at any restart of this case
# (also at the source rank count); the fluid forces are continuous.
export QM_ROOT=/project/home/p201287/philip/qm-a421
export QM_SCRIPTS=/project/home/p201287/philip/qm-final/runs/r4r5-scripts
S=$QM_SCRIPTS/scripts; D=$QM_ROOT/runs/timing-6b; P=$QM_ROOT/runs/prefix5ms
echo "6b $SLURM_JOB_ID on $(hostname) $(date)"
( source $QM_ROOT/env.sh > /dev/null 2>&1; env | sort > $D/env.txt; which mpirun > $D/which_mpirun.txt 2>&1 )
# QM L3 state: written by the running L3 production run (Mx 5399576)
L3=$QM_ROOT/runs/r5/r5-tube-mono-L3-t6
until [ -f $L3/processor63/0.005/uniform/time ]; do sleep 120; done; sleep 120
CASES="mono-L2:$P/p5-tube-mono-L2:0.005625:1,2,4,8,16,32,64
robin-L2:$P/p5-tube-robin-L2:0.005625:1,2,4,8,16,32,64
mono-L3:$L3:0.0053125:16,32,64,128
robin-L3:$P/p5-tube-robin-L3:0.0053125:16,32,64,128"
for line in $CASES; do
  IFS=: read c src end ns <<< "$line"
  for n in ${ns//,/ }; do
    B=$D/src/6b-$c-n$n
    [ -d $B ] || bash $D/redecomp.sh $src 0.005 $B $n $end || echo "redecomp $B failed"
  done
done
for rep in 1 2 3; do
  for line in $CASES; do
    IFS=: read c src end ns <<< "$line"
    for n in ${ns//,/ }; do
      B=$D/src/6b-$c-n$n; R=$D/6b-$c-n$n-r$rep
      [ -d $B ] || continue
      [ -d $R ] || ( source $QM_ROOT/env.sh > /dev/null 2>&1; /usr/bin/python3.12 $S/qm_setup.py restart --from 0.005 --end $end --write-final-only $B $R > /dev/null ) || { echo "setup $R failed"; continue; }
      export FARM_CORES=$(seq -s, 0 $((n-1)))
      echo "run $R $(date)"; bash $S/run_task.sh $R; echo "rc $? $R"
    done
  done
done
echo "6b done $(date)"
