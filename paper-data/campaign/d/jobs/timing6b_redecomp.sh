#!/bin/bash -l
# Usage: redecomp.sh SRC T0 DEST N END
# Restart copy of SRC at T0 (qm_setup.py restart, which keeps the source rank
# count), then reconstruct T0 and re-decompose it to N ranks (QM:
# decomposeParMonolithic; RN: decomposePar per region), for the 6b
# strong-scaling windows. N = 1 runs serial from the reconstructed state.
set -e
SRC=$1; T0=$2; DEST=$3; N=$4; END=$5
QM_ROOT=${QM_ROOT:-/project/home/p201287/philip/qm-a421}
S=${QM_SCRIPTS:-/project/home/p201287/philip/qm-final/runs/r4r5-scripts}/scripts
set +e; source $QM_ROOT/env.sh > /dev/null 2>&1; set -e
/usr/bin/python3.12 $S/qm_setup.py restart --from $T0 --end $END --write-final-only $SRC $DEST > /dev/null
cd $DEST
for r in fluid solid; do reconstructPar -region $r -time $T0 > log.reconstructPar.$r 2>&1; done
rm -rf processor*
for f in system/decomposeParDict system/fluid/decomposeParDict system/solid/decomposeParDict; do
  [ -f $f ] && sed -i "s/^numberOfSubdomains .*/numberOfSubdomains $N;/" $f
done
dec=$(/usr/bin/python3.12 -c "import json;print(json.load(open(\"qm_run.json\"))[\"decompose\"])")
if [ "$N" -gt 1 ]; then
  if [ "$dec" = monolithic ]; then decomposeParMonolithic -force > log.decomposeParMonolithic 2>&1
  else for r in fluid solid; do decomposePar -force -region $r > log.decomposePar.$r 2>&1; done; fi
fi
/usr/bin/python3.12 - $N <<PY
import json,sys
d=json.load(open("qm_run.json")); d["ranks"]=int(sys.argv[1]); d["prepare"]=False
d["edits"]=d.get("edits",[])+["reconstructed at t0 and re-decomposed to %s ranks"%sys.argv[1]]
json.dump(d,open("qm_run.json","w"),indent=1)
PY
echo "$DEST ready ($N ranks)"
