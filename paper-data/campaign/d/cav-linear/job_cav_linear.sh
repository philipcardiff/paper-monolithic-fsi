#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=05:00:00
#SBATCH --output=/project/home/p201287/philip/qm-a421/runs/cav-linear/slurm-%j.out
# Cavity QM interpolate(U) linear, L2-L4, a421f063d (paper sectionConsistency todo).
BUILD=/project/home/p201287/philip/qm-a421
QM_ROOT=/project/home/p201287/philip/qm-head
source "$BUILD/env.sh"
export PATH="$QM_ROOT/campaign/pybin:$PATH"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export OMPI_MCA_rmaps_base_oversubscribe=1 PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe
D=$BUILD/runs/cav-linear
python3 $D/cav_linear.py --s4f "$BUILD/solids4foam" --runs "$D/runs" \
    --provenance "$QM_ROOT/campaign/scripts/provenance.py" --cores 16 ${ONLY:+--only $ONLY}
echo "done $(date)"
