#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=04:00:00
#SBATCH --job-name=agentC-fix-b1
#SBATCH --output=/project/home/p201136/philip-agentC/runs/fix/slurm-%x-%j.out
#
# Agent C on the #618 build (solids4foam 1252bd2e5 = 4ae081609 + #617
# tutorials), batch 1, farmed on one exclusive node, 8 ranks per run:
#   fsi3-1x   TurekHron2006 FSI3 QM-AMI tutorial 1x (4a check; fields
#             every 10 steps for the 4e placeholder image)
#   tube-L1   3dTube QM L1 (6a; fields every 1 ms for 6e)
#   tube-L2   3dTube QM L2 (6a; fields every 2.5 ms, incl. 5 ms restart)
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

echo "agent C batch 1 on $(hostname), job $SLURM_JOB_ID, code $code, $(date)"
run_one fsi3-1x 0-7 8 ./verification/Allverify --coupling monolithicAMI \
    --levels 1 --cores 8 --write-interval 10 > "$RUNS/slot-fsi3-1x.log" 2>&1 &
run_one tube-L1 32-39 8 ./verification/Allverify --coupling monolithic \
    --levels 1 --cores 8 --time-scheme backward --solid-preconditioner hypre \
    > "$RUNS/slot-tube-L1.log" 2>&1 &
run_one tube-L2 64-71 8 ./verification/Allverify --coupling monolithic \
    --levels 2 --cores 8 --time-scheme backward --solid-preconditioner hypre \
    > "$RUNS/slot-tube-L2.log" 2>&1 &
wait
cat "$RUNS"/slot-*.log
echo "done $(date)"
