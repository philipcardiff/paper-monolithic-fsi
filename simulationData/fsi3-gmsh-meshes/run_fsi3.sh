#!/bin/bash
# Usage: run_fsi3.sh <case> [END]   (env file: <case>/case.env; ENV_SH: OpenFOAM/solids4foam env)
# Mesh, decompose, rigid phase 0-2 s at DT_RIGID, then coupled to END at DT.

c=$1; cd "$c" || exit 1
source ./case.env
END=${2:-$END}
source "${ENV_SH:-$HOME/claude-runs/agent-b-gmsh/env_a421.sh}"
MPIRUN=${MPIRUN:-mpirun -np $RANKS}
run() { local log=$1; shift; "$@" > "$log" 2>&1 || { echo "$c: $* failed (see $log)"; exit 1; }; }
if [ ! -f log.blockMesh.solid ]; then
    run log.blockMesh.solid blockMesh -region solid
    run log.checkMesh.solid checkMesh -region solid -noFunctionObjects
fi
par=""
if [ "$RANKS" -gt 1 ]; then
    par=-parallel
    [ -d processor0 ] || { run log.decomposePar.fluid decomposePar -region fluid; run log.decomposePar.solid decomposePar -region solid; }
fi
latest() { if [ -n "$par" ]; then \ls -1 processor0 | grep -E '^[0-9.e+-]+$' | sort -g | tail -1; else foamListTimes -region fluid -latestTime -withZero 2>/dev/null | tail -1; fi; }
T_SWITCH=${T_SWITCH:-2}
if awk "BEGIN{exit !($(latest) < $T_SWITCH)}"; then
    WI=$(sed -n -E 's/^writeInterval +([^;]*);/\1/p' system/controlDict)
    sed -i -E "s/^deltaT .*/deltaT          $DT_RIGID;/; s/^endTime .*/endTime         $T_SWITCH;/; s/^writeInterval .*/writeInterval   $T_SWITCH;/" system/controlDict
    $MPIRUN solids4Foam $par > log.solids4Foam.rigid 2>&1 || { echo "$c: rigid phase failed"; exit 1; }
    sed -i -E "s/^writeInterval .*/writeInterval   $WI;/" system/controlDict
fi
sed -i -E "s/^deltaT .*/deltaT          $DT;/; s/^endTime .*/endTime         $END;/" system/controlDict
n=$(\ls -1 log.solids4Foam.coupled* 2>/dev/null | wc -l | tr -d ' ')
$MPIRUN solids4Foam $par > log.solids4Foam.coupled$n 2>&1 || { echo "$c: coupled phase failed"; exit 1; }
echo "$c: done to $END"
