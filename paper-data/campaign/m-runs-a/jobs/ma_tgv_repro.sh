#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=test
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --time=00:30:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
# CI failure reproduction: tutorials/fluids/decayingTaylorGreenVortex
B=/project/home/p201136/philip-ma/timing
R=/project/home/p201136/philip-ma/runs/tgv
mkdir -p "$R"
for n in pr cache; do
    (
        source "$B/$n/env.sh"
        d=$R/$n; rm -rf "${d:?}"
        cp -a "$B/$n/solids4foam/tutorials/fluids/decayingTaylorGreenVortex" "$d"
        cd "$d" && ./Allrun > log.Allrun 2>&1
        echo "$n: $(grep -c 'FOAM FATAL\|Aborted\|sigFpe\|Floating point' log.solids4Foam log.Allrun | tr '\n' ' ')"
    ) &
done
wait
