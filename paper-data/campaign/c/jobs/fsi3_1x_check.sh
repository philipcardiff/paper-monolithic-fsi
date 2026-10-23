#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=04:00:00
#SBATCH --job-name=agentC-fsi3-1x
#SBATCH --output=/project/home/p201136/philip-agentC/runs/4a/slurm-%x-%j.out
#
# Agent C, item 4a, 1x check: TurekHron2006 FSI3 QM-AMI on the tutorial 1x
# mesh through the tutorial verification driver (--coupling monolithicAMI,
# Δt 1 ms, t = 7 s, last 1 s analysed), three variants farmed onto one node,
# 8 ranks each on separate core ranges:
#   A  div(phi,U) as the tutorial (cellLimited), vST no   (V set-up)
#   B  div(phi,U) Gauss linearUpwind grad(U),     vST no
#   C  div(phi,U) Gauss linearUpwind grad(U),     vST yes
QM_ROOT=/project/home/p201287/philip/qm-head
source "$QM_ROOT/env.sh"
set -u
ROOT=/project/home/p201136/philip-agentC
RUNS=$ROOT/runs/4a
SRC=$QM_ROOT/solids4foam/tutorials/fluidSolidInteraction/TurekHron2006
export PATH="$QM_ROOT/campaign/pybin:$PATH"   # python3.12 for the driver
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1
code=$(git -C "$QM_ROOT/solids4foam" describe --always --tags --dirty)

run_one()
{
    local tag="$1" div="$2" vst="$3" cores="$4" ranks=8
    local id="m4a-fsi3-qmami-1x-$tag" d
    d="$RUNS/$id"
    python3 "$ROOT/scripts/fsi3_setup.py" "$SRC" "$d" --div "$div" --vst "$vst" \
        > "$RUNS/$id.setup.log" 2>&1 || { echo "$id setup failed"; return 1; }
    cd "$d" || return 1
    local cmd=(./verification/Allverify --coupling monolithicAMI --levels 1
               --cores "$ranks")
    local t0 t1 rc
    t0=$(date +%s.%N)
    taskset -c "$cores" timeout 13800 "${cmd[@]}" > log.Allverify.top 2>&1
    rc=$?
    t1=$(date +%s.%N)
    local sc
    sc=$(ls -d "$d"/verification/work/*/ 2>/dev/null | head -n 1); sc="${sc%/}"
    python3 "$QM_ROOT/campaign/scripts/provenance.py" "${sc:-$d}" --ranks "$ranks" \
        --run-id "$id" --out "$d/provenance.json" > /dev/null 2>&1
    cat > "$d/run_meta.json" <<JSON
{"run_id": "$id", "variant": "$tag", "div_phi_U": "$div",
 "viscousStressTranspose": "$vst", "ranks": $ranks, "cores": "$cores",
 "command": "${cmd[*]}", "solver_case": "${sc:-}", "code_commit": "$code",
 "node": "$(hostname)", "slurm_job_id": "$SLURM_JOB_ID", "account": "p201136",
 "exclusive_node": true, "shared_with_other_runs": true,
 "binding": "taskset -c $cores; MPI binding none",
 "rc": $rc, "wall_s": $(python3 -c "print(round($t1 - $t0, 3))")}
JSON
    echo "$id rc=$rc wall=$(python3 -c "print(round($t1 - $t0))") s"
}

echo "agent C FSI3 1x check on $(hostname), job $SLURM_JOB_ID, code $code, $(date)"
run_one A cellLimited no  0-7   > "$RUNS/slot-A.log" 2>&1 &
run_one B aligned     no  32-39 > "$RUNS/slot-B.log" 2>&1 &
run_one C aligned     yes 64-71 > "$RUNS/slot-C.log" 2>&1 &
wait
cat "$RUNS"/slot-?.log
echo "done $(date)"
