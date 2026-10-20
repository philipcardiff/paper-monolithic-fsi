#!/bin/bash -l
#SBATCH --account=p201287
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --time=16:00:00
#SBATCH --output=/project/home/p201287/philip/qm-paper/runs/b2/slurm-%x-%j.out
#
# B2 step 2: collapsibleChannel, quasi-monolithic Newton coupling
# (./Allrun monolithic, nonLinearGeometryTotalLagrangianVelocity solid),
# fluid level 2, rho_s/rho_f = 1, dt = 0.00625 s, t = 0 to 1.5 s.
#
# Parameterised by the solid mesh:
#   SOLID_NX, SOLID_NY  solid divisions (160 8 = conformal level-2 baseline)
#   RUN_ID              run id (directory under runs/b2)
# If SOLID_NX != 160 the driver's configure_case selects AMI, and this script
# adds conservativeTractionTransfer yes + useUndeformedArea yes.
#
# Serial on an exclusive node, for both the conformal baseline and the AMI
# run: the tutorial's Allrun has no parallel path for this case, the recorded
# README timings (2008 s) are serial, and an exclusive node removes
# memory-bandwidth contention from other jobs, so the two costs compare.
#
# Examples:
#   sbatch -J qm-b2-conf --export=ALL,SOLID_NX=160,SOLID_NY=8,RUN_ID=b2-mono-F2-S160x8-directMap b2_mono.sh
#   sbatch -J qm-b2-ami  --export=ALL,SOLID_NX=640,SOLID_NY=8,RUN_ID=b2-mono-F2-S640x8-AMI b2_mono.sh

QM_ROOT="${QM_ROOT:-/project/home/p201287/philip/qm-paper}"
# OpenFOAM's bashrc reads unset variables, so enable -u only after it
source "$QM_ROOT/env.sh"
set -u

: "${SOLID_NX:?}" "${SOLID_NY:?}" "${RUN_ID:?}"
LEVEL=2
DT=0.00625
END=1.5
RUNS="$QM_ROOT/runs/b2"
SCRIPTS="$QM_ROOT/campaign/scripts"
d="$RUNS/$RUN_ID"
mkdir -p "$RUNS"

export OMPI_MCA_rmaps_base_mapping_policy=core
export OMPI_MCA_hwloc_base_binding_policy=core
export OMPI_MCA_hwloc_base_report_bindings=1

extra=()
[ "$SOLID_NX" -ne $((80*LEVEL)) ] && extra=(--conservative)
python3 "$SCRIPTS/b2_setup.py" fsi "$d" --level $LEVEL \
    --solid "$SOLID_NX" "$SOLID_NY" --dt $DT --end $END ${extra[@]+"${extra[@]}"} \
    || exit 1
cd "$d" || exit 1

# Allrun builds setPoiseuilleFlow into $FOAM_USER_APPBIN; give each run its
# own bin directory so concurrent jobs never relink a shared executable
export FOAM_USER_APPBIN="$d/bin"
mkdir -p "$FOAM_USER_APPBIN"
export PATH="$FOAM_USER_APPBIN:$PATH"

python3 "$SCRIPTS/provenance.py" "$d" --ranks 1 --run-id "$RUN_ID" > /dev/null

# Stop the solver 15 min before the Slurm limit so that the post-run
# records are still written (rc 124 = timeout)
limit_s=$(( $(squeue -h -j "$SLURM_JOB_ID" -o %L | \
    awk -F'[-:]' '{n=NF; s=$n+60*$(n-1); if(n>2)s+=3600*$(n-2); if(n>3)s+=86400*$(n-3); print s}') - 900 ))
t0=$(date +%s.%N)
timeout "$limit_s" ./Allrun monolithic > log.Allrun 2>&1
rc=$?
t1=$(date +%s.%N)

# fvSolution's options block exists only after Allrun selected the
# monolithic variant, so record provenance again
python3 "$SCRIPTS/provenance.py" "$d" --ranks 1 --run-id "$RUN_ID" > /dev/null

cat > run_meta.json <<EOF
{"run_id": "$RUN_ID", "study": "mono", "level": $LEVEL,
 "solid_mesh": "${SOLID_NX}x${SOLID_NY}", "dt": $DT, "end_time": $END,
 "ranks": 1, "exclusive": true, "node": "$(hostname)",
 "slurm_job_id": "$SLURM_JOB_ID", "allrun_rc": $rc, "timeout_s": $limit_s,
 "allrun_wall_s": $(python3 -c "print(round($t1 - $t0, 3))")}
EOF
echo "$RUN_ID rc=$rc"
tail -n 5 log.solids4Foam
