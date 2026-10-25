#!/bin/bash
# Copy the small per-run records (qm_run.json, run_meta.json, qm_result.json,
# provenance.json) and the farm state files from MeluXina into
# paper-data/campaign/<stream>/records/.
# Usage: fetch_records.sh r4|r5
set -eu
ST=${1:?}
HERE=$(cd "$(dirname "$0")/../.." && pwd)
DST=$HERE/$ST/records
mkdir -p "$DST"
R=/project/home/p201287/philip/qm-final/runs
rsync -a --prune-empty-dirs --exclude='processor*/' --exclude='[0-9]*/' \
    --exclude='constant/' --exclude='system/' --exclude='postProcessing/' \
    --include='*/' --include='qm_run.json' --include='run_meta.json' \
    --include='qm_result.json' --include='provenance.json' --exclude='*' \
    "meluxina:$R/$ST/" "$DST/"
mkdir -p "$DST/farms"
rsync -a --include='farm*/' --include='farm*/tasks.txt' \
    --include='farm*/farm_state.*.json' --include='farm*/slurm-*.out' \
    --exclude='*' "meluxina:$R/" "$DST/farms/"
echo "records in $DST"
