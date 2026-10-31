#!/usr/bin/env python3
"""Smooth-family blockMeshDict (ht_mesh_smooth.py) at one level, with the
division counts of selected edge chains taken from a finer level (localisation
test: one region at the finer level, gradings unchanged).

Regions (chains named by one member edge):
  ring : cylinder ring, radial (6-10) and circumferential (10-11, 10-16, 16-17)
  flag : y-rows of the band/flag/wake row, y 0.12-0.28 m (7-13, 14-20, 19-24),
         and along the flag, x 0.3-0.6 m (13-14, 19-20)

    python3 ht_mesh_local.py --base <tutorial blockMeshDict> --level 3 \
        --fine-level 4 --region ring --out blockMeshDict
"""
import argparse
import sys
from pathlib import Path

S = Path("/Volumes/OpenFOAM/philipc-v2512/s4f-htsmooth/tutorials/fluidSolidInteraction/TurekHron2006/verification/scripts")
sys.path.insert(0, str(S))
import ht_mesh_smooth as ms  # noqa: E402

REGIONS = {
    "ring": [(6, 10), (10, 11), (10, 16), (16, 17)],
    "flag": [(7, 13), (14, 20), (19, 24), (13, 14), (19, 20)],
}


def build(base, level, fine, edges, params=None):
    p = dict(ms.DEFAULTS, **(params or {}))
    pts, arcs, blocks, chains, nchain, dists, find, key = ms.design(base, p)
    fine_chains = {find(key(a, b)) for a, b in edges}

    def n(c):
        return nchain[c] * (fine if c in fine_chains else level)

    def g(a, b):
        k = key(a, b)
        return dists[k].grading(reverse=(k != (a, b)))
    lines, cells = [], 0
    for v in blocks:
        nx, ny = n(find(key(v[0], v[1]))), n(find(key(v[0], v[3])))
        cells += nx * ny
        eg = [g(v[0], v[1]), g(v[3], v[2]), g(v[3], v[2]), g(v[0], v[1]),
              g(v[0], v[3]), g(v[1], v[2]), g(v[1], v[2]), g(v[0], v[3]), "1", "1", "1", "1"]
        lines.append(f"    hex ({' '.join(map(str, v))}) ({nx} {ny} 1)\n        edgeGrading\n        (\n"
                     + "".join(f"            {x}\n" for x in eg) + "        )")
    i0 = base.index("blocks")
    i1 = base.index("edges", i0)
    refined = sorted({e for c in fine_chains for e in chains[c]})
    return base[:i0] + "blocks\n(\n" + "\n".join(lines) + "\n);\n\n" + base[i1:], cells, refined


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--level", type=int, default=3)
    ap.add_argument("--fine-level", type=int, default=4)
    ap.add_argument("--region", choices=sorted(REGIONS), action="append", required=True)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    edges = [e for r in a.region for e in REGIONS[r]]
    txt, cells, refined = build(a.base.read_text(), a.level, a.fine_level, edges)
    print(f"cells {cells}; chains at level {a.fine_level} contain edges {refined}")
    if a.out:
        a.out.write_text(txt)
