# pvbatch blob_field.py <case> <out.png>: blobInTreacle at steady state (t = 3 s),
# fluid velocity magnitude on the deformed mesh, solid coloured by |D| on the
# displaced configuration.
import sys
from paraview.simple import *
case, out = sys.argv[1], sys.argv[2]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/mesh_x2_300.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/mesh_x2_300.vtm"])
fli0 = ExtractBlock(Input=fl); fli0.Selectors = ["/Root/internal"]
fli = CellDatatoPointData(Input=fli0)
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]
sop = CellDatatoPointData(Input=soi)
warp = WarpByVector(Input=sop); warp.Vectors = ["POINTS", "D"]; warp.ScaleFactor = 1.0
sl = Slice(Input=soi); sl.SliceType = "Plane"; sl.SliceType.Origin = [0, 0, 0]; sl.SliceType.Normal = [0, 0, 1]
und0 = FeatureEdges(Input=sl); und0.FeatureEdges = 0; und0.NonManifoldEdges = 0; und0.ManifoldEdges = 0
und = Transform(Input=und0); und.Transform.Translate = [0, 0, 0.6]
v = CreateView("RenderView"); v.ViewSize = [2400, 760]; v.OrientationAxesVisibility = 0; v.Background = [1, 1, 1]
v.UseColorPaletteForBackground = 0
d1 = Show(fli, v); ColorBy(d1, ("POINTS", "U", "Magnitude"))
lut = GetColorTransferFunction("U"); lut.ApplyPreset("Viridis", True); lut.Discretize = 1; lut.NumberOfTableValues = 14
d3 = Show(und, v); d3.AmbientColor = d3.DiffuseColor = [0, 0, 0]; d3.LineWidth = 4; d3.ColorArrayName = ["POINTS", ""]
d2 = Show(warp, v); d2.Representation = "Surface"; ColorBy(d2, ("POINTS", "D", "Magnitude"))
lut2 = GetColorTransferFunction("D"); lut2.ApplyPreset("Reds", True); lut2.Discretize = 1; lut2.NumberOfTableValues = 12; lut2.InvertTransferFunction(); lut2.RescaleTransferFunction(0.0, 0.12); lut.RescaleTransferFunction(0.0, 1.68)
for l, t in ((lut, "Fluid velocity magnitude (m/s)"), (lut2, "Solid displacement magnitude (m)")):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 28; sb.LabelFontSize = 24
    sb.Orientation = "Horizontal"; sb.AddRangeLabels = 0; sb.WindowLocation = "Any Location"; sb.ScalarBarLength = 0.25
GetScalarBar(lut, v).Position = [0.15, 0.03]; GetScalarBar(lut2, v).Position = [0.6, 0.03]
for l, labs in ((lut, [0, 0.4, 0.8, 1.2, 1.6]), (lut2, [0, 0.03, 0.06, 0.09, 0.12])):
    sb = GetScalarBar(l, v); sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"; sb.RangeLabelFormat = "%-#.2g"
v.CameraParallelProjection = 1
ResetCamera(v); v.CameraPosition = [3.25, 0.0, 10]; v.CameraFocalPoint = [3.25, 0.0, 0]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelScale = 1.04
SaveScreenshot(out, v, ImageResolution=[2400, 760], TransparentBackground=0)
