#!/bin/bash -l
#SBATCH --job-name=qm-b2-static
#SBATCH --account=p201287
#SBATCH --partition=cpu
#SBATCH --qos=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --output=/project/home/p201287/philip/qm-paper/runs/b2/slurm-%x-%j.out
#
# B2 step 1: partitioned static wall (linear partitioned solid,
# solidProperties.linear, 20 load steps to the full external pressure),
# against the static oomph-lib beam deflection -0.143628 m, run with the
# tutorial's verification-driver procedure (run_static_case/evaluate_static)
# through campaign/scripts/b2_setup.py. Serial, as the driver runs it: the
# partitioned solid does not converge in parallel (tutorial README).
#
# Submit with: sbatch --export=ALL,QM_ROOT=/project/home/p201287/philip/qm-paper b2_static.sh

QM_ROOT="${QM_ROOT:-/project/home/p201287/philip/qm-paper}"
# OpenFOAM's bashrc reads unset variables, so enable -u only after it
source "$QM_ROOT/env.sh"
set -u

RUNS="$QM_ROOT/runs/b2"
SCRIPTS="$QM_ROOT/campaign/scripts"
mkdir -p "$RUNS"

for mesh in 320x8 640x8 1280x8 640x16
do
    nx=${mesh%x*}
    ny=${mesh#*x}
    id="b2-static-S${mesh}-linear"
    t0=$(date +%s.%N)
    python3 "$SCRIPTS/b2_setup.py" static "$RUNS" "$id" "$nx" "$ny" \
        > "$RUNS/$id.setup.log" 2>&1
    rc=$?
    t1=$(date +%s.%N)
    mkdir -p "$RUNS/$id"
    python3 "$SCRIPTS/provenance.py" "$RUNS/$id" --ranks 1 --run-id "$id" \
        > /dev/null
    cat > "$RUNS/$id/run_meta.json" <<EOF
{"run_id": "$id", "study": "static", "ranks": 1, "setup_rc": $rc,
 "allrun_wall_s": $(python3 -c "print(round($t1 - $t0, 3))")}
EOF
    echo "$id rc=$rc $(tail -n 1 "$RUNS/$id.setup.log")"
done
