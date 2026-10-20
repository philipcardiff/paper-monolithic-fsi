#!/bin/bash -l
# B0 smoke test and timing calibration (campaign handoff, Section 2).
#
# Runs, one after another on the allocated node:
#   ringAddedMass  ./Allrun monolithic            serial and 4 ranks
#   cavityFlexibleBottom level 1 (tutorial mesh)  serial and 4 ranks
# then, unless QM_SKIP_CALIBRATION=1, repeats ringAddedMass serial and
# cavityFlexibleBottom 4 ranks three times each for the wall-time spread.
#
# Required environment:
#   QM_ENV      file that loads OpenFOAM, PETSc and the solids4foam build
#   QM_RUNS     directory for the run cases
#   QM_SCRIPTS  campaign/scripts directory (provenance.py)

# OpenFOAM's bashrc reads unset variables, so enable -u only after it
source "${QM_ENV:?}"
set -u
mkdir -p "${QM_RUNS:?}"

# Rank placement used for every campaign run: map and bind each rank to a
# core, and print the bindings into the solver log
export OMPI_MCA_rmaps_base_mapping_policy=core
export OMPI_MCA_hwloc_base_binding_policy=core
export OMPI_MCA_hwloc_base_report_bindings=1

TUT="$WM_PROJECT_USER_DIR/solids4foam/tutorials/fluidSolidInteraction"

run_case()
{
    local id="$1" case="$2" ranks="$3"
    local d="$QM_RUNS/$id" args="monolithic"

    rm -rf "$d"
    cp -r "$TUT/$case" "$d"
    cd "$d" || return 1

    if [ "$ranks" -gt 1 ]
    then
        args="monolithic parallel"
        for f in system/decomposeParDict system/*/decomposeParDict
        do
            [ -f "$f" ] && \
                foamDictionary -entry numberOfSubdomains -set "$ranks" "$f" \
                    > /dev/null
        done
    fi

    python3 "${QM_SCRIPTS:?}/provenance.py" "$d" --ranks "$ranks" \
        --run-id "$id" > /dev/null

    local t0 t1 rc
    t0=$(date +%s.%N)
    ./Allrun $args > log.Allrun 2>&1
    rc=$?
    t1=$(date +%s.%N)

    # The fvSolution options block exists only after Allrun selected the
    # monolithic variant, so record provenance again
    python3 "$QM_SCRIPTS/provenance.py" "$d" --ranks "$ranks" \
        --run-id "$id" > /dev/null

    cat > run_meta.json <<EOF
{"run_id": "$id", "case": "$case", "ranks": $ranks, "allrun_args": "$args",
 "allrun_rc": $rc, "allrun_wall_s": $(python3 -c "print(round($t1 - $t0, 3))"),
 "binding": "mpirun map-by core bind-to core"}
EOF
    echo "$id rc=$rc wall=$(python3 -c "print(round($t1 - $t0, 3))")"
}

run_case b0-ram-s1  ringAddedMass        1
run_case b0-ram-p4  ringAddedMass        4
run_case b0-cav-s1  cavityFlexibleBottom 1
run_case b0-cav-p4  cavityFlexibleBottom 4

if [ "${QM_SKIP_CALIBRATION:-0}" != 1 ]
then
    for r in 1 2 3
    do
        run_case "b0-cal-ram-s1-r$r" ringAddedMass        1
        run_case "b0-cal-cav-p4-r$r" cavityFlexibleBottom 4
    done
fi
