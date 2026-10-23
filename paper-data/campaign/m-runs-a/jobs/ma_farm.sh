#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# Run agent A: serial correctness runs packed onto one node (task farm),
# at most MA_CORES at once. Required: MA_CORES; optional: MA_ONLY (run ids),
# MA_BATCH (1 or 2), MA_RUNS (run directory root).
# Submit with --ntasks-per-node/--cpus-per-task matching MA_CORES (and
# --exclusive for a full node).

QM_ROOT=/project/home/p201287/philip/qm-head
# MA_BUILD: build root with env.sh and solids4foam (default the R0 build)
BUILD="${MA_BUILD:-$QM_ROOT}"
source "$BUILD/env.sh"
export PATH="$QM_ROOT/campaign/pybin:$PATH"   # python3.12 (drivers need >= 3.9)
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
# mpirun -np N inside a one-task allocation (cavity L4)
export OMPI_MCA_rmaps_base_oversubscribe=1 PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe
# Run directories on p201136 storage (p201287 is close to its file quota)
RUNS="${MA_RUNS:-/project/home/p201136/philip-ma/runs}"
mkdir -p "$RUNS"
echo "agent A farm on $(hostname), job $SLURM_JOB_ID, $(date)"
(cd "$BUILD/solids4foam" && git describe --always --dirty && git describe --tags)
python3 "$QM_ROOT/campaign/ma/ma_run.py" --s4f "$BUILD/solids4foam" \
    --runs "$RUNS" --provenance "$QM_ROOT/campaign/scripts/provenance.py" \
    --cores "${MA_CORES:?}" ${MA_ONLY:+--only "$MA_ONLY"} ${MA_BATCH:+--batch "$MA_BATCH"}
echo "agent A farm done $(date)"
