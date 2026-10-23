#!/usr/bin/env python3
"""vST diagnostic D3: the viscous traction on the fluid-solid interface of a
converged blobInTreacle state, from the same grad(U) (written by
`postProcess -region fluid -func 'grad(U)'`, i.e. fvc::grad with the
boundary correction n & grad(U)_b = snGrad(U)), with

    QM (newtonIcoFluid::patchViscousForce):
        nu*snGrad(U) + n & nu*dev2(T(grad(U)))      [vST yes]
        nu*snGrad(U)                                [vST no]
    pimpleFluid::patchViscousForce:
        n & (-devReff) = n & nu*dev(twoSymm(grad(U)))

per unit density, and the pressure traction p n, as face values and as
integrals over the interface (per unit depth of the 2-D case).

    vst_d3.py CASE [CASE ...] [--time 3] [--patch interface]
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np


def body(path):
    text = Path(path).read_text()
    return text[text.index("}", text.index("FoamFile")) + 1:]


def read_list(text, start=0):
    """The first OpenFOAM list N ( ... ) at or after start."""
    m = re.compile(r"(\d+)\s*\(").search(text, start)
    n = int(m.group(1))
    i, depth = m.end(), 1
    j = i
    while depth:
        c = text[j]
        depth += c == "("
        depth -= c == ")"
        j += 1
    return n, text[i:j - 1]


def numbers(s):
    return np.array([float(x) for x in re.findall(r"[-+0-9.eE]+", s)])


def mesh(case, time):
    poly = case / "constant/fluid/polyMesh"
    moved = case / time / "fluid/polyMesh/points"
    n, s = read_list(body(moved if moved.is_file() else poly / "points"))
    pts = numbers(s).reshape(n, 3)
    n, s = read_list(body(poly / "faces"))
    faces = [list(map(int, f.split()))
             for f in re.findall(r"\d+\(([^)]*)\)", s)]
    return pts, faces, body(poly / "boundary")


def patch_range(boundary, name):
    m = re.search(rf"\b{name}\s*\{{([^}}]*)\}}", boundary)
    nf = int(re.search(r"nFaces\s+(\d+)", m.group(1)).group(1))
    sf = int(re.search(r"startFace\s+(\d+)", m.group(1)).group(1))
    return sf, nf


def patch_values(path, name, width):
    text = body(path)
    i = text.index("boundaryField")
    m = re.search(rf"\b{name}\s*\{{", text[i:])
    j = i + m.end()
    end = text.index("}", j)
    k = text.find("value", j, end)
    if k < 0:
        return None, None
    head = text[k:k + 40]
    if "uniform" in head and "nonuniform" not in head:
        v = numbers(head.split("uniform")[1].split(";")[0])
        return None, v
    n, s = read_list(text, k)
    return n, numbers(s).reshape(n, width)


def area_vectors(pts, faces):
    out = []
    for f in faces:
        p = pts[f]
        c = p.mean(axis=0)
        a = np.zeros(3)
        for i in range(len(f)):
            a += 0.5 * np.cross(p[i] - c, p[(i + 1) % len(f)] - c)
        out.append(a)
    return np.array(out)


def analyse(case, time, patch):
    pts, faces, boundary = mesh(case, time)
    sf, nf = patch_range(boundary, patch)
    Sf = area_vectors(pts, faces[sf:sf + nf])
    magSf = np.linalg.norm(Sf, axis=1)
    n = Sf / magSf[:, None]          # out of the fluid
    nu = float(numbers(re.search(r"\bnu\b[^;]*;", body(
        case / "constant/fluid/transportProperties")).group(0).split("]")[-1])[0])
    _, G = patch_values(case / time / "fluid/grad(U)", patch, 9)
    G = G.reshape(-1, 3, 3)          # G[i][j] = d_i U_j (OpenFOAM grad)
    _, p = patch_values(case / time / "fluid/p", patch, 1)
    if p is None:
        # zeroGradient: the owner-cell values
        n_o, s_o = read_list(body(case / "constant/fluid/polyMesh/owner"))
        owner = numbers(s_o).astype(int)[sf:sf + nf]
        ptext = body(case / time / "fluid/p")
        _, s_p = read_list(ptext, ptext.index("internalField"))
        p = numbers(s_p)[owner]
    p = p.reshape(-1) * np.ones(nf)
    I = np.eye(3)
    tr = np.trace(G, axis1=1, axis2=2)
    GT = np.transpose(G, (0, 2, 1))
    sn = np.einsum("fi,fij->fj", n, G)                     # = snGrad(U)
    dev2GT = GT - (2.0 / 3.0) * tr[:, None, None] * I
    tT = nu * np.einsum("fi,fij->fj", n, dev2GT)           # transpose part
    tQMyes = nu * sn + tT
    tQMno = nu * sn
    twoSymm = G + GT
    devS = twoSymm - (1.0 / 3.0) * np.trace(twoSymm, axis1=1, axis2=2)[:, None, None] * I
    tPimple = nu * np.einsum("fi,fij->fj", n, devS)
    tp = -p[:, None] * n                                   # pressure on solid
    # force on the solid per unit density: -(viscous traction n & sigma)...
    # reported as integrals of the traction vectors themselves
    integ = lambda t: (t * magSf[:, None]).sum(axis=0)[:2].tolist()
    mag = lambda t: np.linalg.norm(t[:, :2], axis=1)
    d = tQMyes - tPimple
    return {
        "case": case.name, "faces": nf, "nu": nu,
        "max|tQMyes - tPimple|": float(mag(d).max()),
        "max|tPimple|": float(mag(tPimple).max()),
        "max|transpose part|": float(mag(tT).max()),
        "mean|transpose part|": float(mag(tT).mean()),
        "mean|viscous (QM yes)|": float(mag(tQMyes).mean()),
        "max|n.grad(U).n| (wall-normal stretching)":
            float(np.abs(np.einsum("fj,fj->f", sn, n)).max()),
        "max|tr grad(U)| at wall": float(np.abs(tr).max()),
        "F_viscous_QMyes": integ(tQMyes), "F_viscous_QMno": integ(tQMno),
        "F_viscous_pimple": integ(tPimple), "F_transpose": integ(tT),
        "F_pressure": integ(tp),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="+", type=Path)
    ap.add_argument("--time", default="3")
    ap.add_argument("--patch", default="interface")
    args = ap.parse_args()
    out = [analyse(c, args.time, args.patch) for c in args.cases]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
