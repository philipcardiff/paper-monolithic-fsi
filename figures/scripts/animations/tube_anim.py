# pvbatch tube_anim.py <case> <framesdir>: 3-D pressure-pulse tube (tutorial mesh, QM):
# half tube (quarter model reflected), fluid pressure on the symmetry plane, wall
# coloured by |D| and displaced x10; one frame per written time (every 0.1 ms).
import sys, os, json
from paraview.simple import *
case, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True)
nm = os.path.basename(case.rstrip("/"))
series = json.load(open(f"{case}/VTK/fluid/{nm}.vtm.series"))["files"]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{series[0]['name']}"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{series[0]['name']}"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]
flr = Reflect(Input=CellDatatoPointData(Input=fli)); flr.Plane = "Y Min"; flr.CopyInput = 1
sor = Reflect(Input=CellDatatoPointData(Input=soi)); sor.Plane = "Y Min"; sor.CopyInput = 1
calc = Calculator(Input=sor); calc.ResultArrayName = "Dmm"; calc.Function = "mag(D)*1000"
warp = WarpByVector(Input=calc); warp.Vectors = ["POINTS", "D"]; warp.ScaleFactor = 10.0
pmin = pmax = dmax = 0.0
for f in series:
    fl.FileName = [f"{case}/VTK/fluid/{f['name']}"]; so.FileName = [f"{case}/VTK/solid/{f['name']}"]
    flr.UpdatePipeline(); calc.UpdatePipeline()
    r = flr.PointData["p"].GetRange(); pmin = min(pmin, r[0]); pmax = max(pmax, r[1]); dmax = max(dmax, calc.PointData["Dmm"].GetRange()[1])
print("p", pmin, pmax, "Dmm", dmax)
v = CreateView("RenderView"); v.ViewSize = [1920, 800]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(flr, v); ColorBy(d1, ("POINTS", "p"))
lp = GetColorTransferFunction("p"); lp.ApplyPreset("Viridis", True); lp.Discretize = 1; lp.NumberOfTableValues = 14
P1 = 1.4; P0 = -0.2 if pmin < -0.05 else 0.0; lp.RescaleTransferFunction(P0, P1)
d2 = Show(warp, v); ColorBy(d2, ("POINTS", "Dmm"))
ld = GetColorTransferFunction("Dmm"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 12
ld.RescaleTransferFunction(0.0, 0.16)
for l, t, pos, labs in ((lp, "Fluid kinematic pressure (m²/s²)", [0.08, 0.04], [0, 0.4, 0.8, 1.2]),
                        (ld, "Wall displacement magnitude (mm), shown ×10", [0.56, 0.04], [0, 0.04, 0.08, 0.12, 0.16])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 22; sb.LabelFontSize = 18
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.32; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs
tt = Text(); tl = Show(tt, v); tl.WindowLocation = "Upper Left Corner"; tl.FontSize = 22; tl.Color = [0.15, 0.15, 0.15]
v.CameraPosition = [-0.045, 0.012, 0.025]; v.CameraFocalPoint = [0.0, -0.0022, 0.025]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelProjection = 1; v.CameraParallelScale = 0.0118
for i, f in enumerate(series):
    fl.FileName = [f"{case}/VTK/fluid/{f['name']}"]; so.FileName = [f"{case}/VTK/solid/{f['name']}"]
    tt.Text = f"t = {1e3 * f['time']:.1f} ms"
    SaveScreenshot(f"{outdir}/f{i:04d}.png", v, ImageResolution=[1920, 800])
print("frames", len(series))
