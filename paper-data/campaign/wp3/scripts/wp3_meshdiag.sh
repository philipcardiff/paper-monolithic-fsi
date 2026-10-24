#!/bin/bash
# Mesh-motion diagnosis of a failed quasi-monolithic collapsibleChannel run
# written every time step (wp3_setup.py --write-every-step). No settings are
# changed (coordinator, 24 Oct: record, do not tune).
#
#   wp3_meshdiag.sh <run_dir>
#
# Writes into <run_dir>/meshdiag/:
#   d_history.csv   per time step and SNES iteration: the fluid mesh-motion
#                   (pseudo-solid D) residual norm and Krylov iterations
#   checkMesh.<t>   checkMesh -region fluid at t = 0 and at the last written
#                   time before the failure
#   jacobian.json   J = V/V0 per cell at that time (min, max, number <= 0)
#
# Requires the OpenFOAM/solids4foam environment (source env.sh).

set -u
d="$(cd "${1:?run dir}" && pwd)"
out="$d/meshdiag"
mkdir -p "$out"
cd "$d" || exit 1

python3 - "$d/log.solids4Foam" > "$out/d_history.csv" <<'EOF'
import re, sys
print("time,snes_it,fnorm,ksp_its,ksp_reason")
t = None; active = None; it = None; norm = None
for line in open(sys.argv[1], errors="replace"):
    s = line.strip()
    m = re.match(r"^Time = ([0-9.eE+-]+)\s*$", s)
    if m:
        t = m.group(1); active = None; continue
    m = re.match(r"^Solving .* for (\w+) using PETSc SNES", s)
    if m:
        active = m.group(1); continue
    if active != "D":
        continue
    m = re.match(r"^(\d+) SNES Function norm (\S+)", s)
    if m:
        if it is not None:
            print(f"{t},{it},{norm},,")
        it, norm = m.group(1), m.group(2); continue
    m = re.match(r"Linear solve (?:converged|did not converge) due to (\w+) "
                 r"iterations (\d+)", s)
    if m and it is not None:
        print(f"{t},{it},{norm},{m.group(2)},{m.group(1)}")
        it = None; continue
    if s.startswith("Nonlinear solve") and it is not None:
        print(f"{t},{it},{norm},,")
        it = None
EOF

last=$(ls -d [0-9]* 2>/dev/null | grep -v '^0$' | sort -g | tail -1)
echo "last written time: $last"
for t in 0 "$last"
do
    checkMesh -region fluid -time "$t" > "$out/checkMesh.$t" 2>&1
done
postProcess -region fluid -func writeCellVolumes -time "0,$last" \
    > "$out/log.writeCellVolumes" 2>&1

python3 - "$d" "$last" > "$out/jacobian.json" <<'EOF'
import json, re, sys
from pathlib import Path
d, last = Path(sys.argv[1]), sys.argv[2]

def read(t):
    text = (d / t / "fluid" / "V").read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*(\d+)\s*\(",
                  text)
    n = int(m.group(1))
    vals = text[m.end():].split(")", 1)[0].split()
    return [float(v) for v in vals[:n]]

v0, v1 = read("0"), read(last)
j = [b / a for a, b in zip(v0, v1)]
i = min(range(len(j)), key=j.__getitem__)
print(json.dumps({"time": float(last), "cells": len(j), "J_min": j[i],
                  "J_min_cell": i, "J_max": max(j),
                  "cells_J_le_0": sum(x <= 0 for x in j),
                  "cells_J_lt_0.1": sum(x < 0.1 for x in j)}, indent=1))
EOF
grep -E "Max skewness|Max non-orthogonality|Minimum face area|Min volume|negative|Failed|Mesh OK" \
    "$out/checkMesh.$last" | sed 's/^ *//'
cat "$out/jacobian.json"
