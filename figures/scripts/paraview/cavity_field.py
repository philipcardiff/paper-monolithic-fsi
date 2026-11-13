# pvbatch cavity_field.py <case> <step> <out.png>: flexible-bottom cavity at steady
# state: fluid velocity magnitude with streamlines, the flexible bottom coloured by
# |D| on the displaced configuration (no magnification), undeformed outline in black.
import sys
from paraview.simple import *
case, step, out = sys.argv[1], sys.argv[2], sys.argv[3]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{step}.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{step}.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; soi.UpdatePipeline(); sop = CellDatatoPointData(Input=soi)
warp = WarpByVector(Input=sop); warp.Vectors = ["POINTS", "D"]
b = soi.GetDataInformation().GetBounds(); fb = (flp.UpdatePipeline(), fli.GetDataInformation().GetBounds())[1]
zm = 0.5 * (fb[4] + fb[5])
flsl = Slice(Input=flp); flsl.SliceType = "Plane"; flsl.SliceType.Origin = [0, 0, zm]; flsl.SliceType.Normal = [0, 0, 1]
sl = Slice(Input=soi); sl.SliceType = "Plane"; sl.SliceType.Origin = [0, 0, 0.5 * (b[4] + b[5])]; sl.SliceType.Normal = [0, 0, 1]
und = Transform(Input=Outline(Input=sl)); und.Transform.Translate = [0, 0, 2.0]
st = StreamTracer(Input=flsl, SeedType="Line"); st.Vectors = ["POINTS", "U"]
st.SeedType.Point1 = [0.5, 1.03, zm]; st.SeedType.Point2 = [0.5, 1.97, zm]; st.SeedType.Resolution = 14
st.MaximumStreamlineLength = 40.0; st.IntegrationDirection = "BOTH"
st2 = StreamTracer(Input=flsl, SeedType="Line"); st2.Vectors = ["POINTS", "U"]
st2.SeedType.Point1 = [4.3, 0.02, zm]; st2.SeedType.Point2 = [4.3, 0.62, zm]; st2.SeedType.Resolution = 7
st2.MaximumStreamlineLength = 9.0; st2.IntegrationDirection = "FORWARD"
stl = Transform(Input=AppendDatasets(Input=[st, st2])); stl.Transform.Translate = [0, 0, 1.5]
v = CreateView("RenderView"); v.ViewSize = [2400, 640]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(flsl, v); ColorBy(d1, ("POINTS", "U", "Magnitude"))
lu = GetColorTransferFunction("U"); lu.ApplyPreset("Viridis", True); lu.Discretize = 1; lu.NumberOfTableValues = 15; lu.RescaleTransferFunction(0.0, 1.5)
d4 = Show(stl, v); d4.ColorArrayName = ["POINTS", ""]; d4.AmbientColor = d4.DiffuseColor = [1, 1, 1]; d4.LineWidth = 1.4; d4.Opacity = 1.0
d2 = Show(warp, v); ColorBy(d2, ("POINTS", "D", "Magnitude"))
ld = GetColorTransferFunction("D"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 12; ld.RescaleTransferFunction(0.0, 0.24)
d3 = Show(und, v); d3.AmbientColor = d3.DiffuseColor = [0, 0, 0]; d3.LineWidth = 3; d3.ColorArrayName = ["POINTS", ""]
for l, t, pos, labs in ((lu, "Fluid velocity magnitude (m/s)", [0.12, 0.02], [0, 0.5, 1.0, 1.5]),
                         (ld, "Bottom displacement magnitude (m)", [0.6, 0.02], [0, 0.08, 0.16, 0.24])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 26; sb.LabelFontSize = 22
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"
v.CameraParallelProjection = 1
xc, yc = 7.0, 0.55
v.CameraPosition = [xc, yc, 50]; v.CameraFocalPoint = [xc, yc, zm]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelScale = 1.97
SaveScreenshot(out, v, ImageResolution=[2400, 640])
print("fluid bounds", fb, "solid bounds", b)
