#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
# Build step of ma_timing_builds.sh (the copies and commits are in place)
B=/project/home/p201136/philip-ma/timing
P=/project/home/p201136/philip-ma/mxpatches
for n in head pr cache; do
    (
        source "$B/$n/env.sh"
        cd "$B/$n/solids4foam" || exit 1
        git apply --check "$P/timing.patch" 2>/dev/null && git apply "$P/timing.patch"
        echo "$n: $(git describe --always --dirty) ($(git log --oneline -1 | cut -c1-60))"
        cd src/solids4FoamModels && wmake -j 10 libso > "$B/$n/log.build.lib" 2>&1
        echo "$n lib rc=$? errors=$(grep -c ' error' $B/$n/log.build.lib)"
    ) &
done
wait
