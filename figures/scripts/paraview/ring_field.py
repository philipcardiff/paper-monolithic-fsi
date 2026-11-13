# pvbatch ring_field.py <case> <step> <out.png>: ring added-mass problem (quarter model
# mirrored to the full annulus): fluid pressure at the final time of the strong-level
# run, ring coloured by displacement magnitude (no magnification).
import sys
from paraview.simple import *
case, step, out = sys.argv[1], sys.argv[2], sys.argv[3]
def full(src):
    m = MergeBlocks(Input=src)
    a = Transform(Input=m); a.Transform.Scale = [-1, 1, 1]
    b = Transform(Input=m); b.Transform.Scale = [1, -1, 1]
    c = Transform(Input=m); c.Transform.Scale = [-1, -1, 1]
    return AppendDatasets(Input=[m, a, b, c])
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{step}.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{step}.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
fsl = Slice(Input=flp); fsl.SliceType = "Plane"; fsl.SliceType.Origin = [0, 0, 0.05]; fsl.SliceType.Normal = [0, 0, 1]
pk = Calculator(Input=fsl); pk.ResultArrayName = "pm"; pk.Function = "1e6*p"
F = full(pk)
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
ssl = Slice(Input=sop); ssl.SliceType = "Plane"; ssl.SliceType.Origin = [0, 0, 0.05]; ssl.SliceType.Normal = [0, 0, 1]
dm = Calculator(Input=ssl); dm.ResultArrayName = "Dmm"; dm.Function = "1000*mag(D)"
S = Transform(Input=full(dm)); S.Transform.Translate = [0, 0, 0.01]
v = CreateView("RenderView"); v.ViewSize = [1600, 1500]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(F, v); ColorBy(d1, ("POINTS", "pm"))
lp = GetColorTransferFunction("pm"); lp.ApplyPreset("Cool to Warm", True); lp.Discretize = 1; lp.NumberOfTableValues = 16
P = 90.0; lp.RescaleTransferFunction(-P, P)
d2 = Show(S, v); ColorBy(d2, ("POINTS", "Dmm"))
ld = GetColorTransferFunction("Dmm"); ld.ApplyPreset("Grayscale", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 10; ld.RescaleTransferFunction(0.0, 0.18)
for l, t, pos, labs in ((lp, "Fluid kinematic pressure (mm²/s²)", [0.06, 0.02], [-90, -45, 0, 45, 90]),
                         (ld, "Ring displacement magnitude (mm)", [0.54, 0.02], [0, 0.06, 0.12, 0.18])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 24; sb.LabelFontSize = 20
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.4; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"
v.CameraParallelProjection = 1
v.CameraPosition = [0, -0.17, 20]; v.CameraFocalPoint = [0, -0.17, 0]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelScale = 1.72
SaveScreenshot(out, v, ImageResolution=[1600, 1500])
pk.UpdatePipeline(); print("p range (1e-6)", pk.PointData["pm"].GetRange())
