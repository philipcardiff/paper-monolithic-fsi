#!/bin/bash -l
# Prepare the B1 spin-up set-ups without running them: case variant and
# meshes (the Allrun up to "# Run solver"), for windows run from t = 0
source "${QM_ENV:?}"
for k in cav tube
do
    ( cd "${QM_RUNS:?}/spin-$k" && bash Allrun.prepare monolithic > log.prepare 2>&1 ) \
        || { echo "prepare spin-$k failed"; exit 1; }
    ls "$QM_RUNS/spin-$k/constant/fluid/polyMesh/points" "$QM_RUNS/spin-$k/constant/solid/polyMesh/points"
done
