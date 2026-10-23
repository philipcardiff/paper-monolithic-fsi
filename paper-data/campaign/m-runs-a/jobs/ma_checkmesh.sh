#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=test
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# 2c: checkMesh on the final (t = 300 s) fluid and solid meshes of the
# cavity QM runs, and on the undeformed meshes (-constant) for comparison.
source /project/home/p201287/philip/qm-head/env.sh
cd /project/home/p201136/philip-ma/runs || exit 1
for d in ma-cav-qm-L1 ma-cav-qm-L2 ma-cav-qm-L3 ma-cav-qm-L4 \
         ma-cav-qm-L2-interplinear ma-cav-qm-L3-interplinear
do
    for region in fluid solid
    do
        (cd "$d" && checkMesh -region "$region" -latestTime \
            > "log.checkMesh.$region.final" 2>&1
         checkMesh -region "$region" -constant \
            > "log.checkMesh.$region.constant" 2>&1)
    done
    echo "$d done"
done
