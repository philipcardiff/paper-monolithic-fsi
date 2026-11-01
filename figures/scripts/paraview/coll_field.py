# pvbatch coll_field.py <case> <step> <out.png>: collapsible channel at the first
# trough: fluid pressure (kinematic) and the wall coloured by |D| on the displaced
# configuration, with the undeformed wall outline.
import sys
from paraview.simple import *
case, step, out = sys.argv[1], sys.argv[2], sys.argv[3]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/case_{step}.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/case_{step}.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
warp = WarpByVector(Input=sop); warp.Vectors = ["POINTS", "D"]
z = soi.GetDataInformation().GetBounds()
sl = Slice(Input=soi); sl.SliceType = "Plane"; sl.SliceType.Origin = [0, 0, 0.5 * (z[4] + z[5])]; sl.SliceType.Normal = [0, 0, 1]
und0 = Outline(Input=sl)
und = Transform(Input=und0); und.Transform.Translate = [0, 0, 0.06]
v = CreateView("RenderView"); v.ViewSize = [2400, 620]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(flp, v); ColorBy(d1, ("POINTS", "p"))
lp = GetColorTransferFunction("p"); lp.ApplyPreset("Viridis", True); lp.Discretize = 1; lp.NumberOfTableValues = 14
pr = flp.PointData["p"].GetRange(); lp.RescaleTransferFunction(pr[0], pr[1])
d2 = Show(warp, v); ColorBy(d2, ("POINTS", "D", "Magnitude"))
ld = GetColorTransferFunction("D"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 12
dr = warp.PointData["D"].GetRange(-1); ld.RescaleTransferFunction(0.0, dr[1])
d3 = Show(und, v); d3.AmbientColor = d3.DiffuseColor = [0, 0, 0]; d3.LineWidth = 4; d3.ColorArrayName = ["POINTS", ""]
for l, t, pos in ((lp, "Fluid kinematic pressure (m^2/s^2)", [0.12, 0.03]), (ld, "Wall displacement magnitude (m)", [0.6, 0.03])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 26; sb.LabelFontSize = 22
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0
v.CameraParallelProjection = 1
v.CameraPosition = [10.0, 0.25, 20]; v.CameraFocalPoint = [10.0, 0.25, 0]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelScale = 1.35

SaveScreenshot(out, v, ImageResolution=[2400, 620])
print("p range", pr, "Dmax", dr[1])
