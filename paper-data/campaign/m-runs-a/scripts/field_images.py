#!/usr/bin/env pvpython
"""Field images of the solver paper (F-field), one script for every case so
that colour maps, colour-bar placement, background and resolution are the
same everywhere.

    pvbatch --opengl-window-backend EGL field_images.py CASE CASE_DIR OUT.png
        [--time T] [--width 2400] [--height 1400]

Fluid: velocity magnitude (viridis), optional streamlines (white). Solid: on
its deformed shape (warped by the cell displacement interpolated to the
points), coloured by the equivalent (von Mises) stress (inferno). Perceptually
uniform maps only; white background; horizontal colour bars below the image.
CASE selects the view and the streamline seeds (CASES below).
"""
import argparse
import json
from pathlib import Path

from paraview.simple import (
    CellDatatoPointData, ColorBy, CreateView, GetColorTransferFunction,
    GetScalarBar, Hide, Line, OpenFOAMReader, Render, SaveScreenshot, Show,
    Reflect, Slice, StreamTracerWithCustomSource, Transform, WarpByVector,
)

CASES = {
    # channel (y 1-2) from x = 0, cavity x 2-6, y 0-1 above the plate:
    # seeds across the channel inlet, and forward only, for about one loop,
    # down the cavity centre (closed recirculation)
    "cavityFlexibleBottom": dict(
        streamlines=[dict(p1=[0.02, 1.03, 0], p2=[0.02, 1.97, 0], n=12),
                     dict(p1=[4.0, 0.15, 0], p2=[4.0, 0.95, 0], n=7,
                          length=9.0)],
        warp=1.0, title_u="|U| (m/s)", title_s="von Mises stress (Pa)"),
    # flow over the half-cylinder blob on the lower wall
    "blobInTreacle": dict(
        streamlines=[dict(p1=[0.05, -0.45, 0], p2=[0.05, 0.95, 0], n=30)],
        warp=1.0, title_u="|U| (m/s)", title_s="von Mises stress (Pa)"),
    # quarter annulus (symmetry on x = 0 and y = 0) mirrored to the full
    # ring; the ovalling amplitude is about 5e-4 m, so the displacement of
    # the ring and of the fluid mesh is magnified (point displacement pointD;
    # the solid mesh is the reference one, the fluid mesh has moved by
    # pointD); seeds on the four diagonals across the annulus
    "ringAddedMass": dict(
        streamlines=[dict(p1=[c * 1.07, s * 1.07, 0], p2=[c * 1.48, s * 1.48, 0],
                          n=6) for c in (0.7071, -0.7071)
                     for s in (0.7071, -0.7071)],
        mirror=True, warp=150.0, warp_vector="pointD", warp_fluid=True,
        title_u="|U| (m/s)",
        title_s="von Mises stress (Pa); displacement x150"),
}


def region(case, name, time, mirror=False):
    r = OpenFOAMReader(FileName=str(case / "case.foam"))
    r.MeshRegions = [f"/{name}/internalMesh"]
    r.CellArrays = ["U", "D", "sigmaEq", "p"]
    r.PointArrays = ["pointD"]
    r.UpdatePipeline(time)
    out = CellDatatoPointData(Input=r)
    if mirror:
        # about x = 0, then y = 0; every vector and tensor array flipped
        for normal in ([1, 0, 0], [0, 1, 0]):
            out = Reflect(Input=out, CopyInput=1, ReflectAllInputArrays=1)
            out.ReflectionPlane.Origin = [0, 0, 0]
            out.ReflectionPlane.Normal = normal
    return out


def mid_slice(src, time):
    """The cases are one cell thick in z: show the mid-plane, so that the
    image is 2-D (no side faces of the extruded mesh)."""
    src.UpdatePipeline(time)
    b = src.GetDataInformation().GetBounds()
    sl = Slice(Input=src)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = [0, 0, 0.5 * (b[4] + b[5])]
    sl.SliceType.Normal = [0, 0, 1]
    sl.UpdatePipeline(time)
    return sl, b


def colour_bar(view, lut, title, position):
    bar = GetScalarBar(lut, view)
    bar.Title = title
    bar.ComponentTitle = ""
    bar.Orientation = "Horizontal"
    bar.WindowLocation = "Any Location"
    bar.Position = position
    bar.ScalarBarLength = 0.33
    bar.TitleColor = bar.LabelColor = [0, 0, 0]
    bar.TitleFontSize = bar.LabelFontSize = 18
    bar.Visibility = 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case", choices=sorted(CASES))
    ap.add_argument("case_dir", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--time", type=float)
    ap.add_argument("--width", type=int, default=2400)
    ap.add_argument("--height", type=int, default=1400)
    a = ap.parse_args()
    cfg = CASES[a.case]

    probe = OpenFOAMReader(FileName=str(a.case_dir / "case.foam"))
    tv = probe.TimestepValues
    if a.time is not None:
        time = a.time
    else:
        time = float(tv[-1]) if hasattr(tv, "__len__") else float(tv)
    Hide(probe)

    view = CreateView("RenderView")
    view.ViewSize = [a.width, a.height]
    view.Background = [1, 1, 1]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0
    view.CameraParallelProjection = 1
    view.ViewTime = time

    fluid3d = region(a.case_dir, "fluid", time, cfg.get("mirror", False))
    if cfg.get("warp_fluid"):
        # the fluid mesh has moved by pointD: magnify to match the solid
        fluid3d = WarpByVector(Input=fluid3d,
                               Vectors=["POINTS", cfg["warp_vector"]],
                               ScaleFactor=cfg["warp"] - 1.0)
    fluid, fb = mid_slice(fluid3d, time)
    fd = Show(fluid, view)
    ColorBy(fd, ("POINTS", "U", "Magnitude"))
    lut_u = GetColorTransferFunction("U")
    lut_u.ApplyPreset("Viridis (matplotlib)", True)
    fd.RescaleTransferFunctionToDataRange(True, False)

    for s in cfg.get("streamlines", []):
        zc = 0.5 * (fb[4] + fb[5])
        seed = Line(Point1=[s["p1"][0], s["p1"][1], zc],
                    Point2=[s["p2"][0], s["p2"][1], zc], Resolution=s["n"])
        st = StreamTracerWithCustomSource(Input=fluid3d, SeedSource=seed)
        st.Vectors = ["POINTS", "U"]
        # closed recirculation: about one loop, not a filled spiral
        st.MaximumStreamlineLength = s.get("length", 100.0)
        st.IntegrationDirection = "FORWARD" if "length" in s else "BOTH"
        # lifted towards the camera so that they are drawn over the slice
        lift = Transform(Input=st)
        lift.Transform.Translate = [0, 0, 0.6 * (fb[5] - fb[4])]
        sd = Show(lift, view)
        ColorBy(sd, None)
        sd.AmbientColor = sd.DiffuseColor = [1, 1, 1]
        sd.LineWidth = 1.5

    solid3d = region(a.case_dir, "solid", time, cfg.get("mirror", False))
    solid, _ = mid_slice(solid3d, time)
    warp = WarpByVector(Input=solid,
                        Vectors=["POINTS", cfg.get("warp_vector", "D")],
                        ScaleFactor=cfg["warp"])
    sod = Show(warp, view)
    ColorBy(sod, ("POINTS", "sigmaEq"))
    lut_s = GetColorTransferFunction("sigmaEq")
    lut_s.ApplyPreset("Inferno (matplotlib)", True)
    sod.RescaleTransferFunctionToDataRange(True, False)

    colour_bar(view, lut_u, cfg["title_u"], [0.08, 0.03])
    colour_bar(view, lut_s, cfg["title_s"], [0.58, 0.03])

    # Parallel view along -z, framed on the deformed geometry with room for
    # the colour bars below
    warp.UpdatePipeline(time)
    wb = warp.GetDataInformation().GetBounds()
    xmin, xmax = min(fb[0], wb[0]), max(fb[1], wb[1])
    ymin, ymax = min(fb[2], wb[2]), max(fb[3], wb[3])
    zc = 0.5 * (fb[4] + fb[5])
    w, h = xmax - xmin, ymax - ymin
    bar_band = 0.16                       # fraction of the image height
    aspect = a.width / a.height
    scale = 0.5 * max(h / (1 - bar_band), w / aspect) * 1.04
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax) - scale * bar_band
    Render(view)   # the first render resets the camera; set it afterwards
    view.CameraFocalPoint = [cx, cy, zc]
    view.CameraPosition = [cx, cy, zc + 10 * max(w, h)]
    view.CameraViewUp = [0, 1, 0]
    view.CameraParallelScale = scale
    Render(view)
    print(f"bounds fluid {fb[:4]} deformed {wb[:4]}; scale set {scale:.4g},"
          f" after render {view.CameraParallelScale:.4g}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    SaveScreenshot(str(a.out), view, ImageResolution=[a.width, a.height])
    a.out.with_suffix(".json").write_text(json.dumps(dict(
        case=a.case, case_dir=str(a.case_dir), time=time, size=[a.width,
        a.height], renderer=view.GetRenderWindow().ReportCapabilities()
        .splitlines()[1:3]), indent=2))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
