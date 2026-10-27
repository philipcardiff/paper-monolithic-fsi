#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=00:30:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# Set-up check for the timing job (not a timing row): ring QM strong m2 n25
# with and without the taskset mask and the single-thread BLAS/OpenMP
# variables, at the same time on one exclusive node, to find where the solver
# clock time exceeds its CPU time.
BUILD=/project/home/p201136/philip-ma/rfix
QM_ROOT=/project/home/p201287/philip/qm-head
source "$BUILD/env.sh"
export PATH="$QM_ROOT/campaign/pybin:$PATH"
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1 PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe
B=/dev/shm/probe-$SLURM_JOB_ID
OUT=/project/home/p201136/philip-ma/runs-timing-probe
ID=tm-ram-qm-strong-m2-n25-r1
run() {   # tag pin(yes|no) blas1(yes|no)
    (
        [ "$3" = yes ] && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
        if [ "$2" = yes ]; then a=(--pin "$4" --slot-width 8); else a=(--cores 1); fi
        python3 "$QM_ROOT/campaign/ma/ma_run.py" --s4f "$BUILD/solids4foam" \
            --runs "$B/$1" --provenance "$QM_ROOT/campaign/scripts/provenance.py" \
            --batch 8 --only $ID "${a[@]}" > "$B/$1.log" 2>&1
    ) &
}
mkdir -p "$B" "$OUT"
run A-nopin-blasdef no no
run B-nopin-blas1 no yes
run C-pin-blasdef yes no 64
run D-pin-blas1 yes yes 96
wait
for t in A-nopin-blasdef B-nopin-blas1 C-pin-blasdef D-pin-blas1; do
    echo "$t $(grep ExecutionTime $B/$t/$ID/log.solids4Foam | sed -n '1p;$p' | tr '\n' ' ')"
    echo "   threads seen: $(grep -c . /dev/null)"
done
rsync -a "$B/" "$OUT/"
