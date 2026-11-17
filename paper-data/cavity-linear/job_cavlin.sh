#!/bin/bash -l
#SBATCH --account=p201287
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=06:00:00
#SBATCH --signal=B:TERM@900
#SBATCH --job-name=cavlin
#SBATCH --output=/project/home/p201136/philip-ma/cavlin/slurm-%j.out
# Cavity QM with interpolate(U) linear (the partitioned solver's continuity-flux
# interpolation), levels 1-4, 3 repeats, timed under the protocol of the
# timing-ma job 5400191 (same build a421f063d, same case definitions with only
# interpolate(U) changed): one exclusive node, at most 8 runs at once, each
# masked to its own 8-core CCD slot (first cores 0,16,...,112), runs in /dev/shm.
BUILD=/project/home/p201287/philip/qm-a421
source "$BUILD/env.sh"
export OMPI_MCA_hwloc_base_binding_policy=none PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1 PRTE_MCA_rmaps_default_mapping_policy=:oversubscribe
W=/project/home/p201136/philip-ma/cavlin
SRC=$W/src/timing-ma/runs
LOCAL=/dev/shm/cavlin-$SLURM_JOB_ID
OUT=$W/runs
mkdir -p "$LOCAL" "$OUT"
echo "job $SLURM_JOB_ID on $(hostname) $(date)"; (cd $BUILD/solids4foam && git describe --always --dirty --tags)
copy_back() { rsync -a --exclude 'processor*' "$LOCAL/" "$OUT/" && echo "copied to $OUT"; }
trap 'copy_back; exit 1' TERM
prep() { # level repeat
    local s=$SRC/tm-cav-qm-L$1-r1 d=$LOCAL/tl-cav-qmlin-L$1-r$2
    rsync -a --exclude 'processor*' --exclude 'postProcessing' --exclude 'log.*' --exclude 'ma_result.json' --exclude 'provenance.json' "$s/" "$d/"
    find "$d" -maxdepth 1 -regex '.*/[0-9.e+-]+' ! -name 0 -exec rm -rf {} +
    rm -rf "$d"/constant/*/polyMesh
    for f in "$d"/system/fluid/fvSchemes "$d"/system/fluid/fvSchemes.monolithic; do
        sed -i -E 's/^(\s*interpolate\(U\)\s+)[^;]+;/\1linear;/' "$f"
        grep -q -E '^\s*interpolate\(U\)\s+linear;' "$f" || { echo "edit failed $f"; exit 2; }
    done
}
run() { # level repeat slot
    local d=$LOCAL/tl-cav-qmlin-L$1-r$2 args="monolithic" c0=$3
    [ "$1" = 4 ] && args="monolithic parallel"
    ( cd "$d" && taskset -c $c0-$((c0+7)) ./Allrun $args > log.Allrun 2>&1; echo "L$1 r$2 rc=$? $(date)" )
}
for L in 4 3 2 1; do for r in 1 2 3; do prep $L $r; done; done
# Slots: longest first; second wave reuses the slots of the short runs.
run 4 1 0 & run 4 2 16 & run 4 3 32 &
run 3 1 48 & run 3 2 64 & run 3 3 80 &
( run 2 1 96; run 1 1 96; run 1 3 96 ) &
( run 2 2 112; run 2 3 112; run 1 2 112 ) &
wait
copy_back && rm -rf "$LOCAL"
echo "done $(date)"
