#!/bin/bash
# Farm 1 (R4 accuracy + calibration, R5 consistency + calibration): build the
# run directories (file operations only, login node) and write tasks.txt.
# Run on MeluXina:  bash farm1_setup.sh
#
# FSI3 (conformal meshes): ranks 1x 1, 2x 4, 4x 16, the same for both
#   couplings (also the timing rank counts).
#   mono: tutorial tolerances, snes_rtol = snes_stol = 1e-6, ksp_rtol 1e-4.
#   iqn:  strict test, outerCorrTolerance 1e-6, nOuterCorr 100, fluid inner
#         tolerances 1e-8 (tutorial 1e-6) so that the inner-solver floor
#         stays below the coupling tolerance (TurekHron2006 README: at 1e-6
#         with 1e-6 inner tolerances IQN-ILS stalls about once in 5000 steps).
#   Both write every 1 s (binary): restarts at 5 s (tolerance sweep, restart
#   check) and 6 s (timing windows).
# Restart check (1x): continue from t = 5 s to 5.05 s; first-step residuals and
#   point histories compared with the continuous run.
# Tolerance sweep (2x, from the t = 5 s state of the 2x runs to 7 s, QoIs over
#   6-7 s): mono snes_rtol = snes_stol 1e-4, 1e-6, 1e-8 and the reference
#   1e-10 (ksp_rtol 1e-8, ksp_max_it 10000); iqn strict 1e-4, 1e-5, 1e-6 and
#   the reference 1e-8 (fluid inner 1e-10, solid SNES 1e-10, solid ksp_rtol
#   1e-8, nOuterCorr 200).
# 3dTube monolithic (S1 BoomerAMG solid block, backward, lag 8):
#   L3 on 64 ranks at snes_rtol = snes_stol 1e-6, ksp_rtol 1e-4 (tighter than
#   the tutorial 1e-4/1e-3, so that the long run need not wait for the L2
#   calibration; the 5% rule is an upper bound on the iterative error);
#   L2 (16 ranks) and L1 (8 ranks) at the same setting, the tutorial setting
#   and the tight reference: the full-run tolerance check on L2 (the B1
#   check covered only the early pulse).
#   Robin-Neumann L1/L2 at the same code version, for consistency.
set -eu
QM=/project/home/p201287/philip/qm-final
S=$QM/runs/r4r5-scripts/scripts
P=/usr/bin/python3.12
R4=$QM/runs/r4; R5=$QM/runs/r5
mkdir -p $R4 $R5
F=$QM/runs/farm1; mkdir -p $F
T=$F/tasks.txt
: > $T
task() { echo "$*" >> $T; }
run() { echo "bash $S/run_task.sh $1"; }
rs() {  # rs SRC DEST FROM END [options] -> command that sets up then runs
    local src=$1 dst=$2 from=$3 end=$4; shift 4
    echo "$P $S/qm_setup.py restart $src $dst --from $from --end $end $* && bash $S/run_task.sh $dst"
}

MONO6="snes_rtol=1e-6,snes_stol=1e-6,ksp_rtol=1e-4"
IQN6="ctol=1e-6,fluid_tol=1e-8,nouter=100"

# --- builds -----------------------------------------------------------------
$P $S/qm_setup.py tube $R5/r5-tube-mono-L3-t6 --coupling mono --level 3 --ranks 64 --tol $MONO6
for lv in 4 2 1; do
    n=$([ $lv = 4 ] && echo 16 || ([ $lv = 2 ] && echo 4 || echo 1))
    $P $S/qm_setup.py fsi3 $R4/r4-fsi3-mono-${lv}x --coupling mono --level $lv --ranks $n --tol $MONO6
    $P $S/qm_setup.py fsi3 $R4/r4-fsi3-iqn-${lv}x --coupling iqn --level $lv --ranks $n --tol $IQN6
done
TREF="snes_rtol=1e-10,snes_stol=1e-10,ksp_rtol=1e-8,ksp_max_it=10000"
TTUT="snes_rtol=1e-4,snes_stol=1e-4,ksp_rtol=1e-3"
for lv in 2 1; do
    n=$([ $lv = 2 ] && echo 16 || echo 8)
    $P $S/qm_setup.py tube $R5/r5-tube-mono-L$lv-tref --coupling mono --level $lv --ranks $n --tol $TREF
    $P $S/qm_setup.py tube $R5/r5-tube-mono-L$lv-t6 --coupling mono --level $lv --ranks $n --tol $MONO6
    $P $S/qm_setup.py tube $R5/r5-tube-mono-L$lv-t4 --coupling mono --level $lv --ranks $n --tol $TTUT
    $P $S/qm_setup.py tube $R5/r5-tube-robin-L$lv --coupling robin --level $lv --ranks $n
done

# --- tasks (file order = priority) -------------------------------------------
task r5-tube-mono-L3-t6 64 - $(run $R5/r5-tube-mono-L3-t6)
task r4-fsi3-mono-4x 16 - $(run $R4/r4-fsi3-mono-4x)
task r4-fsi3-iqn-4x 16 - $(run $R4/r4-fsi3-iqn-4x)
task r4-fsi3-mono-2x 4 - $(run $R4/r4-fsi3-mono-2x)
task r4-fsi3-iqn-2x 4 - $(run $R4/r4-fsi3-iqn-2x)
task r4-fsi3-mono-1x 1 - $(run $R4/r4-fsi3-mono-1x)
task r4-fsi3-iqn-1x 1 - $(run $R4/r4-fsi3-iqn-1x)
task r5-tube-mono-L2-tref 16 - $(run $R5/r5-tube-mono-L2-tref)
task r4-fsi3-mono-1x-rs5 1 r4-fsi3-mono-1x $(rs $R4/r4-fsi3-mono-1x $R4/r4-fsi3-mono-1x-rs5 5 5.05 --write-final-only)
task r4-fsi3-iqn-1x-rs5 1 r4-fsi3-iqn-1x $(rs $R4/r4-fsi3-iqn-1x $R4/r4-fsi3-iqn-1x-rs5 5 5.05 --write-final-only)
for t in 1e-4 1e-6 1e-8; do
    task r4-fsi3-mono-2x-s$t 4 r4-fsi3-mono-2x $(rs $R4/r4-fsi3-mono-2x $R4/r4-fsi3-mono-2x-s$t 5 7 --write-final-only --tol snes_rtol=$t,snes_stol=$t)
done
task r4-fsi3-mono-2x-sref 4 r4-fsi3-mono-2x $(rs $R4/r4-fsi3-mono-2x $R4/r4-fsi3-mono-2x-sref 5 7 --write-final-only --tol $TREF)
for t in 1e-4 1e-5 1e-6; do
    task r4-fsi3-iqn-2x-s$t 4 r4-fsi3-iqn-2x $(rs $R4/r4-fsi3-iqn-2x $R4/r4-fsi3-iqn-2x-s$t 5 7 --write-final-only --tol ctol=$t)
done
task r4-fsi3-iqn-2x-sref 4 r4-fsi3-iqn-2x $(rs $R4/r4-fsi3-iqn-2x $R4/r4-fsi3-iqn-2x-sref 5 7 --write-final-only --tol ctol=1e-8,fluid_tol=1e-10,solid_rtol=1e-10,solid_ksp_rtol=1e-8,nouter=200)
task r5-tube-mono-L2-t6 16 - $(run $R5/r5-tube-mono-L2-t6)
task r5-tube-mono-L2-t4 16 - $(run $R5/r5-tube-mono-L2-t4)
task r5-tube-robin-L2 16 - $(run $R5/r5-tube-robin-L2)
for x in tref t6 t4; do task r5-tube-mono-L1-$x 8 - $(run $R5/r5-tube-mono-L1-$x); done
task r5-tube-robin-L1 8 - $(run $R5/r5-tube-robin-L1)
cat $T
