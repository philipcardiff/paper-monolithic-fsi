#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --time=24:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# FSI3 conformal 1x QM on the vST fix build, set up exactly as the R0 run
# r0-fsi3-backward-a (r0_setup.py fsi3, Allverify --coupling monolithic
# --levels 1 --cores 4), for the before/after comparison.
QM_ROOT=/project/home/p201287/philip/qm-head
BUILD=/project/home/p201136/philip-ma/qm-fix
source "$BUILD/env.sh"
export PATH="$QM_ROOT/campaign/pybin:$PATH"
export OMPI_MCA_hwloc_base_binding_policy=none PRTE_MCA_hwloc_default_binding_policy=none
RID="${FSI3_ID:-mafix-fsi3-1x}"
D=/project/home/p201136/philip-ma/runs/$RID
python3 "$QM_ROOT/campaign/scripts/r0_setup.py" fsi3 "$D" --ranks 4 --ddt-u backward > "$D.setup.log" 2>&1 || exit 1
cd "$D" || exit 1
# r0_setup.py copies the tutorial of $WM_PROJECT_USER_DIR/solids4foam (the
# fix tree). FSI3_SKEW=1 restores the former skewCorrected interpolation of
# U (for the code-only comparison with R0); FSI3_LINEAR=1 forces linear
if [ "${FSI3_SKEW:-0}" = 1 ]; then
    perl -pi -e 's/^(\s*interpolate\(U\)\s+)linear;/${1}skewCorrected linear;/' system/fluid/fvSchemes.monolithic
    grep "interpolate(U)" system/fluid/fvSchemes.monolithic
fi
if [ "${FSI3_LINEAR:-0}" = 1 ]; then
    perl -pi -e 's/^(\s*interpolate\(U\)\s+)skewCorrected linear;/${1}linear;/' system/fluid/fvSchemes.monolithic
    grep "interpolate(U)" system/fluid/fvSchemes.monolithic
fi
mkdir -p bin; export FOAM_USER_APPBIN_SAVE="$FOAM_USER_APPBIN"
(cd "$BUILD/solids4foam" && git describe --always --dirty)
t0=$(date +%s)
./verification/Allverify --coupling monolithic --levels 1 --cores 4 > log.Allrun 2>&1
echo "rc=$? wall=$(( $(date +%s) - t0 )) s"
sc=$(ls -d "$D"/verification/work/*/ | head -n 1)
python3 "$QM_ROOT/campaign/scripts/provenance.py" "${sc%/}" --ranks 4 --run-id "$RID" --s4f "$BUILD/solids4foam" --out "$D/provenance.json" > /dev/null 2>&1
