#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=24:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# PR solids4foam#618 review checks, packed on one exclusive node, each run on
# its own core range (taskset; MPI binding off):
#  - decomposition: 3dTube L1 serial vs 8 ranks; FSI3 conformal 1x serial vs
#    4 ranks (fix build)
#  - cost: 3dTube L2 on 8 ranks, head build vs fix build, same tutorial copy
#  - FSI3 QM-AMI tutorial meshes 1x/2x, interpolate(U) skewCorrected vs linear
# Each run is a copy of the fix tree's tutorial run through its driver.

FIX=/project/home/p201136/philip-ma/qm-fix
HEAD=/project/home/p201287/philip/qm-head
PYBIN=$HEAD/campaign/pybin
R=/project/home/p201136/philip-ma/runs/pr618
mkdir -p "$R"
export OMPI_MCA_hwloc_base_binding_policy=none PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1

run() {   # id build tutorial cores scheme cmd...
    local id=$1 build=$2 tut=$3 cores=$4 scheme=$5; shift 5
    local d=$R/$id
    (
        source "$build/env.sh"
        export PATH="$PYBIN:$PATH"
        rm -rf "${d:?}"
        cp -a "$FIX/solids4foam/tutorials/fluidSolidInteraction/$tut" "$d"
        cd "$d" || exit 1
        if [ "$scheme" = skew ]; then
            perl -pi -e 's/^(\s*interpolate\(U\)\s+)linear;/${1}skewCorrected linear;/' system/fluid/fvSchemes.monolithic
        fi
        echo "$id: build $(cd $build/solids4foam && git describe --always --dirty), $(grep -h 'interpolate(U)' system/fluid/fvSchemes.monolithic | tr -s ' ')" > run_info.txt
        t0=$(date +%s)
        taskset -c "$cores" "$@" > log.Allverify 2>&1
        echo "rc=$? wall=$(( $(date +%s) - t0 ))" >> run_info.txt
    ) &
}

V=./verification/Allverify
run tube-L1-np1      $FIX  3dTube        0      lin  $V --coupling monolithic --levels 1 --cores 1
run tube-L1-np8      $FIX  3dTube        1-8    lin  $V --coupling monolithic --levels 1 --cores 8
run tube-L2-np8-head $HEAD 3dTube        9-16   lin  $V --coupling monolithic --levels 2 --cores 8
run tube-L2-np8-fix  $FIX  3dTube        17-24  lin  $V --coupling monolithic --levels 2 --cores 8
run fsi3c-1x-np1     $FIX  TurekHron2006 25     lin  $V --coupling monolithic --levels 1 --cores 1
run fsi3c-1x-np4     $FIX  TurekHron2006 26-29  lin  $V --coupling monolithic --levels 1 --cores 4
run fsi3a-1x-skew    $FIX  TurekHron2006 30-37  skew $V --coupling monolithicAMI --levels 1 --cores 8
run fsi3a-1x-lin     $FIX  TurekHron2006 38-45  lin  $V --coupling monolithicAMI --levels 1 --cores 8
run fsi3a-2x-skew    $FIX  TurekHron2006 46-61  skew $V --coupling monolithicAMI --levels 2 --cores 16
run fsi3a-2x-lin     $FIX  TurekHron2006 62-77  lin  $V --coupling monolithicAMI --levels 2 --cores 16
wait
echo "PR 618 checks done $(date)"
for f in "$R"/*/run_info.txt; do cat "$f"; done
