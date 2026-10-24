#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=06:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
# PR #618 bcf29f8d3 on Linux/GCC: TGV (CI case), FSI3 conformal 1x serial vs
# 4 ranks, then (alone on the node) a 3dTube L2 cost run.
B=/project/home/p201136/philip-ma/timing
P=/project/home/p201136/philip-ma/mxpatches
R=/project/home/p201136/philip-ma/runs/bcf
mkdir -p "$R"
export OMPI_MCA_hwloc_base_binding_policy=none PRTE_MCA_hwloc_default_binding_policy=none OMPI_MCA_rmaps_base_oversubscribe=1
(
  source "$B/cache/env.sh"
  cd "$B/cache/solids4foam" && git apply "$P"/0001-newtonIcoFluid-cache-sets-*.patch && echo "applied: $(git describe --always --dirty)"
  cd src/solids4FoamModels && wmake -j 32 libso > "$B/cache/log.build.bcf" 2>&1; echo "build rc=$? errors=$(grep -c ' error' $B/cache/log.build.bcf)"
) || exit 1
run() { # id cores cmd
  local id=$1 cores=$2; shift 2
  ( source "$B/cache/env.sh"; export PATH="/project/home/p201287/philip/qm-head/campaign/pybin:$PATH"
    d=$R/$id; rm -rf "${d:?}"; cp -a "$B/cache/solids4foam/tutorials/$TUT" "$d"; cd "$d" || exit 1
    t0=$(date +%s); taskset -c "$cores" "$@" > log.run 2>&1; echo "$id rc=$? wall=$(( $(date +%s) - t0 ))" > run_info.txt ) &
}
TUT=fluids/decayingTaylorGreenVortex run tgv 0 ./Allrun
TUT=fluidSolidInteraction/TurekHron2006 run fsi3c-np1 1 ./verification/Allverify --coupling monolithic --levels 1 --cores 1
TUT=fluidSolidInteraction/TurekHron2006 run fsi3c-np4 2-5 ./verification/Allverify --coupling monolithic --levels 1 --cores 4
wait
cat "$R"/*/run_info.txt
( source "$B/cache/env.sh"; export PATH="/project/home/p201287/philip/qm-head/campaign/pybin:$PATH"
  taskset -c 0-7 python3 /project/home/p201287/philip/qm-head/campaign/ma/ma_cost.py /project/home/p201136/philip-ma/runs/cost/L2-bcf-r1 --s4f "$B/head/solids4foam" --level 2 --steps 20 --cores 8 ) | tail -1
