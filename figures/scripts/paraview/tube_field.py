# pvbatch tube_field.py <case> <step> <out.png>: 3-D pressure-pulse tube at t = 4 ms:
# half tube (quarter model reflected), fluid pressure on the longitudinal symmetry
# plane, wall coloured by |D| and displaced x10.
import sys
from paraview.simple import *
case, step, out = sys.argv[1], sys.argv[2], sys.argv[3]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/case_{step}.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/case_{step}.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]
flr = Reflect(Input=CellDatatoPointData(Input=fli)); flr.Plane = "Y Min"; flr.CopyInput = 1
sor = Reflect(Input=CellDatatoPointData(Input=soi)); sor.Plane = "Y Min"; sor.CopyInput = 1
calc = Calculator(Input=sor); calc.ResultArrayName = "Dmm"; calc.Function = "mag(D)*1000"
warp = WarpByVector(Input=calc); warp.Vectors = ["POINTS", "D"]; warp.ScaleFactor = 10.0
v = CreateView("RenderView"); v.ViewSize = [2400, 1000]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(flr, v); ColorBy(d1, ("POINTS", "p"))
lp = GetColorTransferFunction("p"); lp.ApplyPreset("Viridis", True); lp.Discretize = 1; lp.NumberOfTableValues = 14
lp.RescaleTransferFunction(0.0, 1.4)
d2 = Show(warp, v); ColorBy(d2, ("POINTS", "Dmm"))
ld = GetColorTransferFunction("Dmm"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 12
ld.RescaleTransferFunction(0.0, 0.16)
for l, t, pos in ((lp, "Fluid kinematic pressure (m\u00b2/s\u00b2)", [0.1, 0.04]), (ld, "Wall displacement magnitude (mm), shown \u00d710", [0.58, 0.04])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 26; sb.LabelFontSize = 22
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.32; sb.AddRangeLabels = 0
    sb.UseCustomLabels = 1; sb.CustomLabels = [0, 0.4, 0.8, 1.2] if l is lp else [0, 0.04, 0.08, 0.12, 0.16]
v.CameraPosition = [-0.045, 0.012, 0.025]; v.CameraFocalPoint = [0.0, -0.0022, 0.025]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelProjection = 1; v.CameraParallelScale = 0.0118
SaveScreenshot(out, v, ImageResolution=[2400, 1000])
