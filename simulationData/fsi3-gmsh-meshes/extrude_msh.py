#!/usr/bin/env python3
"""Extrude a 2-D gmsh msh2 mesh (tri/quad, named physical curves) one cell in z
and write a 3-D msh2 for gmshToFoam: quads -> hexes, triangles -> prisms, each
boundary line -> a side quad with its curve's physical name, the z = 0 and
z = dz faces -> 'frontAndBackPlanes'.

    python3 extrude_msh.py mesh2d.msh mesh.msh --dz 0.015
"""
import argparse


def read(path):
    L = open(path).read().split("\n")
    i = 0
    names, nodes, elems = {}, {}, []
    while i < len(L):
        t = L[i].strip()
        if t == "$PhysicalNames":
            n = int(L[i + 1]); [names.__setitem__((int(x.split()[0]), int(x.split()[1])), x.split()[2].strip('"')) for x in L[i + 2:i + 2 + n]]; i += n + 2
        elif t == "$Nodes":
            n = int(L[i + 1])
            for x in L[i + 2:i + 2 + n]:
                a = x.split(); nodes[int(a[0])] = (float(a[1]), float(a[2]))
            i += n + 2
        elif t == "$Elements":
            n = int(L[i + 1])
            for x in L[i + 2:i + 2 + n]:
                a = list(map(int, x.split())); nt = a[2]
                elems.append((a[1], a[3], a[3 + nt:]))
            i += n + 2
        else:
            i += 1
    return names, nodes, elems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("--dz", type=float, default=0.015)
    a = ap.parse_args()
    names, nodes, elems = read(a.src)
    ids = sorted(nodes); idx = {k: i + 1 for i, k in enumerate(ids)}; N = len(ids)
    pnames = {v: k[1] for k, v in names.items()}
    fluid = pnames["fluid"]; fb = max(k[1] for k in names) + 1
    out_names = [(2, k[1], v) for k, v in names.items() if k[0] == 1] + [(2, fb, "frontAndBackPlanes"), (3, fluid, "fluid")]
    E = []
    for typ, tag, v in elems:
        v = [idx[x] for x in v]
        if typ == 1:  # line -> side quad
            E.append((3, tag, [v[0], v[1], v[1] + N, v[0] + N]))
        elif typ in (2, 3):
            # orient every face counter-clockwise (+z normal) before extruding
            xy = [nodes[ids[k - 1]] for k in v]
            area2 = sum(xy[i][0] * xy[(i + 1) % len(xy)][1] - xy[(i + 1) % len(xy)][0] * xy[i][1] for i in range(len(xy)))
            if area2 < 0:
                v = v[::-1]
            E.append((typ, fb, v)); E.append((typ, fb, [x + N for x in v[::-1]]))
            E.append((6 if typ == 2 else 5, fluid, v + [x + N for x in v]))
        elif typ == 15:
            continue
        else:
            raise SystemExit(f"element type {typ} not handled")
    # gmshToFoam numbers the patches in order of appearance: sort the boundary
    # faces by physical tag (= order of definition in the geo), volumes last
    E.sort(key=lambda e: (e[0] in (5, 6), e[1]))
    with open(a.dst, "w") as f:
        f.write("$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$PhysicalNames\n%d\n" % len(out_names))
        for d, t, n in out_names:
            f.write(f'{d} {t} "{n}"\n')
        f.write("$EndPhysicalNames\n$Nodes\n%d\n" % (2 * N))
        for z in (0.0, a.dz):
            for k in ids:
                x, y = nodes[k]; f.write(f"{idx[k] + (N if z else 0)} {x:.12g} {y:.12g} {z:g}\n")
        f.write("$EndNodes\n$Elements\n%d\n" % len(E))
        for i, (typ, tag, v) in enumerate(E, 1):
            f.write(f"{i} {typ} 2 {tag} {tag} " + " ".join(map(str, v)) + "\n")
        f.write("$EndElements\n")
    nq = sum(1 for e in E if e[0] == 5); nt = sum(1 for e in E if e[0] == 6)
    print(f"{a.dst}: {nq} hexes, {nt} prisms")


if __name__ == "__main__":
    main()
