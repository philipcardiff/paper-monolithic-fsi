#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --time=06:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
# Reference for the PR #618 decomposition check: FSI3 conformal 1x on the
# head build (85b0c1de6), serial vs 4 ranks, same driver as pr618 fsi3c-*
HEAD=/project/home/p201287/philip/qm-head
R=/project/home/p201136/philip-ma/runs/pr618
export OMPI_MCA_hwloc_base_binding_policy=none PRTE_MCA_hwloc_default_binding_policy=none OMPI_MCA_rmaps_base_oversubscribe=1
for spec in "fsi3c-1x-head-np1:1:0" "fsi3c-1x-head-np4:4:1-4"; do
    id=${spec%%:*}; rest=${spec#*:}; np=${rest%%:*}; cores=${rest#*:}
    (
        source "$HEAD/env.sh"; export PATH="$HEAD/campaign/pybin:$PATH"
        d=$R/$id; rm -rf "${d:?}"; cp -a "$HEAD/solids4foam/tutorials/fluidSolidInteraction/TurekHron2006" "$d"; cd "$d" || exit 1
        t0=$(date +%s); taskset -c "$cores" ./verification/Allverify --coupling monolithic --levels 1 --cores $np > log.Allverify 2>&1
        echo "$id rc=$? wall=$(( $(date +%s) - t0 ))" > run_info.txt
    ) &
done
wait
