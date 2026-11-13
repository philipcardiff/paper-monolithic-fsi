# pvbatch fsi3_anim.py <dir with animFluidVTK/ and animSolidVTK/> <framesdir> [first last]
# Hron-Turek FSI3 (QM level 2, restart from t = 5.888 s): fluid vorticity (z) and the flag
# coloured by |D| on the displaced configuration, with the undeformed flag outline; one frame
# per VTK output (every 35 steps, 0.00495 s).
import sys, os, json
from paraview.simple import *
src, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True)
fser = json.load(open(f"{src}/animFluidVTK/fluid/fsi3_qm2.vtm.series"))["files"]
sser = {round(f["time"], 5): f["name"] for f in json.load(open(f"{src}/animSolidVTK/solid/fsi3_qm2.vtm.series"))["files"]}
first = int(sys.argv[3]) if len(sys.argv) > 3 else 0; last = int(sys.argv[4]) if len(sys.argv) > 4 else len(fser) - 1
fl = XMLMultiBlockDataReader(FileName=[f"{src}/animFluidVTK/fluid/{fser[0]['name']}"])
so = XMLMultiBlockDataReader(FileName=[f"{src}/animSolidVTK/solid/{sser[round(fser[0]['time'], 5)]}"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
wz = Calculator(Input=flp); wz.ResultArrayName = "wz"; wz.Function = "vorticity_Z"
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
warp = WarpByVector(Input=sop); warp.Vectors = ["POINTS", "D"]
soi.UpdatePipeline(); b = soi.GetDataInformation().GetBounds()
sl = Slice(Input=soi); sl.SliceType = "Plane"; sl.SliceType.Origin = [0, 0, 0.5 * (b[4] + b[5])]; sl.SliceType.Normal = [0, 0, 1]
und = Transform(Input=Outline(Input=sl)); und.Transform.Translate = [0, 0, 0.05]
v = CreateView("RenderView"); v.ViewSize = [1920, 688]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(wz, v); ColorBy(d1, ("POINTS", "wz"))
lw = GetColorTransferFunction("wz"); lw.ApplyPreset("PRGn", True); lw.Discretize = 1; lw.NumberOfTableValues = 20
d2 = Show(warp, v); ColorBy(d2, ("POINTS", "D", "Magnitude"))
ld = GetColorTransferFunction("D"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 10
d3 = Show(und, v); d3.AmbientColor = d3.DiffuseColor = [0, 0, 0]; d3.LineWidth = 2.5; d3.ColorArrayName = ["POINTS", ""]
for l, r in ((lw, (-120.0, 120.0)), (ld, (0.0, 0.04))):
    l.AutomaticRescaleRangeMode = "Never"; l.RescaleTransferFunction(*r)
for l, t, pos, labs in ((lw, "Fluid vorticity (1/s)", [0.12, 0.03], [-120, -60, 0, 60, 120]),
                         (ld, "Flag displacement magnitude (m)", [0.6, 0.03], [0, 0.01, 0.02, 0.03, 0.04])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 22; sb.LabelFontSize = 18
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"
tt = Text(); tl = Show(tt, v); tl.WindowLocation = "Upper Left Corner"; tl.FontSize = 20; tl.Color = [0.15, 0.15, 0.15]
v.CameraParallelProjection = 1
xc, yc = 0.81, 0.122
v.CameraPosition = [xc, yc, 10]; v.CameraFocalPoint = [xc, yc, 0]; v.CameraViewUp = [0, 1, 0]; v.CameraParallelScale = 0.29
for i, f in enumerate(fser[first:last + 1]):
    fl.FileName = [f"{src}/animFluidVTK/fluid/{f['name']}"]
    so.FileName = [f"{src}/animSolidVTK/solid/{sser[round(f['time'], 5)]}"]
    tt.Text = f"t = {f['time']:.3f} s"
    SaveScreenshot(f"{outdir}/f{i:04d}.png", v, ImageResolution=[1920, 688])
print("frames", last - first + 1)
