#!/bin/bash -l
#SBATCH --partition=main
#SBATCH --ntasks=16
#SBATCH --output=/home/philipc/OpenFOAM/philipc-v2512-qmhead/runs/wp3/slurm-%x-%j.out
#
# WP3 robustness maps: serial runs packed onto one exclusive node as a task
# farm (MeluXina nodes are exclusive, so one node for the whole map costs
# less than one job per run). Each run is set up by wp3_setup.py, runs on
# its own core (taskset; MPI binding off), with its own timeout, and is
# classified by wp3_post.py.
#
# Required environment: WP3_TASKS (task file: one "run_id setup-args..." per
# line, setup-args as for wp3_setup.py without the run directory),
# WP3_TIMEOUT_H (per-run limit, hours). Optional: WP3_SLOTS (default 120),
# WP3_PIN (yes|no, default yes; no on XenoSim, which has no Slurm cpusets,
# so pinning to cores 0..N-1 would stack runs on other users' processes),
# WP3_RUNS, WP3_SCRIPTS, WP3_PROVENANCE (paths; MeluXina defaults).

QM_ROOT="${QM_ROOT:-/project/home/p201287/philip/qm-head}"
export QM_ROOT
source "$QM_ROOT/env.sh"
set -u
RUNS="${WP3_RUNS:-$QM_ROOT/runs/wp3}"
SCRIPTS="${WP3_SCRIPTS:-$QM_ROOT/campaign/wp3}"
PROVENANCE="${WP3_PROVENANCE:-$QM_ROOT/campaign/scripts/provenance.py}"
PIN="${WP3_PIN:-yes}"
TASKS="${WP3_TASKS:?}"
TLIM_S=$(( ${WP3_TIMEOUT_H:?} * 3600 ))
SLOTS="${WP3_SLOTS:-120}"
mkdir -p "$RUNS"
export PATH="$QM_ROOT/campaign/pybin:$PATH"
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none

now() { date +%s.%N; }

run_one()
{
    local core="$1" id="$2"; shift 2
    local d="$RUNS/$id"
    python3 "$SCRIPTS/wp3_setup.py" "$1" "$d" "${@:2}" \
        > "$RUNS/$id.setup.log" 2>&1 || { echo "$id setup failed"; return 1; }
    cd "$d" || return 1
    # collapsibleChannel's Allrun builds a utility into FOAM_USER_APPBIN;
    # keep it inside the run directory
    mkdir -p bin
    export FOAM_USER_APPBIN="$d/bin" PATH="$d/bin:$PATH"
    local t0 t1 rc wall
    t0=$(now)
    if [ "$PIN" = yes ]
    then
        taskset -c "$core" timeout "$TLIM_S" $(cat wp3_cmd) > log.Allrun 2>&1
    else
        timeout "$TLIM_S" $(cat wp3_cmd) > log.Allrun 2>&1
    fi
    rc=$?
    t1=$(now)
    wall=$(python3 -c "print(round($t1 - $t0, 3))")
    python3 "$PROVENANCE" "$d" --ranks 1 \
        --run-id "$id" --out "$d/provenance.json" > /dev/null 2>&1
    cat > "$d/run_meta.json" <<EOF
{"run_id": "$id", "core": $core, "node": "$(hostname)",
 "slurm_job_id": "$SLURM_JOB_ID", "exclusive_node": $([ "$PIN" = yes ] && echo true || echo false),
 "shared_with_other_wp3_runs": true,
 "binding": "$([ "$PIN" = yes ] && echo "taskset -c $core" || echo "none (shared node)")",
 "rc": $rc, "timeout_s": $TLIM_S, "wall_s": $wall}
EOF
    python3 "$SCRIPTS/wp3_post.py" "$d" --rc "$rc" --wall "$wall"
}

echo "WP3 farm on $(hostname), job $SLURM_JOB_ID, $(date), tasks $TASKS"
declare -A pid_core
free=()
for ((c = 0; c < SLOTS; c++)); do free+=("$c"); done

while read -r id args
do
    [ -z "$id" ] && continue
    case "$id" in \#*) continue ;; esac
    while [ "${#free[@]}" -eq 0 ]
    do
        wait -n
        for p in "${!pid_core[@]}"
        do
            if ! kill -0 "$p" 2>/dev/null
            then
                free+=("${pid_core[$p]}")
                unset "pid_core[$p]"
            fi
        done
    done
    core="${free[0]}"
    free=("${free[@]:1}")
    # shellcheck disable=SC2086
    ( run_one "$core" "$id" $args ) > "$RUNS/$id.farm.log" 2>&1 &
    pid_core[$!]="$core"
    echo "$(date +%T) start $id on core $core"
done < "$TASKS"
wait
echo "WP3 farm done $(date)"
cat "$RUNS"/*.farm.log 2>/dev/null | grep -E " (pass|cap|newton|nan|diverged|timeout|crash) " | sort
