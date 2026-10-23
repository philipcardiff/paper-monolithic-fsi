#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# Run agent A: serial correctness runs packed onto one node (task farm),
# at most MA_CORES at once. Required: MA_CORES; optional: MA_ONLY (run ids).
# Submit with --ntasks-per-node/--cpus-per-task matching MA_CORES (and
# --exclusive for a full node).

QM_ROOT=/project/home/p201287/philip/qm-head
source "$QM_ROOT/env.sh"
export PATH="$QM_ROOT/campaign/pybin:$PATH"   # python3.12 (drivers need >= 3.9)
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
# Run directories on p201136 storage (p201287 is close to its file quota)
RUNS="${MA_RUNS:-/project/home/p201136/philip-ma/runs}"
mkdir -p "$RUNS"
echo "agent A farm on $(hostname), job $SLURM_JOB_ID, $(date)"
(cd "$QM_ROOT/solids4foam" && git describe --always --dirty && git describe --tags)
python3 "$QM_ROOT/campaign/ma/ma_run.py" --s4f "$QM_ROOT/solids4foam" \
    --runs "$RUNS" --provenance "$QM_ROOT/campaign/scripts/provenance.py" \
    --cores "${MA_CORES:?}" ${MA_ONLY:+--only "$MA_ONLY"}
echo "agent A farm done $(date)"
