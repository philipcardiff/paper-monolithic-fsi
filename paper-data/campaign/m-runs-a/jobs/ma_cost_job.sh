#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=08:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# PR #618 cost: 3dTube L2, 8 ranks, 20 steps, head vs PR vs PR + caching
# (timing builds), run one after another on one exclusive node, two rounds
# interleaved. All use the same tutorial and driver (the head tree), so
# only the library differs.
B=/project/home/p201136/philip-ma/timing
R=/project/home/p201136/philip-ma/runs/cost
PY=/project/home/p201287/philip/qm-head/campaign/pybin
SCRIPT=/project/home/p201287/philip/qm-head/campaign/ma/ma_cost.py
mkdir -p "$R"
export OMPI_MCA_hwloc_base_binding_policy=none PRTE_MCA_hwloc_default_binding_policy=none
for round in 1 2; do
    for n in head pr cache; do
        (
            source "$B/$n/env.sh"
            export PATH="$PY:$PATH"
            taskset -c 0-7 python3 "$SCRIPT" "$R/L2-$n-r$round" \
                --s4f "$B/head/solids4foam" --level 2 --steps 20 --cores 8
        ) > "$R/L2-$n-r$round.out" 2>&1
        echo "$n r$round: $(tail -1 $R/L2-$n-r$round.out)"
    done
done
