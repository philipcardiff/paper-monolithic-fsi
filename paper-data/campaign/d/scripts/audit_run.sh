#!/bin/bash
source ~/bin/load-openfoam v2512 >/dev/null 2>&1
S=$1; T=$S/tutorials/fluidSolidInteraction/TurekHron2006
for fam in tutorial conformal; do for lvl in 1 2 4; do
  d=$S/runs/$fam-$lvl; rm -rf $d; mkdir -p $d/system/fluid $d/constant/fluid
  grep -v "^#include" $T/system/controlDict > $d/system/controlDict
  \cp -f $T/system/fluid/{fvSchemes,fvSolution} $d/system/fluid/
  src=$T/system/fluid/blockMeshDict; [ $fam = conformal ] && src=$T/system/fluid/blockMeshDict.monolithic
  python3 -I -c "
import re,sys
p,f,o=sys.argv[1],int(sys.argv[2]),sys.argv[3]
t=open(p).read()
t=re.sub(r'(hex\s+\([^)]*\)\s+)\(([^()]+)\)',lambda m:m.group(1)+'(%d %d %s)'%(int(m.group(2).split()[0])*f,int(m.group(2).split()[1])*f,m.group(2).split()[2]),t)
open(o,'w').write(t)" $src $lvl $d/system/fluid/blockMeshDict
  (cd $d && blockMesh -region fluid > log.blockMesh 2>&1 && foamFormatConvert -region fluid -constant > /dev/null 2>&1 ; \
   postProcess -region fluid -func writeCellVolumes -time 0 > log.V 2>&1; postProcess -region fluid -func writeCellCentres -time 0 > log.C 2>&1; \
   ls constant/fluid/V >/dev/null && echo "$fam $lvl $(python3 -I $S/../audit_ratio.py $d)" || tail -5 log.blockMesh)
done; done
