# pvbatch fsi3_field.py <case> <step> <out.png>: Hron-Turek FSI3 near maximum upward
# flag deflection: fluid vorticity (z) and the flag coloured by |D| on the displaced
# configuration, with the undeformed flag outline.
import sys
from paraview.simple import *
case, step, out = sys.argv[1], sys.argv[2], sys.argv[3]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{step}.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{step}.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]
flp = CellDatatoPointData(Input=fli)
gr = Gradient(Input=flp); gr.ScalarArray = ["POINTS", "U"]; gr.ComputeVorticity = 1; gr.ResultArrayName = "gradU"
wz = Calculator(Input=gr); wz.ResultArrayName = "wz"; wz.Function = "Vorticity_Z"
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
warp = WarpByVector(Input=sop); warp.Vectors = ["POINTS", "D"]
soi.UpdatePipeline(); b = soi.GetDataInformation().GetBounds()
sl = Slice(Input=soi); sl.SliceType = "Plane"; sl.SliceType.Origin = [0, 0, 0.5 * (b[4] + b[5])]; sl.SliceType.Normal = [0, 0, 1]
und = Transform(Input=Outline(Input=sl)); und.Transform.Translate = [0, 0, 0.05]
v = CreateView("RenderView"); v.ViewSize = [2400, 860]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(wz, v); ColorBy(d1, ("POINTS", "wz"))
lw = GetColorTransferFunction("wz"); lw.ApplyPreset("PRGn", True); lw.Discretize = 1; lw.NumberOfTableValues = 20
W = 120.0; lw.RescaleTransferFunction(-W, W)
d2 = Show(warp, v); ColorBy(d2, ("POINTS", "D", "Magnitude"))
ld = GetColorTransferFunction("D"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 10
ld.RescaleTransferFunction(0.0, 0.04)
d3 = Show(und, v); d3.AmbientColor = d3.DiffuseColor = [0, 0, 0]; d3.LineWidth = 3; d3.ColorArrayName = ["POINTS", ""]
for l, t, pos, labs in ((lw, "Fluid vorticity (1/s)", [0.12, 0.02], [-120, -60, 0, 60, 120]),
                         (ld, "Flag displacement magnitude (m)", [0.6, 0.02], [0, 0.01, 0.02, 0.03, 0.04])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 26; sb.LabelFontSize = 22
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"
v.CameraParallelProjection = 1
xc, yc = 0.81, 0.122
v.CameraPosition = [xc, yc, 10]; v.CameraFocalPoint = [xc, yc, 0]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelScale = 0.29
SaveScreenshot(out, v, ImageResolution=[2400, 860])
print("fluid bounds", fli.GetDataInformation().GetBounds(), "wz range", wz.PointData["wz"].GetRange(), "Dmax", warp.PointData["D"].GetRange(-1))
