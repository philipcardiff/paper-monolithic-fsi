#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=08:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# Timing rows 1d (ring strong m2 n25/50/100: QM, IQN-ILS, RN) and 2a (cavity
# L1-L4: QM, Aitken), 3 repeats each (ma_run.py batch 8), on one exclusive
# node. Every arm uses the same build (R-fix, 1252bd2e5). At most 8 runs at
# once, each pinned (taskset) to its own core complex: first cores 0, 16,
# ..., 112 (every other CCD, four per socket); the 4-rank L4 runs use the
# four cores of their complex. Timings: solver ClockTime of log.solids4Foam.
# MA_SMOKE=1: a short check of the set-up on a shared node (not a timing
# row): four cheap runs, slots on the cores Slurm gives the job.
BUILD=/project/home/p201136/philip-ma/rfix
QM_ROOT=/project/home/p201287/philip/qm-head
source "$BUILD/env.sh"
export PATH="$QM_ROOT/campaign/pybin:$PATH"
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1 PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
echo "timing on $(hostname), job $SLURM_JOB_ID, $(date)"
(cd "$BUILD/solids4foam" && git describe --always --dirty --tags)
lscpu | grep -E "^(Model name|Socket|Core|Thread|NUMA node[0-9]|L3)"
echo "allowed cpus: $(taskset -pc $$ | sed 's/.*: //')"
if [ "${MA_SMOKE:-0}" = 1 ]; then
    RUNS=/project/home/p201136/philip-ma/runs-timing-smoke
    cpus=$(python3 -c "import os; print(','.join(map(str, sorted(os.sched_getaffinity(0)))))")
    PIN=$(echo "$cpus" | cut -d, -f1,5)
    ONLY=tm-ram-qm-strong-m2-n25-r1,tm-ram-iqn-strong-m2-n25-r1,tm-cav-aitken-L1-r1,tm-cav-qm-L1-r1
else
    RUNS=/project/home/p201136/philip-ma/runs-timing
    PIN=0,16,32,48,64,80,96,112
    ONLY=${MA_ONLY:-}
fi
echo "runs $RUNS, slots $PIN"
python3 "$QM_ROOT/campaign/ma/ma_run.py" --s4f "$BUILD/solids4foam" \
    --runs "$RUNS" --provenance "$QM_ROOT/campaign/scripts/provenance.py" \
    --batch 8 --pin "$PIN" --slot-width 4 ${ONLY:+--only "$ONLY"}
echo "timing done $(date)"
