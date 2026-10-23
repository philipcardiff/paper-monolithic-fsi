#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --time=06:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# 7a foilInWind to t = 0.2 s. Required: FOIL_COUPLING (qm|iqn), FOIL_DT;
# optional FOIL_RANKS (default 128). IQN-ILS uses 8 ranks: on 128 ranks the
# partitioned PETSc solid solve (4 608 cells) stalls at 10 000 Krylov
# iterations in the first step (job 5377782). Submit with --ntasks-per-node=NP (and --exclusive for 128).

QM_ROOT=/project/home/p201287/philip/qm-head
source "$QM_ROOT/env.sh"
export PATH="$QM_ROOT/campaign/pybin:$PATH"
export OMPI_MCA_hwloc_base_binding_policy=none
export PRTE_MCA_hwloc_default_binding_policy=none
export OMPI_MCA_rmaps_base_oversubscribe=1
RUNS=/project/home/p201136/philip-ma/runs
NP="${FOIL_RANKS:-128}"
ID="ma-foil-${FOIL_COUPLING:?}-dt${FOIL_DT:?}"
D="$RUNS/$ID"
python3 "$QM_ROOT/campaign/ma/ma_foil_setup.py" "$FOIL_COUPLING" "$D" \
    --dt "$FOIL_DT" --ranks "$NP" --qm-root "$QM_ROOT" || exit 1
cd "$D" || exit 1
mkdir -p bin
export FOAM_USER_APPBIN="$D/bin" PATH="$D/bin:$PATH"
if [ "$FOIL_COUPLING" = qm ]; then cmd=(./Allrun monolithic parallel)
else cmd=(./Allrun parallel); fi
t0=$(date +%s.%N)
"${cmd[@]}" > log.Allrun 2>&1
rc=$?
t1=$(date +%s.%N)
python3 "$QM_ROOT/campaign/scripts/provenance.py" "$D" --ranks "$NP" \
    --run-id "$ID" --out "$D/provenance.json" > /dev/null 2>&1
cat > "$D/run_meta.json" <<EOF
{"run_id": "$ID", "coupling": "$FOIL_COUPLING", "dt": $FOIL_DT,
 "ranks": $NP, "command": "${cmd[*]}", "node": "$(hostname)",
 "slurm_job_id": "$SLURM_JOB_ID", "exclusive_node": $([ "$NP" = 128 ] && echo true || echo false), "rc": $rc,
 "wall_s": $(python3 -c "print(round($t1 - $t0, 3))")}
EOF
echo "$ID rc=$rc"
