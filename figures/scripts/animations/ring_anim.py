# pvbatch ring_anim.py <case> <framesdir>: ring added-mass problem (strong level, quarter
# model mirrored), fluid kinematic pressure and the ring coloured by |D|; both regions
# warped by M x displacement (labelled), one frame per written time.
import sys, json, os
from paraview.simple import *
case, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True)
M = 250.0
series = json.load(open(f"{case}/VTK/fluid/ring_anim.vtm.series"))["files"]
def full(src):
    m = MergeBlocks(Input=src)
    a = Transform(Input=m); a.Transform.Scale = [-1, 1, 1]
    b = Transform(Input=m); b.Transform.Scale = [1, -1, 1]
    c = Transform(Input=m); c.Transform.Scale = [-1, -1, 1]
    return AppendDatasets(Input=[m, a, b, c])
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{series[0]['name']}"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{series[0]['name']}"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
fw = Calculator(Input=flp); fw.ResultArrayName = "Dm"; fw.Function = f"{M-1}*D"
fwarp = WarpByVector(Input=fw); fwarp.Vectors = ["POINTS", "Dm"]
fsl = Slice(Input=fwarp); fsl.SliceType = "Plane"; fsl.SliceType.Origin = [0, 0, 0.05]; fsl.SliceType.Normal = [0, 0, 1]
pk = Calculator(Input=fsl); pk.ResultArrayName = "pm"; pk.Function = "1e6*p"
F = full(pk)
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
sw = Calculator(Input=sop); sw.ResultArrayName = "Dm"; sw.Function = f"{M}*D"
swarp = WarpByVector(Input=sw); swarp.Vectors = ["POINTS", "Dm"]
ssl = Slice(Input=swarp); ssl.SliceType = "Plane"; ssl.SliceType.Origin = [0, 0, 0.05]; ssl.SliceType.Normal = [0, 0, 1]
dm = Calculator(Input=ssl); dm.ResultArrayName = "Dmm"; dm.Function = "1000*mag(D)"
S = Transform(Input=full(dm)); S.Transform.Translate = [0, 0, 0.5]
# global ranges
pmax = dmax = 0.0
for f in series:
    fl.FileName = [f"{case}/VTK/fluid/{f['name']}"]; so.FileName = [f"{case}/VTK/solid/{f['name']}"]
    pk.UpdatePipeline(); dm.UpdatePipeline()
    r = pk.PointData["pm"].GetRange(); pmax = max(pmax, abs(r[0]), abs(r[1]))
    dmax = max(dmax, dm.PointData["Dmm"].GetRange()[1])
print("pmax", pmax, "dmax mm", dmax)
P = 40.0; Dm = round(dmax + 0.005, 2)
v = CreateView("RenderView"); v.ViewSize = [1080, 1080]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(F, v); ColorBy(d1, ("POINTS", "pm"))
lp = GetColorTransferFunction("pm"); lp.ApplyPreset("Cool to Warm", True); lp.Discretize = 1; lp.NumberOfTableValues = 16; lp.RescaleTransferFunction(-P, P)
d2 = Show(S, v); ColorBy(d2, ("POINTS", "Dmm"))
ld = GetColorTransferFunction("Dmm"); ld.ApplyPreset("Grayscale", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 10; ld.RescaleTransferFunction(0.0, Dm)
for l, t, pos, labs in ((lp, "Fluid kinematic pressure (mm²/s²)", [0.05, 0.03], [-P, -P / 2, 0, P / 2, P]),
                         (ld, "Ring displacement magnitude (mm)", [0.55, 0.03], [0, Dm / 2, Dm])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 20; sb.LabelFontSize = 17
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.4; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.3g"
tt = Text(); tl = Show(tt, v); tl.WindowLocation = "Upper Left Corner"; tl.FontSize = 20; tl.Color = [0.15, 0.15, 0.15]
mg = Text(Text=f"deformation magnified {int(M)}×"); ml = Show(mg, v); ml.WindowLocation = "Upper Right Corner"; ml.FontSize = 20; ml.Color = [0.15, 0.15, 0.15]
v.CameraParallelProjection = 1
v.CameraPosition = [0, -0.2, 20]; v.CameraFocalPoint = [0, -0.2, 0]; v.CameraViewUp = [0, 1, 0]; v.CameraParallelScale = 1.78
for i, f in enumerate(series):
    fl.FileName = [f"{case}/VTK/fluid/{f['name']}"]; so.FileName = [f"{case}/VTK/solid/{f['name']}"]
    tt.Text = f"t = {f['time']:.2f} s"
    SaveScreenshot(f"{outdir}/f{i:04d}.png", v, ImageResolution=[1080, 1080])
print("frames", len(series))
