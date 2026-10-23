#!/usr/bin/env pvpython
"""Render the mesh layer of a 3-D case geometry figure with ParaView.

The 3-D counterpart of mesh_layer.py: the cell edges on chosen boundary
patches of the fluid and solid meshes, drawn with the same grey levels (fluid
light grey edges on white, solid dark grey edges on light grey), from a fixed
orthographic camera, to a PNG with a transparent background. A JSON file
written next to the image records the camera, so the render can be repeated.

Usage (run with ParaView's pvpython):
    pvpython mesh_render3d.py OUT.png CASE/CASE.foam \
        --fluid inlet,symmetry-x,symmetry-y \
        --solid inlet,symmetry-x,symmetry-y,outer-wall \
        [--view -1,-0.8,-1.2] [--up 0,1,0] [--width-px 3000]

The .foam file may be empty (`touch CASE/CASE.foam`); binary polyMesh files
are read directly.
"""
import argparse
import json
from pathlib import Path

from paraview.simple import (CreateView, OpenFOAMReader, SaveScreenshot,
                             Show)

STYLE = {
    # edge colour, surface colour, line width (px)
    "fluid": ((0.55, 0.55, 0.55), (1.0, 1.0, 1.0), 1.0),
    "solid": ((0.25, 0.25, 0.25), (0.88, 0.88, 0.88), 1.0),
}


def vec(text):
    return [float(v) for v in text.split(",")]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def unit(a):
    n = dot(a, a) ** 0.5
    return [x / n for x in a]


def orthonormal_up(d, up):
    d = unit(d)
    return unit([u - dot(up, d) * x for u, x in zip(up, d)])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out")
    ap.add_argument("foam")
    ap.add_argument("--fluid", default="", help="comma-separated patches")
    ap.add_argument("--solid", default="", help="comma-separated patches")
    ap.add_argument("--view", default="-1,-0.8,-1.2",
                    help="direction from the focal point to the camera")
    ap.add_argument("--up", default="0,1,0")
    ap.add_argument("--width-px", type=int, default=3000)
    ap.add_argument("--aspect", type=float, default=0.5,
                    help="image height / width")
    ap.add_argument("--cull-front", default="",
                    help="regions (e.g. fluid) whose front faces are hidden")
    ap.add_argument("--zoom", type=float, default=1.0,
                    help="magnify after fitting the bounding sphere")
    args = ap.parse_args()

    view = CreateView("RenderView")
    view.OrientationAxesVisibility = 0
    view.CameraParallelProjection = 1
    view.Background = [1, 1, 1]
    view.UseColorPaletteForBackground = 0

    bounds = None
    for region in ("fluid", "solid"):
        patches = [p for p in getattr(args, region).split(",") if p]
        if not patches:
            continue
        reader = OpenFOAMReader(FileName=args.foam)
        reader.MeshRegions = [f"/{region}/patch/{p}" for p in patches]
        reader.CellArrays = []
        reader.UpdatePipeline()
        b = reader.GetDataInformation().GetBounds()
        bounds = b if bounds is None else [
            min(bounds[i], b[i]) if i % 2 == 0 else max(bounds[i], b[i])
            for i in range(6)]
        disp = Show(reader, view)
        disp.ColorArrayName = ["POINTS", ""]
        edge, face, lw = STYLE[region]
        disp.SetRepresentationType("Surface With Edges")
        disp.AmbientColor = face
        disp.DiffuseColor = face
        disp.EdgeColor = edge
        disp.LineWidth = lw
        disp.Ambient = 1.0
        disp.Diffuse = 0.0
        disp.Specular = 0.0
        if region in args.cull_front.split(","):
            # boundary faces point out of the domain: culling the front
            # faces leaves the far walls of an enclosing box visible
            disp.BackfaceRepresentation = "Cull Frontface"

    centre = [0.5 * (bounds[2 * i] + bounds[2 * i + 1]) for i in range(3)]
    d = vec(args.view)
    size = max(bounds[2 * i + 1] - bounds[2 * i] for i in range(3))
    view.CameraFocalPoint = centre
    view.CameraPosition = [centre[i] + 10 * size * d[i] for i in range(3)]
    view.CameraViewUp = vec(args.up)
    w = args.width_px
    h = int(round(args.aspect * w))
    view.ViewSize = [w, h]
    # fit the projected bounding box: parallel scale is half the height
    up = orthonormal_up(d, vec(args.up))
    right = unit(cross(up, d))
    corners = [[bounds[i], bounds[2 + j], bounds[4 + k]]
               for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    pu = [dot(c, up) for c in corners]
    pr = [dot(c, right) for c in corners]
    half_h = max(0.5 * (max(pu) - min(pu)),
                 0.5 * (max(pr) - min(pr)) * h / w)
    view.CameraParallelScale = 1.03 * half_h / args.zoom
    SaveScreenshot(args.out, view, ImageResolution=[w, h],
                   TransparentBackground=1)

    meta = {"foam": Path(args.foam).name, "fluid": args.fluid,
            "solid": args.solid, "view": d, "up": vec(args.up),
            "width_px": w, "height_px": h, "zoom": args.zoom,
            "parallel_scale": view.CameraParallelScale, "bounds": list(bounds),
            "projection": "parallel"}
    Path(args.out).with_suffix(".json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
