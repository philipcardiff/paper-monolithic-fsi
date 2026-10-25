#!/bin/bash -l
# R4/R5 farm task: prepare (fresh runs), decompose, run and post-process one
# run directory built by qm_setup.py.
#
# Usage: run_task.sh RUN_DIR     (inside a farm.py task; FARM_CORES is the
#                                 comma-separated list of this task's cores)
#
# Binding: every MPI rank is pinned to one core of FARM_CORES by bindwrap.sh
# (taskset per rank; mpirun binding off, since mpirun's own binding ignores
# an inherited cpuset and starts at core 0). A serial run is pinned with
# taskset. Fields are not reconstructed (restarts use the processor
# directories; the QoIs come from the function objects of the master rank).
QM_ROOT="${QM_ROOT:-/project/home/p201287/philip/qm-final}"
SCR="${QM_SCRIPTS:-$QM_ROOT/runs/r4r5-scripts}"
# The OpenFOAM bashrc is not `set -u` clean: source it first
source "$QM_ROOT/env.sh" > /dev/null 2>&1
command -v solids4Foam > /dev/null || { echo "environment not loaded"; exit 2; }
set -u
export QM_S4F="$QM_ROOT/solids4foam" QM_CAMPAIGN="$SCR/campaign"
PY=/usr/bin/python3.12
RUN=$(readlink -f "$1")
cd "$RUN" || exit 2
CORES="${FARM_CORES:?}"
get() { $PY -c "import json,sys;d=json.load(open('qm_run.json'));print(d.get('$1',''))"; }
RANKS=$(get ranks); PREP=$(get prepare); ALLRUN=$(get allrun); DEC=$(get decompose)
ID=$(basename "$RUN")
NC=$(awk -F, '{print NF}' <<< "$CORES")
if [ "$NC" -lt "$RANKS" ]; then echo "need $RANKS cores, got $CORES"; exit 2; fi

export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1
export FARM_CORES="$CORES"
# The tutorials' Allrun builds nothing here; keep any user binaries local
export FOAM_USER_APPBIN="$RUN/bin" PATH="$RUN/bin:$PATH"

now() { date +%s.%N; }
t0=$(now)
rc=0
if [ "$PREP" = "True" ] && [ ! -f Allrun.prepare.done ]; then
    sed '/^# Run solver/,$d' Allrun > Allrun.prepare
    taskset -c "$CORES" bash Allrun.prepare $ALLRUN > log.prepare 2>&1 || rc=$?
    if [ $rc -eq 0 ] && [ "$RANKS" -gt 1 ]; then
        if [ "$DEC" = "monolithic" ]; then
            taskset -c "$CORES" decomposeParMonolithic -force > log.decomposeParMonolithic 2>&1 || rc=$?
        else
            for r in fluid solid; do
                taskset -c "$CORES" decomposePar -force -region $r > log.decomposePar.$r 2>&1 || rc=$?
            done
        fi
    fi
    [ $rc -eq 0 ] && touch Allrun.prepare.done
fi
t1=$(now)
if [ $rc -eq 0 ]; then
    if [ "$RANKS" -gt 1 ]; then
        taskset -c "$CORES" mpirun -np "$RANKS" --bind-to none \
            "$SCR/scripts/bindwrap.sh" solids4Foam -parallel > log.solids4Foam 2>&1
        rc=$?
    else
        taskset -c "${CORES%%,*}" solids4Foam > log.solids4Foam 2>&1
        rc=$?
    fi
fi
t2=$(now)
$PY "$QM_CAMPAIGN/scripts/provenance.py" "$RUN" --ranks "$RANKS" --run-id "$ID" \
    --s4f "$QM_S4F" --out "$RUN/provenance.json" > /dev/null 2>&1
cat > run_meta.json <<EOF
{"run_id": "$ID", "ranks": $RANKS, "cores": "$CORES",
 "node": "$(hostname)", "slurm_job_id": "${SLURM_JOB_ID:-}",
 "exclusive_node": true, "shared_with_own_jobs_only": true,
 "binding": "one core per rank (taskset per rank via bindwrap.sh); MPI binding none",
 "farm_task": "${FARM_TASK_ID:-}",
 "rc": $rc, "prepare_s": $($PY -c "print(round($t1 - $t0, 3))"),
 "solver_wall_s": $($PY -c "print(round($t2 - $t1, 3))")}
EOF
$PY "$SCR/scripts/qm_post.py" "$RUN" > log.qm_post 2>&1
echo "$ID rc=$rc solver_wall=$($PY -c "print(round($t2 - $t1))") s"
exit $rc
