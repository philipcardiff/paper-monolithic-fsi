#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=24:00:00
#SBATCH --output=/project/home/p201287/philip/qm-head/runs/r0/slurm-%x-%j.out
#
# R0: every paper case once with the quasi-monolithic coupling from the
# solver branch head, at tutorial resolution, to the case's end time, packed
# onto one node as a task farm. Each case runs in the background on its own
# core range (taskset; MPI binding off so that mpirun keeps the range), with
# its own `timeout`, then `wait`.
#
# Required environment: QM_ROOT (qm-head), R0_TAG (suffix of the run ids).
# Optional: R0_CASES (space-separated keys; default all), R0_SLOTS.
#
# Slot table: key ranks cores timeout_h. A case whose fluid ddt(U) was
# switched from Euler to backward is rerun with Euler in the same slot if the
# backward run does not complete (R0 brief).

QM_ROOT="${QM_ROOT:-/project/home/p201287/philip/qm-head}"
source "$QM_ROOT/env.sh"
set -u
RUNS="$QM_ROOT/runs/r0"
SCRIPTS="$QM_ROOT/campaign/scripts"
TAG="${R0_TAG:?}"
mkdir -p "$RUNS"
# The verification drivers need Python >= 3.9; the system python3 is 3.6
mkdir -p "$QM_ROOT/campaign/pybin"
ln -sfn /usr/bin/python3.12 "$QM_ROOT/campaign/pybin/python3"
export PATH="$QM_ROOT/campaign/pybin:$PATH"

export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1

#        key   ranks cores     timeout_h
# (R0_SLOTS overrides the table, e.g. for a dedicated foilInWind job)
SLOTS="${R0_SLOTS:-foil   96    32-127    23
       fsi3   4     8-11      20
       tube   8     12-19     20
       fsi1   1     20        6
       ram    1     0         4
       wom    1     1         6
       coll   1     2         10
       cav    1     3         10
       blob   1     4         16}"
CASES="${R0_CASES:-foil fsi3 tube fsi1 ram wom coll cav blob}"

now() { date +%s.%N; }

# Peak resident memory per run directory (sum over the solver's ranks),
# sampled every 20 s from /proc
mem_sampler()
{
    while true
    do
        for pid in $(pgrep -u "$USER" -x solids4Foam)
        do
            cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null) || continue
            rss=$(awk '/^VmRSS/{print $2}' "/proc/$pid/status" 2>/dev/null)
            [ -n "$rss" ] && echo "$cwd $rss"
        done | awk -v t="$(date +%s)" '{s[$1]+=$2; n[$1]++}
            END{for (d in s) print t, d, s[d], n[d]}' >> "$RUNS/mem_samples.$SLURM_JOB_ID"
        sleep 20
    done
}

run_one()
{
    local key="$1" ranks="$2" cores="$3" tlim_h="$4" ddt="$5"
    local id="r0-$key-$ddt-$TAG" d
    d="$RUNS/$id"
    python3 "$SCRIPTS/r0_setup.py" "$key" "$d" --ranks "$ranks" \
        --ddt-u "$ddt" > "$RUNS/$id.setup.log" 2>&1 || return 1
    cd "$d" || return 1
    # Allrun builds utilities (collapsibleChannel) into FOAM_USER_APPBIN;
    # keep them inside the run directory
    mkdir -p bin
    export FOAM_USER_APPBIN="$d/bin" PATH="$d/bin:$PATH"

    local cmd
    case "$key" in
        tube) cmd=(./verification/Allverify --coupling monolithic --levels 1
                   --cores "$ranks" --time-scheme "$ddt") ;;
        fsi3) cmd=(./verification/Allverify --coupling monolithic --levels 1
                   --cores "$ranks") ;;
        fsi1) cmd=(./verification/Allverify --benchmark fsi1
                   --coupling monolithic --levels 1 --cores "$ranks") ;;
        *)    if [ "$ranks" -gt 1 ]
              then cmd=(./Allrun monolithic parallel)
              else cmd=(./Allrun monolithic)
              fi ;;
    esac
    local t0 t1 rc
    t0=$(now)
    taskset -c "$cores" timeout "$((tlim_h * 3600))" "${cmd[@]}" \
        > log.Allrun 2>&1
    rc=$?
    t1=$(now)

    # The solver case is the run directory, or the driver's copy under
    # verification/work
    local sc="$d"
    case "$key" in tube|fsi3|fsi1)
        sc=$(ls -d "$d"/verification/work/*/ 2>/dev/null | head -n 1)
        sc="${sc%/}"; [ -n "$sc" ] || sc="$d" ;;
    esac
    python3 "$SCRIPTS/provenance.py" "$sc" --ranks "$ranks" --run-id "$id" \
        --out "$d/provenance.json" > /dev/null 2>&1
    cat > "$d/run_meta.json" <<EOF
{"run_id": "$id", "key": "$key", "ranks": $ranks, "cores": "$cores",
 "ddt_U": "$ddt", "command": "${cmd[*]}", "solver_case": "$sc",
 "node": "$(hostname)", "slurm_job_id": "$SLURM_JOB_ID",
 "exclusive_node": true, "shared_with_other_r0_runs": true,
 "binding": "taskset -c $cores; MPI binding none",
 "rc": $rc, "timeout_s": $((tlim_h * 3600)),
 "wall_s": $(python3 -c "print(round($t1 - $t0, 3))")}
EOF
    echo "$id rc=$rc wall=$(python3 -c "print(round($t1 - $t0))") s"
    return $rc
}

slot()
{
    local key="$1" ranks="$2" cores="$3" tlim_h="$4"
    run_one "$key" "$ranks" "$cores" "$tlim_h" backward
    local rc=$?
    case "$key" in coll|cav|blob|tube)
        if [ "$rc" -ne 0 ] || ! python3 "$SCRIPTS/r0_post.py" --completed \
            "$RUNS/r0-$key-backward-$TAG"
        then
            echo "r0-$key-backward-$TAG did not complete: Euler rerun"
            run_one "$key" "$ranks" "$cores" "$tlim_h" Euler
        fi ;;
    esac
}

mem_sampler &
sampler=$!
echo "R0 farm on $(hostname), job $SLURM_JOB_ID, tag $TAG, $(date)"
while read -r key ranks cores tlim_h
do
    case " $CASES " in *" $key "*) ;; *) continue ;; esac
    echo "start $key: $ranks ranks on cores $cores, timeout $tlim_h h"
    slot "$key" "$ranks" "$cores" "$tlim_h" > "$RUNS/slot-$key-$TAG.log" 2>&1 &
done <<< "$SLOTS"
wait $(jobs -p | grep -v "^$sampler$")
kill "$sampler" 2>/dev/null
echo "R0 farm done $(date)"
python3 "$SCRIPTS/status.py" "$RUNS"/r0-*-"$TAG" 2>/dev/null
