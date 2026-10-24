#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=44:00:00
#SBATCH --job-name=agentC-fix-b2
#SBATCH --output=/project/home/p201136/philip-agentC/runs/fix/slurm-%x-%j.out
#
# Agent C on the #618 build (solids4foam 1252bd2e5 = 4ae081609 + #617
# tutorials), batch 2, on one exclusive node, 32 ranks per run:
#   fsi3-4x   TurekHron2006 FSI3 QM-AMI tutorial 4x, full run to t = 7 s (4a)
#   tube-L3   3dTube QM L3, full 20 ms (6a; fields every 2.5 ms, incl. the
#             5 ms restart state for the 6b/6c timing windows)
#   tube-L2   3dTube QM L2, 8 ranks (6a rerun: batch 1 hit the file quota at 5 ms)
ROOT=/project/home/p201136/philip-agentC
BUILD=$ROOT/build-4ae0816
source "$BUILD/env.sh"
set -u
RUNS=$ROOT/runs/fix
T=$BUILD/solids4foam/tutorials/fluidSolidInteraction
export PATH="/project/home/p201287/philip/qm-head/campaign/pybin:$PATH"   # python3.12
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1
code=$(git -C "$BUILD/solids4foam" describe --always --tags --dirty)
mkdir -p "$RUNS"

run_one()
{
    local key="$1" cores="$2" ranks="$3"; shift 3
    local id="mfix-$key" d src flag="" wi=""
    d="$RUNS/$id"
    case "$key" in
        fsi3-*) src=$T/TurekHron2006 ;;
        tube-L1) src=$T/3dTube; flag=--tube-write-env; wi=1e-3 ;;
        tube-*) src=$T/3dTube; flag=--tube-write-env; wi=2.5e-3 ;;
    esac
    python3 "$ROOT/scripts/setup_copy.py" "$src" "$d" $flag \
        > "$RUNS/$id.setup.log" 2>&1 || { echo "$id setup failed"; return 1; }
    cd "$d" || return 1
    local cmd=("$@")
    local t0 t1 rc
    t0=$(date +%s.%N)
    AGENTC_WRITE_INTERVAL="$wi" taskset -c "$cores" "${cmd[@]}" > log.Allverify.top 2>&1
    rc=$?
    t1=$(date +%s.%N)
    local sc
    sc=$(ls -d "$d"/verification/work/*/ 2>/dev/null | head -n 1); sc="${sc%/}"
    python3 /project/home/p201287/philip/qm-head/campaign/scripts/provenance.py \
        "${sc:-$d}" --ranks "$ranks" --run-id "$id" --s4f "$BUILD/solids4foam" \
        --out "$d/provenance.json" > /dev/null 2>&1
    cat > "$d/run_meta.json" <<JSON
{"run_id": "$id", "ranks": $ranks, "cores": "$cores",
 "command": "${cmd[*]}", "write_interval_env": "$wi",
 "solver_case": "${sc:-}", "code_commit": "$code",
 "node": "$(hostname)", "slurm_job_id": "$SLURM_JOB_ID", "account": "p201136",
 "exclusive_node": true, "shared_with_other_runs": true,
 "binding": "taskset -c $cores; MPI binding none",
 "rc": $rc, "wall_s": $(python3 -c "print(round($t1 - $t0, 3))")}
JSON
    echo "$id rc=$rc wall=$(python3 -c "print(round($t1 - $t0))") s"
}

echo "agent C batch 2 on $(hostname), job $SLURM_JOB_ID, code $code, $(date)"
run_one fsi3-4x 0-31 32 ./verification/Allverify --coupling monolithicAMI \
    --levels 4 --cores 32 > "$RUNS/slot-fsi3-4x.log" 2>&1 &
run_one tube-L3 64-95 32 ./verification/Allverify --coupling monolithic \
    --levels 3 --cores 32 --time-scheme backward --solid-preconditioner hypre \
    > "$RUNS/slot-tube-L3.log" 2>&1 &
run_one tube-L2 104-111 8 ./verification/Allverify --coupling monolithic \
    --levels 2 --cores 8 --time-scheme backward --solid-preconditioner hypre \
    > "$RUNS/slot-tube-L2.log" 2>&1 &
wait
cat "$RUNS"/slot-fsi3-4x.log "$RUNS"/slot-tube-L3.log "$RUNS"/slot-tube-L2.log
echo "done $(date)"
