#!/bin/bash
# Usage: mk_foam.sh <dir with mesh.msh>  -> <dir>/constant/polyMesh
# gmshToFoam, then frontAndBackPlanes -> empty and the physicalType entries
# removed, then checkMesh. Needs an OpenFOAM environment (v2512 was used).
set -e
d=$1
mkdir -p "$d/system" "$d/constant"
[ -f "$d/system/controlDict" ] || cat > "$d/system/controlDict" <<'CD'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application gmshToFoam; startFrom startTime; startTime 0; stopAt endTime;
endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;
CD
[ -f "$d/system/fvSchemes" ] || cat > "$d/system/fvSchemes" <<'FS'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default Euler; } gradSchemes { default Gauss linear; }
divSchemes { default none; } laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; } snGradSchemes { default corrected; }
FS
[ -f "$d/system/fvSolution" ] || cat > "$d/system/fvSolution" <<'FV'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers {}
FV
cd "$d"
gmshToFoam mesh.msh > log.gmshToFoam 2>&1 || { echo "gmshToFoam failed"; exit 1; }
python3 - <<'PY'
import re
f = "constant/polyMesh/boundary"
t = open(f).read()
t = re.sub(r"(frontAndBackPlanes\s*\{[^}]*?type\s+)\w+;", r"\1empty;", t)
t = re.sub(r"\s*physicalType\s+\w+;", "", t)
open(f, "w").write(t)
PY
checkMesh -noFunctionObjects > log.checkMesh 2>&1 || true
grep -E "^ +cells:|non-orthogonality Max|Mesh OK|Failed" log.checkMesh
grep -q "Mesh OK" log.checkMesh || { echo "checkMesh FAILED in $d"; exit 2; }
