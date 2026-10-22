#!/usr/bin/env python3
"""Draw the mesh layer of a case geometry figure from OpenFOAM polyMesh files.

The geometry figures of the paper have two layers: this mesh layer (cell edges
of the fluid and solid meshes, drawn to PDF with fixed line widths and grey
levels), and a TikZ annotation layer (dimensions, labels, boundary conditions;
figures/tikz/geomstyle.tex) placed over it. A JSON file written next to the
PDF gives the plotted bounding box, so the TikZ layer can place annotations
in model coordinates.

Two-dimensional meshes (one cell thick, `empty` front and back) and
axisymmetric wedge meshes are drawn from the cell faces of one boundary
patch that lies in the plotting plane: by default the first patch of type
`empty` or `wedge`, taking only the faces on its lower side in the
out-of-plane coordinate. Three-dimensional meshes are not handled here (use
a ParaView render).

The polyMesh files must be in ASCII. If they are binary, run
`foamFormatConvert -constant` (with `-region <name>` for each region) first.

Usage:
    mesh_layer.py OUT.pdf --region fluid=CASE/constant/fluid/polyMesh \
        --region solid=CASE/constant/solid/polyMesh \
        [--axes x,y] [--patch NAME] [--scale 1] [--width-cm 15]

`--axes` picks the two plotted coordinates (x, y or z; for a wedge in the
x-y plane, x,y). Region names `fluid` and `solid` get the paper's grey
levels; any other name is drawn like the fluid.
"""
import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

STYLE = {
    # edge colour, face colour, line width (pt)
    "fluid": ("0.55", "none", 0.25),
    "solid": ("0.25", "0.88", 0.35),
}
AXIS = {"x": 0, "y": 1, "z": 2}


def strip_header(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    i = text.find("FoamFile")
    if i >= 0:
        j = text.find("}", i)
        text = text[j + 1:]
    return text


def list_body(text):
    """Return the text between the outer '(' and ')' of an OpenFOAM list."""
    text = strip_header(text)
    i = text.find("(")
    j = text.rfind(")")
    return text[i + 1:j]


def read_points(path):
    body = list_body(path.read_text())
    return [tuple(float(v) for v in m.split())
            for m in re.findall(r"\(([^()]*)\)", body)]


def read_faces(path):
    body = list_body(path.read_text())
    return [[int(v) for v in m.split()]
            for m in re.findall(r"\d+\s*\(([^()]*)\)", body)]


def read_boundary(path):
    text = strip_header(path.read_text())
    patches = {}
    for name, block in re.findall(r"(\w+)\s*\{([^{}]*)\}", text):
        fields = dict(re.findall(r"(\w+)\s+([^;]+);", block))
        if "nFaces" in fields:
            patches[name] = {
                "type": fields.get("type", "").strip(),
                "startFace": int(fields["startFace"]),
                "nFaces": int(fields["nFaces"]),
            }
    return patches


def plane_faces(mesh_dir, axes, patch_name=None):
    mesh_dir = Path(mesh_dir)
    points = read_points(mesh_dir / "points")
    faces = read_faces(mesh_dir / "faces")
    patches = read_boundary(mesh_dir / "boundary")
    if patch_name is None:
        cands = [n for n, p in patches.items()
                 if p["type"] in ("empty", "wedge")]
        if not cands:
            raise SystemExit(f"{mesh_dir}: no empty or wedge patch; "
                             "use --patch")
        patch_name = cands[0]
    p = patches[patch_name]
    sel = faces[p["startFace"]:p["startFace"] + p["nFaces"]]
    a, b = (AXIS[c] for c in axes)
    normal = 3 - a - b
    # keep the faces on the lower side in the out-of-plane coordinate
    zmid = [sum(points[i][normal] for i in f) / len(f) for f in sel]
    zcut = min(zmid) + 0.5 * (max(zmid) - min(zmid))
    polys = [[(points[i][a], points[i][b]) for i in f]
             for f, z in zip(sel, zmid) if z <= zcut + 1e-12]
    return polys


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out")
    ap.add_argument("--region", action="append", required=True,
                    help="NAME=PATH/TO/polyMesh (repeatable, drawn in order)")
    ap.add_argument("--axes", default="x,y")
    ap.add_argument("--patch", default=None)
    ap.add_argument("--scale", type=float, default=1.0,
                    help="multiply coordinates (e.g. 100 for m to cm)")
    ap.add_argument("--width-cm", type=float, default=15.0)
    args = ap.parse_args()
    axes = args.axes.split(",")

    layers = []
    xs, ys = [], []
    for spec in args.region:
        name, path = spec.split("=", 1)
        polys = [[(args.scale * u, args.scale * v) for u, v in poly]
                 for poly in plane_faces(path, axes, args.patch)]
        layers.append((name, polys))
        for poly in polys:
            for u, v in poly:
                xs.append(u)
                ys.append(v)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w = args.width_cm / 2.54
    h = w * (y1 - y0) / (x1 - x0)

    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    for name, polys in layers:
        edge, face, lw = STYLE.get(name, STYLE["fluid"])
        ax.add_collection(PolyCollection(
            polys, edgecolors=edge, facecolors=face, linewidths=lw))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(args.out, transparent=True)

    meta = {"xmin": x0, "xmax": x1, "ymin": y0, "ymax": y1,
            "width_cm": args.width_cm, "height_cm": h * 2.54,
            "axes": axes, "scale": args.scale}
    Path(args.out).with_suffix(".json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
